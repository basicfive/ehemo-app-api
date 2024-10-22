from typing import Generic, TypeVar, Type, List

from pydantic import BaseModel

from app.core.decorators import handle_not_found
from app.infrastructure.repositories.crud_repository import ModelType, CreateSchemaType, UpdateSchemaType, CRUDRepository

ModelInDB = TypeVar("ModelInDB", bound=BaseModel)
RepositoryType = TypeVar("RepositoryType", bound=CRUDRepository)

class CRUDService(Generic[ModelType, ModelInDB, CreateSchemaType, UpdateSchemaType, RepositoryType]):
    def __init__(
            self,
            repo: CRUDRepository[ModelType, CreateSchemaType, UpdateSchemaType],
            model_in_db: Type[ModelInDB]
    ):
        self._repo = repo
        self.model_in_db = model_in_db

    @property
    def repo(self) -> RepositoryType:
        return self._repo

    def create(self, obj_in: CreateSchemaType) -> ModelInDB:
        db_obj: ModelType = self._repo.create(obj_in=obj_in)
        return self.model_in_db.model_validate(db_obj)

    @handle_not_found
    def get(self, obj_id: int) -> ModelInDB:
        db_obj: ModelType = self._repo.get(obj_id=obj_id)
        return self.model_in_db.model_validate(db_obj)

    @handle_not_found
    def update(self, obj_id: int, update_data: UpdateSchemaType) -> ModelInDB:
        db_obj: ModelType = self._repo.update(obj_id=obj_id, obj_in=update_data)
        return self.model_in_db.model_validate(db_obj)

    @handle_not_found
    def remove(self, obj_id: int) -> ModelInDB:
        db_obj: ModelType = self._repo.remove(obj_id=obj_id)
        return self.model_in_db.model_validate(db_obj)

    # TODO: 리스트에 데이터가 없는 경우 에러 처리할건가?
    def get_all(self) -> List[ModelInDB]:
        db_obj_list: List[ModelType] = self._repo.get_all()
        return [self.model_in_db.model_validate(db_obj) for db_obj in db_obj_list]

