from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Type, Any, Optional, List
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDRepositoryPort(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    @abstractmethod
    async def get(self, *, obj_id: Any) -> Optional[ModelType]:
        pass

    @abstractmethod
    async def exists(self, *, obj_id: Any) -> bool:
        pass

    @abstractmethod
    async def get_all(self) -> List[ModelType]:
        pass

    @abstractmethod
    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        pass
    
    @abstractmethod
    async def create_with_flush(self, *, obj_in: CreateSchemaType) -> ModelType:
        pass
    
    @abstractmethod
    async def update(self, *, obj_id: Any, obj_in: UpdateSchemaType) -> ModelType:
        pass

    @abstractmethod
    async def update_with_flush(self, *, obj_id: Any, obj_in: UpdateSchemaType) -> ModelType:
        pass

    @abstractmethod
    async def delete(self, *, obj_id: Any) -> None:
        pass

    @abstractmethod
    async def delete_with_flush(self, *, obj_id: Any) -> None:
        pass 