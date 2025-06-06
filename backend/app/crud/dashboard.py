from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.models import Student, Prediction
from app.schema import (
    ProgramStudentCount, SectionStudentCount, ProgramAverageScore,
    ScoreDistributionBucket, LearnGuideStatusByProgram, DashboardStudentSummary
)
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
import math

# --- Helper for rounding ---
def safe_round(value: Optional[float], digits: int = 2) -> Optional[float]:
    if value is None or math.isnan(value) or math.isinf(value):
        return None
    return round(value, digits)

# --- Individual Metric Functions ---

def get_total_students(db: Session) -> int:
    return db.query(func.count(Student.student_id)).scalar() or 0

def get_total_unique_programs(db: Session) -> int:
    return db.query(func.count(func.distinct(Student.program))).filter(Student.program.isnot(None)).scalar() or 0

def get_total_unique_sections(db: Session) -> int:
    return db.query(func.count(func.distinct(Student.section))).filter(Student.section.isnot(None)).scalar() or 0

def get_overall_average_score(db: Session) -> Optional[float]:
    avg = db.query(func.avg(Student.avg_test_score)).filter(Student.avg_test_score.isnot(None)).scalar()
    return safe_round(avg)

def get_learn_guide_completion_rate(db: Session) -> Optional[float]:
    total_students = get_total_students(db)
    if total_students == 0:
        return 0.0 

    completed_count = db.query(func.count(Student.student_id))\
        .filter(Student.learn_guide_completed == True).scalar() or 0

    rate = (completed_count / total_students) * 100 if total_students > 0 else 0.0
    return safe_round(rate)

def get_students_at_risk_count(db: Session, threshold: float = 60.0) -> int:
    return db.query(func.count(Student.student_id))\
        .filter(Student.avg_test_score.isnot(None), Student.avg_test_score < threshold).scalar() or 0

def get_students_per_program(db: Session) -> List[ProgramStudentCount]:
    results = db.query(
        Student.program,
        func.count(Student.student_id).label("count")
    ).filter(Student.program.isnot(None)).group_by(Student.program).order_by(Student.program).all()
    return [ProgramStudentCount(program=row.program, count=row.count) for row in results]

def get_students_per_section(db: Session) -> List[SectionStudentCount]:
    results = db.query(
        Student.section,
        func.count(Student.student_id).label("count")
    ).filter(Student.section.isnot(None)).group_by(Student.section).order_by(Student.section).all()
    return [SectionStudentCount(section=row.section, count=row.count) for row in results]

def get_average_score_per_program(db: Session) -> List[ProgramAverageScore]:
    results = db.query(
        Student.program,
        func.avg(Student.avg_test_score).label("average_score")
    ).filter(Student.program.isnot(None), Student.avg_test_score.isnot(None))\
     .group_by(Student.program).order_by(Student.program).all()
    return [
        ProgramAverageScore(program=row.program, average_score=safe_round(row.average_score))
        for row in results
    ]

def get_overall_score_distribution(db: Session) -> List[ScoreDistributionBucket]:
    # Define score ranges/buckets
    buckets = [
        {"label": "90-100", "min": 90, "max": 100},
        {"label": "80-89", "min": 80, "max": 89.99},
        {"label": "70-79", "min": 70, "max": 79.99},
        {"label": "60-69", "min": 60, "max": 69.99},
        {"label": "0-59", "min": 0, "max": 59.99},
    ]
    distribution = []
    for bucket in buckets:
        count = db.query(func.count(Student.student_id)).filter(
            Student.avg_test_score.isnot(None),
            Student.avg_test_score >= bucket["min"],
            Student.avg_test_score <= bucket["max"]
        ).scalar() or 0
        distribution.append(ScoreDistributionBucket(range=bucket["label"], count=count))
    return distribution

def get_learn_guide_status_per_program(db: Session) -> List[LearnGuideStatusByProgram]:
    results = db.query(
        Student.program,
        func.sum(case((Student.learn_guide_completed == True, 1), else_=0)).label("completed"),
        func.sum(case((Student.learn_guide_completed == False, 1), else_=0)).label("not_completed")
    ).filter(Student.program.isnot(None)).group_by(Student.program).order_by(Student.program).all()

    return [
        LearnGuideStatusByProgram(
            program=row.program,
            completed=row.completed or 0,
            not_completed=row.not_completed or 0
        ) for row in results
    ]

def get_recent_students(db: Session, limit: int = 5) -> List[DashboardStudentSummary]:
    results = db.query(Student).order_by(Student.student_id.desc()).limit(limit).all()
    return [
        DashboardStudentSummary(
            student_id=s.student_id,
            first_name=s.first_name,
            last_name=s.last_name,
            program=s.program,
            section=s.section,
            avg_test_score=safe_round(s.avg_test_score)
        ) for s in results
    ]

def get_low_performing_students(db: Session, threshold: float = 60.0, limit: int = 5) -> List[DashboardStudentSummary]:
    results = db.query(Student)\
        .filter(Student.avg_test_score.isnot(None), Student.avg_test_score < threshold)\
        .order_by(Student.avg_test_score.asc())\
        .limit(limit).all()
    return [
        DashboardStudentSummary(
            student_id=s.student_id,
            first_name=s.first_name,
            last_name=s.last_name,
            program=s.program,
            section=s.section,
            avg_test_score=safe_round(s.avg_test_score)
        ) for s in results
    ]
