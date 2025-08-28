from app.domain.product.repositories.store_product_repository import StoreProductRepository
from app.domain.product.repositories.user_purchase_repository import UserPurchaseRepository
from app.domain.product.schemas.user_purchase_schema import UserPurchaseCreate
from app.domain.product.models.user_purchase import UserPurchase

class ProductPurchaseService:
    def __init__(
        self,
        store_product_repository: StoreProductRepository,
        user_purchase_repository: UserPurchaseRepository,
    ):
        self.store_product_repository = store_product_repository
        self.user_purchase_repository = user_purchase_repository

    def purchase_product(
        self,
        user_id: int,
        product_id: str,
        transaction_id: str,
    ) -> UserPurchase:
        store_product = self.store_product_repository.get_by_product_id(product_id)
        user_purchase = self.user_purchase_repository.create(
            obj_in=UserPurchaseCreate(
                user_id=user_id,
                store_product_id=store_product.id,
                price_paid=store_product.price,
                price_paid_in_purchased_currency=store_product.price,
                received_token_amount=store_product.token_amount,
                transaction_id=transaction_id,
            )
        )
        return user_purchase

from fastapi import Depends
from app.domain.product.repositories.store_product_repository import get_store_product_repository
from app.domain.product.repositories.user_purchase_repository import get_user_purchase_repository

def get_product_purchase_service(
    store_product_repository: StoreProductRepository = Depends(get_store_product_repository),
    user_purchase_repository: UserPurchaseRepository = Depends(get_user_purchase_repository),
):
    return ProductPurchaseService(
        store_product_repository=store_product_repository,
        user_purchase_repository=user_purchase_repository,
    )