from typing import TYPE_CHECKING, List, Optional
from pydantic import BaseModel, Field, model_validator

if TYPE_CHECKING:
    from .control import ControlInDB

class RiskBase(BaseModel):
    process_name: str
    risk_description: str
    area_id: int

class RiskCreate(RiskBase):
    # Probability questions
    prob_question_1: int = Field(..., ge=1, le=4)
    prob_question_2: int = Field(..., ge=1, le=4)
    prob_question_3: int = Field(..., ge=1, le=4)

    # Impact questions
    imp_question_1: int = Field(..., ge=1, le=4)
    imp_question_2: int = Field(..., ge=1, le=4)
    imp_question_3: int = Field(..., ge=1, le=4)

    # Optional linked controls
    control_ids: Optional[List[int]] = []
    assigned_to_id: Optional[int] = None

class RiskUpdate(BaseModel):
    process_name: Optional[str] = None
    risk_description: Optional[str] = None
    area_id: Optional[int] = None

    # Probability questions
    prob_question_1: Optional[int] = Field(None, ge=1, le=4)
    prob_question_2: Optional[int] = Field(None, ge=1, le=4)
    prob_question_3: Optional[int] = Field(None, ge=1, le=4)

    # Impact questions
    imp_question_1: Optional[int] = Field(None, ge=1, le=4)
    imp_question_2: Optional[int] = Field(None, ge=1, le=4)
    imp_question_3: Optional[int] = Field(None, ge=1, le=4)

    # Optional linked controls
    control_ids: Optional[List[int]] = None
    assigned_to_id: Optional[int] = None

    @model_validator(mode='after')
    def check_all_or_none_questions(self) -> 'RiskUpdate':
        prob_questions = [
            self.prob_question_1,
            self.prob_question_2,
            self.prob_question_3,
        ]
        imp_questions = [
            self.imp_question_1,
            self.imp_question_2,
            self.imp_question_3,
        ]

        if any(q is not None for q in prob_questions) and not all(
            q is not None for q in prob_questions
        ):
            raise ValueError(
                "All three probability questions must be provided if any one is."
            )

        if any(q is not None for q in imp_questions) and not all(
            q is not None for q in imp_questions
        ):
            raise ValueError(
                "All three impact questions must be provided if any one is."
            )

        return self


class RiskInDB(RiskBase):
    id: int
    organization_id: int
    assigned_to_id: Optional[int]
    inherent_probability: int
    inherent_impact: int
    residual_probability: Optional[int]
    residual_impact: Optional[int]
    reviewed_at: Optional[str]

    class Config:
        orm_mode = True

class Risk(RiskInDB):
    controls: List["ControlInDB"] = []

