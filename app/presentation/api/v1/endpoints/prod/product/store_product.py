from fastapi import APIRouter, Depends
from typing import List

from app.domain.product.models.store_product import StoreType
from app.application.product.store_product_usecase import get_store_product_usecase
from app.application.product.store_product_usecase import StoreProductUseCase
from app.application.product.dto.store_product_dto import StoreProductDto
from app.application.user.auth import validate_user_token

router = APIRouter()

@router.get("/store-product/{store_type}", response_model=List[StoreProductDto])
def get_store_product(
    store_type: StoreType,
    _: int = Depends(validate_user_token),
    usecase: StoreProductUseCase = Depends(get_store_product_usecase),
) -> List[StoreProductDto]:
    return usecase.get_all_products_by_store_type(store_type)