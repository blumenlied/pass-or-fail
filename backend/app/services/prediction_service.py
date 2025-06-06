from sqlalchemy.orm import Session
from app.crud import users as crud_users
from app.crud import predictions as crud_predictions
from app.schema import PredictionCreate, PredictionOut
from app.models import Student
from app.ml import model as ml_model_module

from datetime import date as dt_date
import pandas as pd
from typing import List, Optional
import math

class PredictionError(Exception):
    """Custom exception for prediction failures."""
    pass

def _prepare_raw_features_for_student(student: Student) -> Optional[pd.DataFrame]:
    """
    Prepares a DataFrame with raw features from a Student object.
    The ml.model.predict_pass_fail will handle specific feature engineering.
    """
    # Check if student has at least some test data; can still proceed with NaNs
    if student.test_1_score is None and \
       student.test_2_score is None and \
       student.test_3_score is None:
        print(f"Student {student.student_id} has all test scores as None. Prediction will use defaults for these.")

    features_dict = {
        "test_1_score": student.test_1_score,
        "test_2_score": student.test_2_score,
        "test_3_score": student.test_3_score,
        "learn_guide_completed": student.learn_guide_completed,
    }
    return pd.DataFrame([features_dict])


def generate_and_save_prediction_for_student(db: Session, student_id: int) -> PredictionOut:
    # --- ADDED/MODIFIED LOGGING ---
    print("--- In generate_and_save_prediction_for_student (prediction_service.py) ---")
    print(f"Accessing ml_model_module.loaded_model. Type: {type(ml_model_module.loaded_model)}")
    if ml_model_module.loaded_model: # Access via the imported module object
        print(f"ml_model_module.loaded_model IS an object: {ml_model_module.loaded_model}")
    else:
        print(f"ml_model_module.loaded_model IS None or Falsy at the time of request.")
    # --- END LOGGING ---

    if not ml_model_module.loaded_model: # USE THE MODULE to access the global from ml.model
        print("PredictionError being raised: ML model components (via ml_model_module.loaded_model) are not loaded.")
        raise PredictionError("ML model components are not loaded. Cannot make predictions.")

    student = crud_users.get_student_by_id(db, student_id)
    if not student:
        raise PredictionError(f"Student with ID {student_id} not found.")

    df_raw_features = _prepare_raw_features_for_student(student)
    if df_raw_features is None or df_raw_features.empty:
        raise PredictionError(f"Could not prepare features for student {student_id}.")

    # Also use the module to access predict_pass_fail function
    predicted_scores_proba, categories_numeric = ml_model_module.predict_pass_fail(df_raw_features)

    score_proba = float(predicted_scores_proba[0])
    category_num = int(categories_numeric[0])
    category_label = "Pass" if category_num == 1 else "Fail"

    # Access model name via the module too
    model_name = ml_model_module.loaded_model.__class__.__name__ if hasattr(ml_model_module.loaded_model, '__class__') else "FriendModel"

    prediction_data = PredictionCreate(
        student_id=student_id,
        date=dt_date.today(),
        predicted_score=score_proba,
        category=category_label,
        model_type=model_name
    )
    created_prediction_orm = crud_predictions.create_prediction(db, prediction_data)
    return PredictionOut.model_validate(created_prediction_orm)


def generate_and_save_predictions_for_class(db: Session, program: str, section: str) -> List[PredictionOut]:
    # --- ADDED/MODIFIED LOGGING ---
    print("--- In generate_and_save_predictions_for_class (prediction_service.py) ---")
    print(f"Accessing ml_model_module.loaded_model. Type: {type(ml_model_module.loaded_model)}")
    if ml_model_module.loaded_model: # Access via the imported module object
        print(f"ml_model_module.loaded_model IS an object: {ml_model_module.loaded_model}")
    else:
        print(f"ml_model_module.loaded_model IS None or Falsy at the time of request.")
    # --- END LOGGING ---

    if not ml_model_module.loaded_model: # USE THE MODULE to access the global from ml.model
        print("PredictionError being raised from class prediction: ML model components (via ml_model_module.loaded_model) are not loaded.")
        raise PredictionError("ML model components are not loaded. Cannot make predictions.")

    students_in_class = db.query(Student)\
        .filter(Student.program == program, Student.section == section).all()

    if not students_in_class:
        return [] # No students in class, no predictions to make

    all_student_raw_feature_dfs = []
    valid_student_ids_for_prediction = []

    for student_obj in students_in_class:
        df_student_raw_features = _prepare_raw_features_for_student(student_obj)
        if df_student_raw_features is not None and not df_student_raw_features.empty:
            all_student_raw_feature_dfs.append(df_student_raw_features)
            valid_student_ids_for_prediction.append(student_obj.student_id)
        else:
            print(f"Skipping student {student_obj.student_id} in class {program}-{section} due to issues preparing features.")

    if not all_student_raw_feature_dfs:
        return [] # No students eligible for prediction

    df_features_batch = pd.concat(all_student_raw_feature_dfs, ignore_index=True)

    # Use the module to access predict_pass_fail
    predicted_scores_proba_batch, categories_numeric_batch = ml_model_module.predict_pass_fail(df_features_batch)
    # Access model name via the module too
    model_name = ml_model_module.loaded_model.__class__.__name__ if hasattr(ml_model_module.loaded_model, '__class__') else "FriendModel"

    created_predictions_list = []
    for i, student_id in enumerate(valid_student_ids_for_prediction):
        score_proba = float(predicted_scores_proba_batch[i])
        category_num = int(categories_numeric_batch[i])
        category_label = "Pass" if category_num == 1 else "Fail"

        prediction_data = PredictionCreate(
            student_id=student_id,
            date=dt_date.today(),
            predicted_score=score_proba,
            category=category_label,
            model_type=model_name
        )
        try:
            created_prediction_orm = crud_predictions.create_prediction(db, prediction_data)
            created_predictions_list.append(PredictionOut.model_validate(created_prediction_orm))
        except Exception as e:
            db.rollback() # Rollback for this specific prediction attempt
            print(f"Failed to save prediction for student {student_id}: {e}")

    return created_predictions_list
