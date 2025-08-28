from sqlalchemy import Column, String, Integer, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.domain.time_stamp_model import TimeStampModel

class UserPurchase(TimeStampModel):
    __tablename__ = "user_purchase"

    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    user = relationship("User")

    store_product_id = Column(Integer, ForeignKey("store_product.id"), index=True)
    store_product = relationship("StoreProduct")

    price_paid = Column(Float, nullable=False)
    price_paid_in_purchased_currency = Column(Float, nullable=False)

    received_token_amount = Column(Integer, nullable=False)

    transaction_id = Column(String, nullable=False)
   