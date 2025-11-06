from typing import TYPE_CHECKING, List, Optional
from pydantic import BaseModel, Field, model_validator

if TYPE_CHECKING:
    from .risk import RiskInDB

class ControlBase(BaseModel):
    description: str
    type: str

class ControlCreate(ControlBase):
    # Effectiveness questions
    eff_prob_question_1: float = Field(..., ge=0, le=1.5)
    eff_prob_question_2: float = Field(..., ge=0.3, le=1.5)
    eff_prob_question_3: float = Field(..., ge=0, le=1.5)
    eff_imp_question_1: float = Field(..., ge=0, le=1.5)
    eff_imp_question_2: float = Field(..., ge=0, le=1.5)
    eff_imp_question_3: float = Field(..., ge=0, le=1.5)

    risk_ids: Optional[List[int]] = []

class ControlUpdate(BaseModel):
    description: Optional[str] = None
    type: Optional[str] = None

    # Effectiveness questions
    eff_prob_question_1: Optional[float] = Field(None, ge=0, le=1.5)
    eff_prob_question_2: Optional[float] = Field(None, ge=0.3, le=1.5)
    eff_prob_question_3: Optional[float] = Field(None, ge=0, le=1.5)
    eff_imp_question_1: Optional[float] = Field(None, ge=0, le=1.5)
    eff_imp_question_2: Optional[float] = Field(None, ge=0, le=1.5)
    eff_imp_question_3: Optional[float] = Field(None, ge=0, le=1.5)

    risk_ids: Optional[List[int]] = None

    @model_validator(mode='after')
    def check_all_or_none_questions(self) -> 'ControlUpdate':
        prob_questions = [
            self.eff_prob_question_1,
            self.eff_prob_question_2,
            self.eff_prob_question_3,
        ]
        imp_questions = [
            self.eff_imp_question_1,
            self.eff_imp_question_2,
            self.eff_imp_question_3,
        ]

        if any(q is not None for q in prob_questions) and not all(
            q is not None for q in prob_questions
        ):
            raise ValueError(
                "All three effectiveness probability questions must be provided if any one is."
            )

        if any(q is not None for q in imp_questions) and not all(
            q is not None for q in imp_questions
        ):
            raise ValueError(
                "All three effectiveness impact questions must be provided if any one is."
            )

        return self

class ControlInDB(ControlBase):
    id: int
    organization_id: int
    effectiveness_probability: int
    effectiveness_impact: int
    reviewed_at: Optional[str]

    class Config:
        orm_mode = True

class Control(ControlInDB):
    risks: List["RiskInDB"] = []

