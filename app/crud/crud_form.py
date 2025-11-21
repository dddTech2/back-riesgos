from typing import List, Optional, Any, Dict, Union
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.db.models.form import Form, Question, Option, FormSubmission, Answer, QuestionType
from app.schemas.form import FormCreate, FormUpdate
from app.schemas.submission import SubmissionCreate

class CRUDForm(CRUDBase[Form, FormCreate, FormUpdate]):
    def create_with_questions(self, db: Session, *, obj_in: FormCreate, created_by: int, organization_id: int) -> Form:
        obj_in_data = jsonable_encoder(obj_in)
        questions_data = obj_in_data.pop("questions", [])
        
        db_obj = Form(**obj_in_data, created_by=created_by, organization_id=organization_id)
        db.add(db_obj)
        db.flush() # Get ID

        for q_data in questions_data:
            options_data = q_data.pop("options", [])
            db_question = Question(**q_data, form_id=db_obj.id)
            db.add(db_question)
            db.flush()

            for opt_data in options_data:
                # handle id if present (though for create it shouldn't be)
                opt_data.pop("id", None) 
                db_option = Option(**opt_data, question_id=db_question.id)
                db.add(db_option)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_access_code(self, db: Session, *, access_code: str) -> Optional[Form]:
        return db.query(Form).filter(Form.access_code == access_code).first()

    def get_multi_by_organization(
        self, db: Session, *, organization_id: int, skip: int = 0, limit: int = 100
    ) -> List[Form]:
        return (
            db.query(Form)
            .filter(Form.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_with_questions(
        self, db: Session, *, db_obj: Form, obj_in: Union[FormUpdate, Dict[str, Any]]
    ) -> Form:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # Handle nested updates manually if needed, or for now just update main fields
        # Updating nested questions is complex (add/remove/update). 
        # For MVP, we might simplify or assume full replace if needed.
        # Let's stick to basic update for Form fields for now as per generic update, 
        # but we might need to handle questions separately.
        # For this implementation, let's assume we update form fields only or 
        # simple question updates if needed later.
        
        # Removing 'questions' from update_data to avoid error if passed to Form(**)
        questions_data = update_data.pop("questions", None)
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)

form = CRUDForm(Form)


from fastapi import HTTPException

class CRUDSubmission(CRUDBase[FormSubmission, SubmissionCreate, SubmissionCreate]):
    def create_submission(
        self, db: Session, *, obj_in: SubmissionCreate, form: Form
    ) -> FormSubmission:
        # Calculate Score
        score = 0.0
        total_points = 0
        
        # Map answers to dictionary for easier processing
        # We need to check correctness.
        # Retrieve full question details from DB to verify correct options
        
        # This is a simplified grading logic
        passed = None
        
        # Create Submission Record
        db_submission = FormSubmission(
            form_id=form.id,
            respondent_email=obj_in.respondent_email,
            respondent_name=obj_in.respondent_name,
            respondent_identifier=obj_in.respondent_identifier,
            start_time=datetime.utcnow(), # Or passed from frontend if tracked there
            end_time=datetime.utcnow()
        )
        db.add(db_submission)
        db.flush()

        # Process Answers
        if form.is_graded:
            for q in form.questions:
                total_points += q.points
        
        earned_points = 0.0

        for answer_in in obj_in.answers:
            # Find the question
            question = next((q for q in form.questions if q.id == answer_in.question_id), None)
            if not question:
                continue
            
            # Validate option match if selected
            if answer_in.selected_option_id:
                valid_option = next((o for o in question.options if o.id == answer_in.selected_option_id), None)
                if not valid_option:
                    # Rollback logic or raise error. Since we are in a transaction (autocommit=False usually), 
                    # raising Exception will rollback the db.add(db_submission) above if caught by FastAPI dependency
                    raise HTTPException(status_code=400, detail=f"Option {answer_in.selected_option_id} does not belong to question {answer_in.question_id}")
            
            db_answer = Answer(
                submission_id=db_submission.id,
                question_id=answer_in.question_id,
                text_value=answer_in.text_value,
                selected_option_id=answer_in.selected_option_id
            )
            db.add(db_answer)
            # Flush to ensure ID and relationship is established? 
            # Not strictly needed for adding to session but good for debugging
            
            # Grading Logic
            if form.is_graded and question.points > 0:
                if question.question_type in [QuestionType.single_choice, QuestionType.multiple_choice]:
                    # Check if selected option is correct
                    selected_opt = next((o for o in question.options if o.id == answer_in.selected_option_id), None)
                    if selected_opt and selected_opt.is_correct:
                        earned_points += question.points
        
        if form.is_graded and total_points > 0:
            # Scale to 0-100 or keep raw? Let's keep raw points or percentage?
            # Requirement says "Score", let's assume percentage 0-100 or points.
            # Let's do percentage for consistency.
            final_score = (earned_points / total_points) * 100.0
            db_submission.score = final_score
            # threshold defaults to 60? Or defined in form? 
            # Assuming 60 for now or add to Form model later.
            db_submission.passed = final_score >= 60.0 
        else:
            db_submission.score = 0.0
            db_submission.passed = None # Not graded

        db.commit()
        db.refresh(db_submission)
        return db_submission
    
    def get_by_respondent(self, db: Session, *, form_id: int, identifier: str) -> List[FormSubmission]:
        return db.query(FormSubmission).filter(
            FormSubmission.form_id == form_id, 
            FormSubmission.respondent_identifier == identifier
        ).all()

submission = CRUDSubmission(FormSubmission)

