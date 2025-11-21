from sqlalchemy import Boolean, Column, Integer, String, Text, ForeignKey, DateTime, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base_class import Base

class QuestionType(str, enum.Enum):
    text = "text"
    single_choice = "single_choice"
    multiple_choice = "multiple_choice"
    rating = "rating"

class Form(Base):
    __tablename__ = "forms"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    access_code = Column(String, unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True)
    is_graded = Column(Boolean, default=False)
    max_attempts = Column(Integer, nullable=True)
    time_limit_minutes = Column(Integer, nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    organization = relationship("Organization", backref="forms")
    creator = relationship("User", backref="created_forms")
    questions = relationship("Question", back_populates="form", cascade="all, delete-orphan")
    submissions = relationship("FormSubmission", back_populates="form", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("forms.id"), nullable=False)
    text = Column(String, nullable=False)
    question_type = Column(Enum(QuestionType), nullable=False)
    points = Column(Integer, default=0)
    order_index = Column(Integer, default=0)

    # Relationships
    form = relationship("Form", back_populates="questions")
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")
    answers = relationship("Answer", back_populates="question")

class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    text = Column(String, nullable=False)
    is_correct = Column(Boolean, default=False)

    # Relationships
    question = relationship("Question", back_populates="options")

class FormSubmission(Base):
    __tablename__ = "form_submissions"

    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("forms.id"), nullable=False)
    respondent_email = Column(String, nullable=False)
    respondent_name = Column(String, nullable=False)
    respondent_identifier = Column(String, nullable=False, index=True) # DNI/Cedula
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    score = Column(Float, default=0.0)
    passed = Column(Boolean, nullable=True)

    # Relationships
    form = relationship("Form", back_populates="submissions")
    answers = relationship("Answer", back_populates="submission", cascade="all, delete-orphan")

class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("form_submissions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    text_value = Column(Text, nullable=True)
    selected_option_id = Column(Integer, ForeignKey("options.id"), nullable=True)

    # Relationships
    submission = relationship("FormSubmission", back_populates="answers")
    question = relationship("Question", back_populates="answers")
    selected_option = relationship("Option")

