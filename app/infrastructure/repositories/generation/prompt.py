from fastapi import Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func
from typing import List

from app.domain.common.enums.gender import Gender
from app.infrastructure.repositories.crud_repository import CRUDRepository
from app.core.db.base import get_db
from app.domain.generation.models.prompt import PromptComponentQuestion, PromptComponentSuggestion, LengthPromptEnhancement, ClothingPromptExample, PosePromptExample
from app.domain.generation.schemas.prompt.prompt_component_question import PromptComponentQuestionCreate, PromptComponentQuestionUpdate
from app.domain.generation.schemas.prompt.prompt_component_suggestion import PromptComponentSuggestionCreate, PromptComponentSuggestionUpdate
from app.domain.generation.schemas.prompt.length_prompt_enhancement import LengthPromptEnhancementCreate, LengthPromptEnhancementUpdate
from app.domain.generation.schemas.prompt.clothing_prompt_example import ClothingPromptExampleCreate, ClothingPromptExampleUpdate
from app.domain.generation.schemas.prompt.pose_prompt_example import PosePromptExampleCreate, PosePromptExampleUpdate
from app.domain.generation.enums.prompt_component import PromptComponentType

class PromptComponentQuestionRepository(CRUDRepository[PromptComponentQuestion, PromptComponentQuestionCreate, PromptComponentQuestionUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=PromptComponentQuestion, db=db)
    
    def get_all_by_component_type(self, component_type: PromptComponentType) -> List[PromptComponentQuestion]:
        stmt = select(PromptComponentQuestion).filter(PromptComponentQuestion.component_type == component_type)
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_ids(self, ids: List[int]) -> List[PromptComponentQuestion]:
        stmt = select(PromptComponentQuestion).filter(PromptComponentQuestion.id.in_(ids))
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_all_with_suggestions(self) -> List[PromptComponentQuestion]:
        stmt = select(PromptComponentQuestion).options(joinedload(PromptComponentQuestion.suggestions))
        result = self.db.execute(stmt)
        return list(result.unique().scalars().all())

def get_prompt_component_question_repository(db: Session = Depends(get_db)) -> PromptComponentQuestionRepository:
    return PromptComponentQuestionRepository(db=db)

class PromptComponentSuggestionRepository(CRUDRepository[PromptComponentSuggestion, PromptComponentSuggestionCreate, PromptComponentSuggestionUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=PromptComponentSuggestion, db=db)
    
    def get_all_by_question_ids(self, question_ids: List[int]) -> List[PromptComponentSuggestion]:
        stmt = select(PromptComponentSuggestion).where(PromptComponentSuggestion.question_id.in_(question_ids))
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_all_with_question(self) -> List[PromptComponentSuggestion]:
        stmt = select(PromptComponentSuggestion).options(joinedload(PromptComponentSuggestion.question))
        result = self.db.execute(stmt)
        return list(result.scalars().all())

def get_prompt_component_suggestion_repository(db: Session = Depends(get_db)) -> PromptComponentSuggestionRepository:
    return PromptComponentSuggestionRepository(db=db)


class LengthPromptEnhancementRepository(CRUDRepository[LengthPromptEnhancement, LengthPromptEnhancementCreate, LengthPromptEnhancementUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=LengthPromptEnhancement, db=db)

    def get_all_by_gender(self, gender: Gender) -> List[LengthPromptEnhancement]:
        stmt = select(LengthPromptEnhancement).filter(LengthPromptEnhancement.gender == gender)
        result = self.db.execute(stmt)
        return list(result.scalars().all())

def get_length_prompt_enhancement_repository(db: Session = Depends(get_db)) -> LengthPromptEnhancementRepository:
    return LengthPromptEnhancementRepository(db=db)

class ClothingPromptExampleRepository(CRUDRepository[ClothingPromptExample, ClothingPromptExampleCreate, ClothingPromptExampleUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=ClothingPromptExample, db=db)

    def get_random_by_gender(self, gender: Gender) -> ClothingPromptExample:
        stmt = select(ClothingPromptExample).filter(ClothingPromptExample.gender == gender).order_by(func.random()).limit(1)
        result = self.db.execute(stmt)
        return result.scalars().first()

def get_clothing_prompt_example_repository(db: Session = Depends(get_db)) -> ClothingPromptExampleRepository:
    return ClothingPromptExampleRepository(db=db)

class PosePromptExampleRepository(CRUDRepository[PosePromptExample, PosePromptExampleCreate, PosePromptExampleUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=PosePromptExample, db=db)
    
    def get_random(self) -> PosePromptExample:
        stmt = select(PosePromptExample).order_by(func.random()).limit(1)
        result = self.db.execute(stmt)
        return result.scalars().first()

def get_pose_prompt_example_repository(db: Session = Depends(get_db)) -> PosePromptExampleRepository:
    return PosePromptExampleRepository(db=db)