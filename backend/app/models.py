from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="faculty")


class Student(Base):
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    dob = Column(Date)
    program = Column(String)
    section = Column(String)
    test_1_score = Column(Float)
    test_2_score = Column(Float)
    test_3_score = Column(Float)
    avg_test_score = Column(Float)
    score_improvement_rate = Column(Float)
    test_scores_std_dev = Column(Float)
    learn_guide_completed = Column(Boolean)

    # ✅ Add reverse relationships here
    features = relationship("StudentFeatureSet", back_populates="student", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="student", cascade="all, delete-orphan")


class StudentFeatureSet(Base):
    __tablename__ = "student_feature_sets"

    feature_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    test_1_score = Column(Float, nullable=False)
    test_2_score = Column(Float, nullable=False)
    test_3_score = Column(Float, nullable=False)
    avg_test_score = Column(Float, nullable=False)
    score_improvement_rate = Column(Float, nullable=False)
    test_scores_std_dev = Column(Float, nullable=False)
    learn_guide_completed = Column(Boolean, nullable=False)

    student = relationship("Student", back_populates="features")


class Prediction(Base):
    __tablename__ = "predictions"

    prediction_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    date = Column(Date, nullable=False)
    predicted_score = Column(Float, nullable=False)  # Probability of passing
    category = Column(String, nullable=False)        # e.g., "Pass" or "Fail"
    model_type = Column(String, nullable=False)      # e.g., "LogisticRegression"

    student = relationship("Student", back_populates="predictions")

