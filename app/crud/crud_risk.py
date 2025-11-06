from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.db.models.risk import Risk
from app.db.models.control import Control
from app.schemas.risk import RiskCreate, RiskUpdate
import math

class CRUDRisk(CRUDBase[Risk, RiskCreate, RiskUpdate]):
    def create_with_organization_and_owner(
        self, db: Session, *, obj_in: RiskCreate, organization_id: int, owner_id: int
    ) -> Risk:
        # Calculate inherent probability and impact
        inherent_probability = math.ceil((obj_in.prob_question_1 + obj_in.prob_question_2 + obj_in.prob_question_3) / 3)
        inherent_impact = math.ceil((obj_in.imp_question_1 + obj_in.imp_question_2 + obj_in.imp_question_3) / 3)

        residual_probability = inherent_probability
        residual_impact = inherent_impact
        
        controls = []
        if obj_in.control_ids:
            controls = db.query(Control).filter(Control.id.in_(obj_in.control_ids)).all()
            
            sum_eff_prob = sum(c.effectiveness_probability for c in controls)
            sum_eff_imp = sum(c.effectiveness_impact for c in controls)

            residual_probability = inherent_probability - sum_eff_prob
            if residual_probability < 1:
                residual_probability = 1

            residual_impact = inherent_impact - sum_eff_imp
            if residual_impact < 1:
                residual_impact = 1

        db_obj = Risk(
            process_name=obj_in.process_name,
            risk_description=obj_in.risk_description,
            area_id=obj_in.area_id,
            inherent_probability=inherent_probability,
            inherent_impact=inherent_impact,
            residual_probability=residual_probability,
            residual_impact=residual_impact,
            organization_id=organization_id,
            owner_id=owner_id,
        )
        
        db_obj.controls.extend(controls)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Risk, obj_in: RiskUpdate
    ) -> Risk:
        update_data = obj_in.dict(exclude_unset=True)

        # Recalculate inherent probability and impact if questions are provided
        if "prob_question_1" in update_data:
            inherent_probability = math.ceil(
                (
                    update_data["prob_question_1"]
                    + update_data["prob_question_2"]
                    + update_data["prob_question_3"]
                )
                / 3
            )
            db_obj.inherent_probability = inherent_probability

        if "imp_question_1" in update_data:
            inherent_impact = math.ceil(
                (
                    update_data["imp_question_1"]
                    + update_data["imp_question_2"]
                    + update_data["imp_question_3"]
                )
                / 3
            )
            db_obj.inherent_impact = inherent_impact

        # Update other fields
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        # Recalculate residual risk
        sum_eff_prob = sum(c.effectiveness_probability for c in db_obj.controls)
        sum_eff_imp = sum(c.effectiveness_impact for c in db_obj.controls)

        db_obj.residual_probability = db_obj.inherent_probability - sum_eff_prob
        if db_obj.residual_probability < 1:
            db_obj.residual_probability = 1

        db_obj.residual_impact = db_obj.inherent_impact - sum_eff_imp
        if db_obj.residual_impact < 1:
            db_obj.residual_impact = 1

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def add_control(
        self, db: Session, *, risk_obj: Risk, control_obj: Control
    ) -> Risk:
        if control_obj not in risk_obj.controls:
            risk_obj.controls.append(control_obj)

            # Recalculate residual risk
            sum_eff_prob = sum(c.effectiveness_probability for c in risk_obj.controls)
            sum_eff_imp = sum(c.effectiveness_impact for c in risk_obj.controls)

            risk_obj.residual_probability = risk_obj.inherent_probability - sum_eff_prob
            if risk_obj.residual_probability < 1:
                risk_obj.residual_probability = 1

            risk_obj.residual_impact = risk_obj.inherent_impact - sum_eff_imp
            if risk_obj.residual_impact < 1:
                risk_obj.residual_impact = 1

            db.commit()
            db.refresh(risk_obj)
        return risk_obj

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        sort: Optional[str] = None,
        search: Optional[str] = None,
        filters: Optional[dict] = None,
    ) -> List[Risk]:
        query = db.query(self.model)

        if filters:
            for key, value in filters.items():
                query = query.filter(getattr(self.model, key) == value)

        if search:
            query = query.filter(
                self.model.process_name.ilike(f"%{search}%") |
                self.model.risk_description.ilike(f"%{search}%")
            )

        if sort:
            if sort.startswith("-"):
                query = query.order_by(getattr(self.model, sort[1:]).desc())
            else:
                query = query.order_by(getattr(self.model, sort).asc())

        return query.offset(skip).limit(limit).all()

risk = CRUDRisk(Risk)