from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

# --- Answers ---
class AnswerBase(BaseModel):
    question_id: int
    text_value: Optional[str] = None
    selected_option_id: Optional[int] = None

class AnswerCreate(AnswerBase):
    pass

class Answer(AnswerBase):
    id: int
    submission_id: int

    class Config:
        orm_mode = True

# --- Submissions ---
class SubmissionBase(BaseModel):
    form_id: int
    respondent_email: EmailStr
    respondent_name: str
    respondent_identifier: str

class SubmissionCreate(SubmissionBase):
    access_code: Optional[str] = None # Used for validation, not stored directly on submission
    answers: List[AnswerCreate]

class Submission(SubmissionBase):
    id: int
    start_time: datetime
    end_time: Optional[datetime]
    score: float
    passed: Optional[bool]
    answers: List[Answer] = []

    class Config:
        orm_mode = True

class AccessRequest(BaseModel):
    access_code: Optional[str] = None
    respondent_email: EmailStr
    respondent_identifier: str
    
class FormStats(BaseModel):
    total_submissions: int
    average_score: float
    submissions: List[Submission]

    class Config:
        orm_mode = True
