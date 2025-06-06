from fastapi import FastAPI, Depends, HTTPException, status, Form, Path
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.auth.auth import create_access_token, get_current_user, get_db
from app.crud.users import get_user_by_email, get_all_students, create_student_with_features, update_student_with_features, delete_student_and_features, get_student_by_id
from app.crud import dashboard as crud_dashboard
from app.models import User
from app.schema import StudentOut, PredictionOut, DashboardStatsData, DashboardStatsResponse
from app.auth.utils import verify_password
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
from typing import List, Optional

# <<< START NEW IMPORTS >>>
from app.crud import predictions as crud_predictions
from app.services import prediction_service
from app.services.prediction_service import PredictionError # Import custom exception
from app.ml.model import load_ml_components as load_ml_model # Renamed to avoid conflict
# <<< END NEW IMPORTS >>>


app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# <<< START NEW CODE: STARTUP EVENT >>>
@app.on_event("startup")
async def startup_event():
    print("Application startup: Loading ML model...")
    load_ml_model()
# <<< END NEW CODE: STARTUP EVENT >>>


# Token response model
class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/login", response_model=Token, tags=["Authentication"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/students", response_model=List[StudentOut], tags=["Students"])
def read_students(
    db: Session = Depends(get_db),
):
    return get_all_students(db)


@app.post("/students", response_model=StudentOut, status_code=status.HTTP_201_CREATED, tags=["Students"])
def create_student_endpoint(
    first_name: str = Form(...),
    last_name: str = Form(...),
    dob: str = Form(...),
    program: str = Form(...),
    section: str = Form(...),
    test_1_score: Optional[float] = Form(None),
    test_2_score: Optional[float] = Form(None),
    test_3_score: Optional[float] = Form(None),
    learn_guide_completed: bool = Form(...),
    db: Session = Depends(get_db),
):
    try:
        try:
            dob_as_date_obj = date.fromisoformat(dob)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid date format for 'dob'. Expected YYYY-MM-DD, received '{dob}'."
            )

        new_student_orm = create_student_with_features(
            db=db,
            first_name=first_name,
            last_name=last_name,
            dob=dob_as_date_obj,
            program=program,
            section=section,
            test_1_score=test_1_score,
            test_2_score=test_2_score,
            test_3_score=test_3_score,
            learn_guide_completed=learn_guide_completed
        )
        return StudentOut.model_validate(new_student_orm)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        print(f"SQLAlchemyError creating student: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error: Could not save student.")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error creating student: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")

# test
@app.get("/dashboard", tags=["General"])
def read_dashboard(current_user: User = Depends(get_current_user)):
     return {
         "message": f"Welcome {current_user.email}",
         "data": {
             "total_students": 42
         }
     }

@app.get("/dashboard-stats", response_model=DashboardStatsResponse, tags=["Dashboard"])
async def get_dashboard_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Protect this endpoint
):
    try:
        total_students = crud_dashboard.get_total_students(db)
        total_programs = crud_dashboard.get_total_unique_programs(db)
        total_sections = crud_dashboard.get_total_unique_sections(db)
        overall_avg_score = crud_dashboard.get_overall_average_score(db)
        learn_guide_rate = crud_dashboard.get_learn_guide_completion_rate(db)
        at_risk_count = crud_dashboard.get_students_at_risk_count(db) # Default threshold 60
        students_per_program = crud_dashboard.get_students_per_program(db)
        students_per_section = crud_dashboard.get_students_per_section(db)
        avg_score_per_program = crud_dashboard.get_average_score_per_program(db)
        score_distribution = crud_dashboard.get_overall_score_distribution(db)
        learn_guide_by_program = crud_dashboard.get_learn_guide_status_per_program(db)
        recent_students_list = crud_dashboard.get_recent_students(db) # Default limit 5
        low_performers_list = crud_dashboard.get_low_performing_students(db) # Default threshold 60, limit 5

        dashboard_data = DashboardStatsData(
            total_students=total_students,
            total_programs=total_programs,
            total_sections=total_sections,
            overall_average_score=overall_avg_score,
            learn_guide_completion_rate=learn_guide_rate,
            students_at_risk_count=at_risk_count,
            students_per_program=students_per_program,
            students_per_section=students_per_section,
            average_score_per_program=avg_score_per_program,
            overall_score_distribution=score_distribution,
            learn_guide_status_per_program=learn_guide_by_program,
            recent_students=recent_students_list,
            low_performing_students=low_performers_list,
        )

        return DashboardStatsResponse(
            message=f"Dashboard statistics for {current_user.email}", # Or just "Dashboard Data"
            data=dashboard_data
        )
    except SQLAlchemyError as e:
        print(f"SQLAlchemyError fetching dashboard stats: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error fetching dashboard statistics.")
    except Exception as e:
        print(f"Unexpected error fetching dashboard stats: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while fetching dashboard statistics.")

@app.put("/students/{student_id}", response_model=StudentOut, tags=["Students"])
def update_student_endpoint(
    student_id: int = Path(..., title="The ID of the student to update", ge=1),
    first_name: str = Form(...),
    last_name: str = Form(...),
    dob: str = Form(...),
    program: str = Form(...),
    section: str = Form(...),
    test_1_score: Optional[float] = Form(None),
    test_2_score: Optional[float] = Form(None),
    test_3_score: Optional[float] = Form(None),
    learn_guide_completed: bool = Form(...),
    db: Session = Depends(get_db),
):
    try:
        try:
            dob_as_date_obj = date.fromisoformat(dob)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid date format for 'dob'. Expected YYYY-MM-DD, received '{dob}'."
            )

        updated_student_orm = update_student_with_features(
            db=db,
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            dob=dob_as_date_obj,
            program=program,
            section=section,
            test_1_score=test_1_score,
            test_2_score=test_2_score,
            test_3_score=test_3_score,
            learn_guide_completed=learn_guide_completed,
        )
        if not updated_student_orm:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

        return StudentOut.model_validate(updated_student_orm)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        print(f"SQLAlchemyError updating student: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error: Could not update student.")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error updating student: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")

@app.delete("/students/{student_id}", status_code=status.HTTP_200_OK, tags=["Students"])
def delete_student_endpoint(
    student_id: int = Path(..., title="The ID of the student to delete", ge=1),
    db: Session = Depends(get_db),
):
    try:
        deleted_student_id = delete_student_and_features(db=db, student_id=student_id)

        if deleted_student_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

        return {"message": "Student deleted successfully", "student_id": deleted_student_id}
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        print(f"SQLAlchemyError deleting student: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error: Could not delete student.")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error deleting student: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")


# <<< START NEW PREDICTION ENDPOINTS >>>
@app.post("/students/{student_id}/predict", response_model=PredictionOut, tags=["Predictions"])
async def trigger_prediction_for_student(
    student_id: int = Path(..., title="The ID of the student", ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Protected endpoint
):
    try:
        prediction = prediction_service.generate_and_save_prediction_for_student(db, student_id)
        return prediction
    except PredictionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except SQLAlchemyError as e:
        db.rollback()
        print(f"SQLAlchemyError during student prediction: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error during prediction.")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error during student prediction: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during prediction.")

@app.get("/students/{student_id}/predictions", response_model=List[PredictionOut], tags=["Predictions"])
async def get_student_prediction_history(
    student_id: int = Path(..., title="The ID of the student", ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Protected endpoint
):
    student = get_student_by_id(db, student_id) # from app.crud.users
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    predictions = crud_predictions.get_predictions_by_student_id(db, student_id)
    return predictions


@app.post("/predictions/class/{program}/{section}", response_model=List[PredictionOut], tags=["Predictions"])
async def trigger_predictions_for_class(
    program: str = Path(..., title="Program name"),
    section: str = Path(..., title="Section name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Protected endpoint
):
    try:
        predictions = prediction_service.generate_and_save_predictions_for_class(db, program, section)
        if not predictions:
            pass
        return predictions
    except PredictionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except SQLAlchemyError as e:
        db.rollback()
        print(f"SQLAlchemyError during class prediction: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error during class prediction.")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error during class prediction: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during class prediction.")


@app.get("/predictions/class/{program}/{section}/latest", response_model=List[PredictionOut], tags=["Predictions"])
async def get_latest_predictions_for_class(
    program: str = Path(..., title="Program name"),
    section: str = Path(..., title="Section name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Protected endpoint
):
    predictions = crud_predictions.get_latest_predictions_for_students_in_class(db, program, section)
    return predictions

@app.get("/predictions/class/{program}/{section}/history", response_model=List[PredictionOut], tags=["Predictions"])
async def get_historical_predictions_for_class(
    program: str = Path(..., title="Program name"),
    section: str = Path(..., title="Section name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Protected endpoint
):
    # This retrieves all historical predictions for students in that class.
    predictions = crud_predictions.get_predictions_by_class(db, program, section)
    return predictions

# <<< END NEW PREDICTION ENDPOINTS >>>
