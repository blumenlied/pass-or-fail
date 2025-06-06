import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, List, Any, Dict

# --- Configuration: Paths to your friend's exported files ---
BASE_ML_DIR = Path(__file__).parent
MODEL_FILENAME = 'course_pass_predictor_model.joblib'
SCALER_FILENAME = 'course_pass_scaler.joblib'
FEATURE_NAMES_FILENAME = 'course_pass_feature_names.joblib'

MODEL_PATH = BASE_ML_DIR / MODEL_FILENAME
SCALER_PATH = BASE_ML_DIR / SCALER_FILENAME
FEATURE_NAMES_PATH = BASE_ML_DIR / FEATURE_NAMES_FILENAME

# --- Global variables to hold loaded ML components ---
loaded_model: Any = None
loaded_scaler: Any = None
expected_feature_names: List[str] = []

def load_ml_components():
    """Loads the ML model, scaler, and feature names from disk."""
    global loaded_model, loaded_scaler, expected_feature_names
    all_loaded_successfully = True

    try:
        if MODEL_PATH.exists():
            loaded_model = joblib.load(MODEL_PATH)
            print(f"ML Model loaded successfully from {MODEL_PATH}")
        else:
            print(f"Error: Model file not found at {MODEL_PATH}")
            all_loaded_successfully = False; loaded_model = None

        if SCALER_PATH.exists():
            loaded_scaler = joblib.load(SCALER_PATH)
            print(f"Scaler loaded successfully from {SCALER_PATH}")
        else:
            print(f"Error: Scaler file not found at {SCALER_PATH}")
            all_loaded_successfully = False; loaded_scaler = None

        if FEATURE_NAMES_PATH.exists():
            expected_feature_names = joblib.load(FEATURE_NAMES_PATH)
            print(f"Feature names loaded successfully from {FEATURE_NAMES_PATH}: {expected_feature_names}")
        else:
            print(f"Error: Feature names file not found at {FEATURE_NAMES_PATH}")
            all_loaded_successfully = False; expected_feature_names = []

        if not all_loaded_successfully:
            print("One or more ML components failed to load. Prediction service will be impaired.")
            return False
        print("All ML components loaded successfully.")
        return True
    except Exception as e:
        print(f"Critical error loading ML components: {e}")
        loaded_model = None; loaded_scaler = None; expected_feature_names = []
        return False

def predict_pass_fail(data_df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """
    Makes predictions using the loaded ML model, scaler, and feature engineering logic.
    Args:
        data_df (pd.DataFrame): DataFrame with raw student data (e.g., test scores, learn_guide_completed).
    Returns:
        Tuple[np.ndarray, np.ndarray]: (predicted_probabilities_pass, predicted_categories)
    """
    if not loaded_model or not loaded_scaler or not expected_feature_names:
        print("Warning: ML components not fully loaded. Returning dummy/error predictions.")
        num_samples = len(data_df)
        return np.full(num_samples, 0.01), np.zeros(num_samples, dtype=int)

    try:
        X = data_df.copy()

        # --- 1. Feature Engineering (as per friend's Flask app logic) ---
        raw_features_needed = ['test_1_score', 'test_2_score', 'test_3_score', 'learn_guide_completed']
        for f_name in raw_features_needed:
            if f_name not in X.columns:
                X[f_name] = np.nan

        # Convert 'learn_guide_completed' (boolean from DB) to int (0 or 1)
        if 'learn_guide_completed' in X.columns:
            X['learn_guide_completed'] = X['learn_guide_completed'].fillna(0).astype(int)


        # Calculate 'score_improvement_rate' if it's an expected feature by the model
        if 'score_improvement_rate' in expected_feature_names:
            t1 = pd.to_numeric(X.get('test_1_score'), errors='coerce')
            t3 = pd.to_numeric(X.get('test_3_score'), errors='coerce')
            X['score_improvement_rate'] = (t3 - t1) / 2.0


        # Calculate 'test_scores_std_dev' if it's an expected feature
        if 'test_scores_std_dev' in expected_feature_names:
            score_cols_for_std = ['test_1_score', 'test_2_score', 'test_3_score']
            # Convert relevant columns to numeric, coercing errors to NaN
            numeric_scores_df = X[score_cols_for_std].apply(pd.to_numeric, errors='coerce')
            X['test_scores_std_dev'] = numeric_scores_df.std(axis=1, skipna=True, ddof=1) # ddof=1 for sample std dev

        # --- 2. Handle Missing Values and Prepare features in the correct order ---
        X.replace([np.inf, -np.inf], np.nan, inplace=True)

        features_for_model_dict: Dict[str, pd.Series] = {}
        for feature_name in expected_feature_names:
            if feature_name in X.columns:
                features_for_model_dict[feature_name] = X[feature_name].fillna(0) # Impute NaNs with 0
            else:
                print(f"Warning: Expected feature '{feature_name}' not in input or engineered. Adding as zeros.")
                features_for_model_dict[feature_name] = pd.Series([0] * len(X))

        student_features_for_model_df = pd.DataFrame(features_for_model_dict, columns=expected_feature_names)

        # --- 3. Scale the features ---
        student_features_scaled_np = loaded_scaler.transform(student_features_for_model_df.to_numpy())

        # --- 4. Predict ---
        probabilities = loaded_model.predict_proba(student_features_scaled_np)
        predicted_score_pass_probability = probabilities[:, 1]  # Prob for 'Pass' (class 1)
        predicted_categories_numeric = (predicted_score_pass_probability >= 0.5).astype(int) # Threshold at 0.5

        return predicted_score_pass_probability, predicted_categories_numeric

    except ValueError as ve:
        print(f"ValueError during prediction: {ve}")
        num_samples = len(data_df); return np.full(num_samples, 0.02), np.zeros(num_samples, dtype=int)
    except Exception as e:
        print(f"General error during prediction: {e}")
        num_samples = len(data_df); return np.full(num_samples, 0.03), np.zeros(num_samples, dtype=int)
