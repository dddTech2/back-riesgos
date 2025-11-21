from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, validator
from app.db.models.form import QuestionType

# --- Options ---
class OptionBase(BaseModel):
    text: str
    is_correct: bool = False

class OptionCreate(OptionBase):
    pass

class OptionUpdate(OptionBase):
    id: Optional[int] = None # Allow updating existing options

class Option(OptionBase):
    id: int
    question_id: int

    class Config:
        orm_mode = True

# --- Questions ---
class QuestionBase(BaseModel):
    text: str
    question_type: QuestionType
    points: int = 0
    order_index: int = 0

class QuestionCreate(QuestionBase):
    options: List[OptionCreate] = []

class QuestionUpdate(QuestionBase):
    id: Optional[int] = None
    options: List[OptionUpdate] = []

class Question(QuestionBase):
    id: int
    form_id: int
    options: List[Option] = []

    class Config:
        orm_mode = True

# --- Forms ---
class FormBase(BaseModel):
    title: str
    description: Optional[str] = None
    access_code: Optional[str] = None
    is_active: bool = True
    is_graded: bool = False
    max_attempts: Optional[int] = None
    time_limit_minutes: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class FormCreate(FormBase):
    questions: List[QuestionCreate] = []

class FormUpdate(FormBase):
    questions: List[QuestionUpdate] = []

class Form(FormBase):
    id: int
    organization_id: int
    created_by: int
    created_at: datetime
    questions: List[Question] = []

    class Config:
        orm_mode = True

# Public Schemas (What the respondent sees)
class OptionPublic(BaseModel):
    id: int
    text: str
    
    class Config:
        orm_mode = True

class QuestionPublic(BaseModel):
    id: int
    text: str
    question_type: QuestionType
    points: int
    order_index: int
    options: List[OptionPublic] = []

    class Config:
        orm_mode = True

class FormPublic(BaseModel):
    id: int
    title: str
    description: Optional[str]
    is_graded: bool
    time_limit_minutes: Optional[int]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    questions: List[QuestionPublic] = []

    class Config:
        orm_mode = True

