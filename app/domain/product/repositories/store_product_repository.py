from fastapi import Depends
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import select

from app.core.db.base import get_db
from app.domain.subscription.models.enums.subscription import StoreType
from app.domain.product.models.store_product import StoreProduct
from app.domain.product.schemas.store_product_schema import StoreProductCreate, StoreProductUpdate
from app.infrastructure.repositories.crud_repository import CRUDRepository

class StoreProductRepository(CRUDRepository[StoreProduct, StoreProductCreate, StoreProductUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=StoreProduct, db=db)
    
    def get_all_by_store_type(self, store_type: StoreType) -> List[StoreProduct]:
        stmt = select(StoreProduct).filter(StoreProduct.store_type == store_type)
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_product_id(self, product_id: str) -> StoreProduct:
        stmt = select(StoreProduct).filter(StoreProduct.product_id == product_id)
        result = self.db.execute(stmt)
        return result.scalars().one()

def get_store_product_repository(db: Session = Depends(get_db)) -> StoreProductRepository:
    return StoreProductRepository(db)