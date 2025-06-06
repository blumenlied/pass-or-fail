from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional, List, Dict # Added List, Dict

# --- Student Schemas ---
class StudentBase(BaseModel):
    first_name: str
    last_name: str
    dob: date
    program: str
    section: str
    test_1_score: Optional[float] = None
    test_2_score: Optional[float] = None
    test_3_score: Optional[float] = None
    avg_test_score: Optional[float] = None
    score_improvement_rate: Optional[float] = None
    test_scores_std_dev: Optional[float] = None
    learn_guide_completed: bool

    model_config = ConfigDict(from_attributes=True, extra='ignore')

class StudentCreate(StudentBase):
    pass

class StudentOut(StudentBase):
    student_id: int

# --- Prediction Schemas ---
class PredictionBase(BaseModel):
    student_id: int
    date: date
    predicted_score: float  # Probability of passing
    category: str           # "Pass" or "Fail"
    model_type: str

    model_config = ConfigDict(protected_namespaces=())

class PredictionCreate(PredictionBase):
    pass

class PredictionOut(PredictionBase):
    prediction_id: int
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    role: str = "faculty"

class UserOut(UserBase):
    id: int
    role: str
    model_config = ConfigDict(from_attributes=True)

# --- Token Schema for Login ---
class Token(BaseModel):
    access_token: str
    token_type: str

# --- DASHBOARD SCHEMAS - START ---
class ProgramStudentCount(BaseModel):
    program: str
    count: int

class SectionStudentCount(BaseModel):
    section: str
    count: int

class ProgramAverageScore(BaseModel):
    program: str
    average_score: Optional[float]

class ScoreDistributionBucket(BaseModel):
    range: str
    count: int

class LearnGuideStatusByProgram(BaseModel):
    program: str
    completed: int
    not_completed: int

class DashboardStudentSummary(BaseModel):
    student_id: int
    first_name: str
    last_name: str
    program: Optional[str] = None
    section: Optional[str] = None
    avg_test_score: Optional[float] = None
    model_config = ConfigDict(from_attributes=True) # Added for ORM mode

class DashboardStatsData(BaseModel):
    total_students: int
    total_programs: int
    total_sections: int
    overall_average_score: Optional[float]
    learn_guide_completion_rate: Optional[float] # Percentage
    students_at_risk_count: int
    students_per_program: List[ProgramStudentCount]
    students_per_section: List[SectionStudentCount]
    average_score_per_program: List[ProgramAverageScore]
    overall_score_distribution: List[ScoreDistributionBucket]
    learn_guide_status_per_program: List[LearnGuideStatusByProgram]
    recent_students: List[DashboardStudentSummary]
    low_performing_students: List[DashboardStudentSummary]

class DashboardStatsResponse(BaseModel):
    message: str 
    data: DashboardStatsData
# --- DASHBOARD SCHEMAS - END ---
