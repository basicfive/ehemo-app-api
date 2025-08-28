from app.domain.product.models.user_purchase import UserPurchase
from app.core.db.base import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

from app.domain.product.schemas.user_purchase_schema import UserPurchaseCreate, UserPurchaseUpdate
from app.infrastructure.repositories.crud_repository import CRUDRepository

class UserPurchaseRepository(CRUDRepository[UserPurchase, UserPurchaseCreate, UserPurchaseUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=UserPurchase, db=db)

def get_user_purchase_repository(db: Session = Depends(get_db)) -> UserPurchaseRepository:
    return UserPurchaseRepository(db)