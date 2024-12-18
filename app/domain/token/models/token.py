from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship

from app.domain.time_stamp_model import TimeStampModel
from app.domain.token.models.enums.token import TokenTransactionType, TokenSourceType


class TokenWallet(TimeStampModel):
    __tablename__ = "token_wallet"

    remaining_token = Column(Integer, default=0, nullable=False)
    total_received_tokens = Column(Integer, default=0, nullable=False)

    next_refill_date = Column(DateTime(timezone=True), nullable=False)
    last_refill_date = Column(DateTime(timezone=True), nullable=False)

    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    user_subscription_id = Column(Integer, ForeignKey("user_subscription.id"), index=True)

    user = relationship("User", back_populates="token_wallet")
    user_subscription = relationship("UserSubscription", back_populates="token_wallet")

    token_transactions = relationship("TokenTransaction", back_populates="token_wallet")

    # Indexes
    __table_args__ = (
        Index('idx_token_refill', 'next_refill_date', 'user_subscription_id'),
    )

    def has_available_token(self, required_token: int) -> bool:
        return self.remaining_token >= required_token

class TokenTransaction(TimeStampModel):
    __tablename__ = "token_transaction"

    transaction_type = Column(Enum(TokenTransactionType), nullable=False)
    source_type = Column(Enum(TokenSourceType), nullable=False)
    amount = Column(Integer, nullable=False)

    balance_before = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)

    description = Column(String)

    token_wallet_id = Column(Integer, ForeignKey("token_wallet.id"), index=True)
    token_wallet = relationship("TokenWallet", back_populates="token_transactions")
