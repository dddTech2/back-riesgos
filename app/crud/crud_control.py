from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.crud.base import CRUDBase
from app.db.models.control import Control
from app.db.models.risk import Risk
from app.schemas.control import ControlCreate, ControlUpdate
import math

class CRUDControl(CRUDBase[Control, ControlCreate, ControlUpdate]):
    def create_with_organization_and_risks(
        self, db: Session, *, obj_in: ControlCreate, organization_id: int
    ) -> Control:
        # Calculate effectiveness
        eff_prob = math.ceil((obj_in.eff_prob_question_1 + obj_in.eff_prob_question_2 + obj_in.eff_prob_question_3) / 3)
        eff_imp = math.ceil((obj_in.eff_imp_question_1 + obj_in.eff_imp_question_2 + obj_in.eff_imp_question_3) / 3)

        db_obj = Control(
            description=obj_in.description,
            type=obj_in.type,
            effectiveness_probability=eff_prob,
            effectiveness_impact=eff_imp,
            organization_id=organization_id,
        )
        
        if obj_in.risk_ids:
            risks = db.query(Risk).filter(Risk.id.in_(obj_in.risk_ids)).all()
            
            for risk in risks:
                risk.controls.append(db_obj)
                sum_eff_prob = sum(c.effectiveness_probability for c in risk.controls)
                sum_eff_imp = sum(c.effectiveness_impact for c in risk.controls)
                
                risk.residual_probability = risk.inherent_probability - sum_eff_prob
                if risk.residual_probability < 1:
                    risk.residual_probability = 1

                risk.residual_impact = risk.inherent_impact - sum_eff_imp
                if risk.residual_impact < 1:
                    risk.residual_impact = 1
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Control, obj_in: ControlUpdate
    ) -> Control:
        update_data = obj_in.dict(exclude_unset=True)

        # Recalculate effectiveness if questions are provided
        if "eff_prob_question_1" in update_data:
            eff_prob = math.ceil(
                (
                    update_data["eff_prob_question_1"]
                    + update_data["eff_prob_question_2"]
                    + update_data["eff_prob_question_3"]
                )
                / 3
            )
            db_obj.effectiveness_probability = eff_prob

        if "eff_imp_question_1" in update_data:
            eff_imp = math.ceil(
                (
                    update_data["eff_imp_question_1"]
                    + update_data["eff_imp_question_2"]
                    + update_data["eff_imp_question_3"]
                )
                / 3
            )
            db_obj.effectiveness_impact = eff_imp

        # Update other fields
        if "description" in update_data:
            db_obj.description = update_data["description"]
        if "type" in update_data:
            db_obj.type = update_data["type"]

        # Update associated risks
        if "risk_ids" in update_data:
            risks = db.query(Risk).filter(Risk.id.in_(update_data["risk_ids"])).all()
            db_obj.risks = risks

        # Recalculate residual risk for all associated risks
        for risk in db_obj.risks:
            sum_eff_prob = sum(c.effectiveness_probability for c in risk.controls)
            sum_eff_imp = sum(c.effectiveness_impact for c in risk.controls)

            risk.residual_probability = risk.inherent_probability - sum_eff_prob
            if risk.residual_probability < 1:
                risk.residual_probability = 1

            risk.residual_impact = risk.inherent_impact - sum_eff_imp
            if risk.residual_impact < 1:
                risk.residual_impact = 1

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def add_risk(self, db: Session, *, control_obj: Control, risk_obj: Risk) -> Control:
        if risk_obj not in control_obj.risks:
            control_obj.risks.append(risk_obj)
            db.commit()
            db.refresh(control_obj)
        return control_obj

    def get(self, db: Session, id: int) -> Optional[Control]:
        return db.query(self.model).options(joinedload(self.model.risks)).filter(self.model.id == id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        sort: Optional[str] = None,
        search: Optional[str] = None,
        filters: Optional[dict] = None,
    ) -> List[Control]:
        query = db.query(self.model).options(joinedload(self.model.risks))

        if filters:
            for key, value in filters.items():
                query = query.filter(getattr(self.model, key) == value)

        if search:
            query = query.filter(self.model.description.ilike(f"%{search}%"))

        if sort:
            if sort.startswith("-"):
                query = query.order_by(getattr(self.model, sort[1:]).desc())
            else:
                query = query.order_by(getattr(self.model, sort).asc())

        return query.offset(skip).limit(limit).all()

control = CRUDControl(Control)