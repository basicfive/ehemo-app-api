from typing import List


from app.application.transactional_service import TransactionalService
from app.infrastructure.database.unit_of_work import UnitOfWork
from app.domain.product.models.store_product import StoreType
from app.domain.product.models.store_product import StoreProduct
from app.domain.product.repositories.store_product_repository import StoreProductRepository
from app.application.product.dto.store_product_dto import StoreProductDto
from app.domain.product.schemas.store_product_schema import StoreProductInDB

class StoreProductUseCase(TransactionalService):
    def __init__(
        self,
        store_product_repo: StoreProductRepository,
        unit_of_work: UnitOfWork,
    ):
        super().__init__(unit_of_work)
        self.store_product_repo = store_product_repo

    def get_all_products_by_store_type(self, store_type: StoreType) -> List[StoreProductDto]:
        products: List[StoreProduct] = self.store_product_repo.get_all_by_store_type(store_type)
        product_indb_list = [StoreProductInDB.model_validate(product) for product in products]
        return [StoreProductDto(**product.model_dump()) for product in product_indb_list]
    

from fastapi import Depends
from app.domain.product.repositories.store_product_repository import get_store_product_repository
from app.infrastructure.database.unit_of_work import get_unit_of_work

def get_store_product_usecase(
    store_product_repo: StoreProductRepository = Depends(get_store_product_repository),
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
) -> StoreProductUseCase:
    return StoreProductUseCase(store_product_repo, unit_of_work)