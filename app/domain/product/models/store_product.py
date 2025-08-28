from sqlalchemy import Column, String, Integer, Float, Enum
from sqlalchemy.orm import relationship

from app.domain.time_stamp_model import TimeStampModel
from app.domain.subscription.models.enums.subscription import StoreType

class StoreProduct(TimeStampModel):
    __tablename__ = "store_product"
    store_type = Column(Enum(StoreType), nullable=False)
    product_id = Column(String(255), nullable=False, index=True)

    price = Column(Float, nullable=False)
    token_amount = Column(Integer, nullable=False)

    user_purchases = relationship("UserPurchase", back_populates="store_product")
