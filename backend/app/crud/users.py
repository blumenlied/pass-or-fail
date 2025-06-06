from sqlalchemy.orm import Session
from app.models import User, Student, StudentFeatureSet
from app.auth.utils import get_password_hash # Assuming you have this
from datetime import date
import math
from typing import Optional, Tuple


def _calculate_student_metrics(
    test_1_score: Optional[float],
    test_2_score: Optional[float],
    test_3_score: Optional[float]
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Calculates average score, improvement rate (between test 1 and 3), and std dev.
    These are general metrics stored in the DB, separate from specific model feature engineering.
    """
    scores = [s for s in [test_1_score, test_2_score, test_3_score] if s is not None and not math.isnan(s)]

    avg_score_val = None
    improvement_rate_val = None
    std_dev_val = None

    if len(scores) > 0:
        avg_score_val = sum(scores) / len(scores)
        avg_score_val = round(avg_score_val, 2)

    if len(scores) >= 2: # Need at least two scores for variance/std_dev
        if avg_score_val is not None:
            variance = sum([(s - avg_score_val) ** 2 for s in scores]) / len(scores)
            std_dev_val = round(math.sqrt(variance), 2)

    t1 = test_1_score if test_1_score is not None and not math.isnan(test_1_score) else None
    t3 = test_3_score if test_3_score is not None and not math.isnan(test_3_score) else None

    if t1 is not None and t3 is not None:
        if t1 != 0:
            improvement_rate_val = ((t3 - t1) / abs(t1)) * 100
            improvement_rate_val = round(improvement_rate_val, 2)
        elif t1 == 0 and t3 > 0:
            improvement_rate_val = float('inf') # Represents a very large improvement
        elif t1 == 0 and t3 < 0:
            improvement_rate_val = float('-inf')
        elif t1 == 0 and t3 == 0:
            improvement_rate_val = 0.0

    return avg_score_val, improvement_rate_val, std_dev_val


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, password: str, role: str = "faculty") -> User:
    hashed_password = get_password_hash(password)
    db_user = User(email=email, hashed_password=hashed_password, role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_student_by_id(db: Session, student_id: int) -> Optional[Student]:
    return db.query(Student).filter(Student.student_id == student_id).first()

def get_all_students(db: Session) -> list[Student]:
    return db.query(Student).order_by(Student.last_name, Student.first_name).all()

def create_student_with_features(
    db: Session,
    first_name: str,
    last_name: str,
    dob: date,
    program: str,
    section: str,
    test_1_score: Optional[float],
    test_2_score: Optional[float],
    test_3_score: Optional[float],
    learn_guide_completed: bool
) -> Student:
    avg_score, improvement_rate, std_dev = _calculate_student_metrics(
        test_1_score, test_2_score, test_3_score
    )

    new_student = Student(
        first_name=first_name,
        last_name=last_name,
        dob=dob,
        program=program,
        section=section,
        test_1_score=test_1_score,
        test_2_score=test_2_score,
        test_3_score=test_3_score,
        avg_test_score=avg_score,
        score_improvement_rate=improvement_rate,
        test_scores_std_dev=std_dev,
        learn_guide_completed=learn_guide_completed
    )
    try:
        db.add(new_student)
        db.flush()  # To get new_student.student_id

        # Create a corresponding feature set entry
        feature_set = StudentFeatureSet(
            student_id=new_student.student_id,
            test_1_score=test_1_score,
            test_2_score=test_2_score,
            test_3_score=test_3_score,
            avg_test_score=avg_score,
            score_improvement_rate=improvement_rate,
            test_scores_std_dev=std_dev,
            learn_guide_completed=learn_guide_completed
        )
        db.add(feature_set)
        db.commit()
        db.refresh(new_student)
    except Exception as e:
        db.rollback()
        print(f"Error creating student and features: {e}")
        raise
    return new_student


def update_student_with_features(
    db: Session,
    student_id: int,
    first_name: str,
    last_name: str,
    dob: date,
    program: str,
    section: str,
    test_1_score: Optional[float],
    test_2_score: Optional[float],
    test_3_score: Optional[float],
    learn_guide_completed: bool
) -> Optional[Student]:
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        return None

    avg_score, improvement_rate, std_dev = _calculate_student_metrics(
        test_1_score, test_2_score, test_3_score
    )

    student.first_name = first_name
    student.last_name = last_name
    student.dob = dob
    student.program = program
    student.section = section
    student.test_1_score = test_1_score
    student.test_2_score = test_2_score
    student.test_3_score = test_3_score
    student.avg_test_score = avg_score
    student.score_improvement_rate = improvement_rate
    student.test_scores_std_dev = std_dev
    student.learn_guide_completed = learn_guide_completed

    # Update the related feature set
    feature_set = db.query(StudentFeatureSet).filter(StudentFeatureSet.student_id == student_id).first()
    if feature_set:
        feature_set.test_1_score = test_1_score
        feature_set.test_2_score = test_2_score
        feature_set.test_3_score = test_3_score
        feature_set.avg_test_score = avg_score
        feature_set.score_improvement_rate = improvement_rate
        feature_set.test_scores_std_dev = std_dev
        feature_set.learn_guide_completed = learn_guide_completed
    else:
        print(f"Warning: No StudentFeatureSet found for student_id {student_id} during update. Creating one.")
        feature_set = StudentFeatureSet(
            student_id=student.student_id,
            test_1_score=test_1_score, test_2_score=test_2_score, test_3_score=test_3_score,
            avg_test_score=avg_score, score_improvement_rate=improvement_rate,
            test_scores_std_dev=std_dev, learn_guide_completed=learn_guide_completed
        )
        db.add(feature_set)
    try:
        db.commit()
        db.refresh(student)
        if feature_set:
             db.refresh(feature_set)
    except Exception as e:
        db.rollback()
        print(f"Error updating student and features: {e}")
        raise
    return student

def delete_student_and_features(db: Session, student_id: int) -> Optional[int]:
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        return None
    try:
        # Cascade delete should handle StudentFeatureSet and Prediction due to model relationships
        deleted_id = student.student_id
        db.delete(student)
        db.commit()
        return deleted_id
    except Exception as e:
        db.rollback()
        print(f"Error deleting student and associated data: {e}")
        raise
