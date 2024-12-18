from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db.base import get_db
from app.domain.token.models.token import TokenWallet, TokenTransaction
from app.domain.token.schemas.token_transaction import TokenTransactionCreate, TokenTransactionUpdate
from app.domain.token.schemas.token_wallet import TokenWalletUpdate, TokenWalletCreate
from app.infrastructure.repositories.crud_repository import CRUDRepository


class TokenWalletRepository(CRUDRepository[TokenWallet, TokenWalletCreate, TokenWalletUpdate]):
    def __init__(self, db: Session):
        super().__init__(db=db, model=TokenWallet)

    def get_by_user(self, user_id: int) -> TokenWallet:
        stmt = select(TokenWallet).where(TokenWallet.user_id == user_id)
        return self.db.execute(stmt).scalar_one()

def get_token_wallet_repository(db: Session = Depends(get_db)) -> TokenWalletRepository:
    return TokenWalletRepository(db=db)


class TokenTransactionRepository(CRUDRepository[TokenTransaction, TokenTransactionCreate, TokenTransactionUpdate]):
    def __init__(self, db: Session):
        super().__init__(db=db, model=TokenTransaction)

def get_token_transaction_repository(db: Session = Depends(get_db)) -> TokenTransactionRepository:
    return TokenTransactionRepository(db=db)

