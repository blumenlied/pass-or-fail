from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Prediction, Student
from app.schema import PredictionCreate
from typing import List, Optional

def create_prediction(db: Session, prediction: PredictionCreate) -> Prediction:
    db_prediction = Prediction(
        student_id=prediction.student_id,
        date=prediction.date,
        predicted_score=prediction.predicted_score,
        category=prediction.category,
        model_type=prediction.model_type
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

def get_predictions_by_student_id(db: Session, student_id: int) -> List[Prediction]:
    return db.query(Prediction)\
             .filter(Prediction.student_id == student_id)\
             .order_by(desc(Prediction.date), desc(Prediction.prediction_id))\
             .all()

def get_latest_prediction_for_student(db: Session, student_id: int) -> Optional[Prediction]:
    return db.query(Prediction)\
             .filter(Prediction.student_id == student_id)\
             .order_by(desc(Prediction.date), desc(Prediction.prediction_id))\
             .first()

def get_predictions_by_class(db: Session, program: str, section: str) -> List[Prediction]:
    """
    Gets all historical predictions for all students in a given class.
    """
    return db.query(Prediction)\
             .join(Student, Prediction.student_id == Student.student_id)\
             .filter(Student.program == program, Student.section == section)\
             .order_by(Student.student_id, desc(Prediction.date), desc(Prediction.prediction_id))\
             .all()

def get_latest_predictions_for_students_in_class(db: Session, program: str, section: str) -> List[Prediction]:
    """
    Gets only the latest prediction for each student in a given class.
    """
    students_in_class = db.query(Student.student_id)\
        .filter(Student.program == program, Student.section == section).all()

    latest_predictions_list = []
    student_ids_in_class = [s.student_id for s in students_in_class]

    if not student_ids_in_class:
        return []

    for student_id in student_ids_in_class:
        latest_pred = get_latest_prediction_for_student(db, student_id)
        if latest_pred:
            latest_predictions_list.append(latest_pred)
    return latest_predictions_list
