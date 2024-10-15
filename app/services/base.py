from abc import abstractmethod
from typing import Generic, TypeVar, Type, List, Dict, Any, Callable

from pydantic import BaseModel

from app.core.decorators import handle_not_found
from app.core.errors.exceptions import ParentKeyNotFoundException
from app.repositories.base import ModelType, CreateSchemaType, UpdateSchemaType, BaseRepository

ModelInDB = TypeVar("ModelInDB", bound=BaseModel)
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)

class BaseService(Generic[ModelType, ModelInDB, CreateSchemaType, UpdateSchemaType, RepositoryType]):
    def __init__(
            self,
            repo: BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType],
            model_in_db: Type[ModelInDB]
    ):
        self._repo = repo
        self.model_in_db = model_in_db

    @property
    def repo(self) -> RepositoryType:
        return self._repo

    # def create(self, obj_in: CreateSchemaType) -> ModelInDB:
    #     db_obj: ModelType = self._repo.create(obj_in=obj_in)
    #     return self.model_in_db.model_validate(db_obj)

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

class CRUDService(BaseService[ModelType, ModelInDB, CreateSchemaType, UpdateSchemaType, RepositoryType]):
    def __init__(self, repo: RepositoryType, model_in_db: Type[ModelInDB]):
        super().__init__(repo=repo, model_in_db=model_in_db)


class RelationValidatedCRUDService(BaseService[ModelType, ModelInDB, CreateSchemaType, UpdateSchemaType, RepositoryType]):
    def __init__(
            self,
            repo: RepositoryType,
            model_in_db: Type[ModelInDB],
            relation_validators: Dict[str, Callable[[Any], bool]]
    ):
        super().__init__(repo=repo, model_in_db=model_in_db)
        self.relation_validators = relation_validators

    def validate_relation(self, obj_in: CreateSchemaType):
        for field, validator in self.relation_validators.items():
            # 필드가 존재하지 않으면 에러를 발생
            if not hasattr(obj_in, field):
                raise ValueError(f"Field '{field}' does not exist in the input schema")

            # 필드 값을 가져옴
            value = getattr(obj_in, field)

            # Optional 필드의 경우 None이면 검증하지 않고 넘어감
            if value is not None and not validator(value):
                raise ParentKeyNotFoundException(f"Validation failed for field '{field}' with value {value}")

    def create(self, obj_in: CreateSchemaType) -> ModelInDB:
        self.validate_relation(obj_in)
        db_obj: ModelType = self.repo.create(obj_in=obj_in)
        return self.model_in_db.model_validate(db_obj)

