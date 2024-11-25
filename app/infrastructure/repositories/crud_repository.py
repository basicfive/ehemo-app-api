from typing import Generic, TypeVar, Type, List, Optional, Dict, Union, Any

from certifi import where
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db:Session):
        self.model = model
        self.db = db

    def exists(self, id: Any) -> bool:
        try:
            self.get(id)
            return True
        except NoResultFound:
            return False

    def get(self, obj_id: int) -> ModelType:
        db_obj = self.db.get(self.model, obj_id)
        if db_obj is None:
            raise ValueError(f"Object with id {obj_id} does not exist in the database")
        return db_obj

    def get_all_in(self, obj_id_list: List[int]) -> List[ModelType]:
        if not obj_id_list:
            return []

        stmt = select(self.model).where(self.model.id.in_(obj_id_list))
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def get_all(self) -> List[ModelType]:
        return self.db.query(self.model).all()

    def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(
            self,
            *,
            obj_id: int,
            obj_in: Union[UpdateSchemaType, Dict[str, any]],
    ) -> ModelType:

        db_obj = self.get(obj_id=obj_id)
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        for field in update_data:
            setattr(db_obj, field, update_data[field])

        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def remove(self, *, obj_id: int) -> ModelType:
        db_obj = self.get(obj_id=obj_id)
        self.db.delete(db_obj)
        self.db.commit()
        return db_obj
