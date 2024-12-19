from datetime import datetime
from typing import Tuple, Optional

from fastapi import Depends

from app import token_transaction_consts
from app.domain.token.models.enums.token import TokenTransactionType, TokenSourceType
from app.domain.token.models.token import TokenWallet, TokenTransaction
from app.domain.token.schemas.token_transaction import TokenTransactionCreate
from app.domain.token.schemas.token_wallet import TokenWalletUpdate, TokenWalletCreate
from app.infrastructure.repositories.token.token import TokenWalletRepository, TokenTransactionRepository, \
    get_token_wallet_repository, get_token_transaction_repository

"""
token wallet / token transaction 일관성을 유지해야하기 때문에,
애플리케이션 레이어에서 repo로의 직접 접근을 허용하지 않음.
이가 코드 레벨에서 드러나도록 구분하는 법에 대한 고민이 필요함.
"""
class TokenDomainService:
   def __init__(
           self,
           token_wallet_repo: TokenWalletRepository,
           token_transaction_repo: TokenTransactionRepository,
   ):
       self.token_wallet_repo = token_wallet_repo
       self.token_transaction_repo = token_transaction_repo

   def get_wallet(self, user_id: int) -> TokenWallet:
       return self.token_wallet_repo.get_by_user(user_id)

   def create_wallet_with_flush(self, wallet_create: TokenWalletCreate) -> TokenWallet:
       return self.token_wallet_repo.create_with_flush(obj_in=wallet_create)

   def consume_token(
           self,
           token_wallet: TokenWallet,
           amount: int,
           source_type: TokenSourceType,
           description: Optional[str] = token_transaction_consts.CONSUME_MESSAGE,
   ) -> Tuple[TokenWallet, TokenTransaction]:
       if amount < 0:
           ValueError(f"amount should always be a positive number, amount: {amount}")

       current_token = token_wallet.remaining_token
       token_wallet: TokenWallet = self.token_wallet_repo.update_with_flush(
           obj_id=token_wallet.id,
           obj_in=TokenWalletUpdate(
               remaining_token=current_token - amount
           )
       )

       token_transaction: TokenTransaction = self.token_transaction_repo.create_with_flush(
           obj_in=TokenTransactionCreate(
               transaction_type=TokenTransactionType.USE,
               source_type=source_type,
               amount=-amount,
               balance_before=current_token,
               balance_after=current_token - amount,
               description=description,
               token_wallet_id=token_wallet.id,
           )
       )

       return token_wallet, token_transaction

   def refund_token(
           self,
           token_wallet: TokenWallet,
           amount: int,
           source_type: TokenSourceType,
           description: Optional[str] = token_transaction_consts.REFUND_MESSAGE,
   ) -> Tuple[TokenWallet, TokenTransaction]:
       if amount < 0:
           ValueError(f"amount should always be a positive number, amount: {amount}")

       current_token = token_wallet.remaining_token
       token_wallet: TokenWallet = self.token_wallet_repo.update_with_flush(
           obj_id=token_wallet.id,
           obj_in=TokenWalletUpdate(
               remaining_token=current_token + amount
           )
       )

       token_transaction: TokenTransaction = self.token_transaction_repo.create_with_flush(
           obj_in=TokenTransactionCreate(
               transaction_type=TokenTransactionType.REFUND,
               source_type=source_type,
               amount=amount,
               balance_before=current_token,
               balance_after=current_token + amount,
               description=description,
               token_wallet_id=token_wallet.id,
           )
       )

       return token_wallet, token_transaction

   def refill_token(
           self,
           token_wallet: TokenWallet,
           amount: int,
           next_refill_date: datetime,
           current_time: datetime,
           source_type: TokenSourceType,
           description: Optional[str] = token_transaction_consts.CONSUME_MESSAGE,
   ) -> Tuple[TokenWallet, TokenTransaction]:
       if amount < 0:
           ValueError(f"amount should always be a positive number, amount: {amount}")

       current_token = token_wallet.remaining_token
       token_wallet: TokenWallet = self.token_wallet_repo.update_with_flush(
           obj_id=token_wallet.id,
           obj_in=TokenWalletUpdate(
               remaining_token=current_token + amount,
               total_received_tokens=token_wallet.total_received_tokens + amount,
               next_refill_date=next_refill_date,
               last_refill_date=current_time,
           )
       )

       token_transaction: TokenTransaction = self.token_transaction_repo.create_with_flush(
           obj_in=TokenTransactionCreate(
               transaction_type=TokenTransactionType.REFILL,
               source_type=source_type,
               amount=amount,
               balance_before=current_token,
               balance_after=current_token + amount,
               description=description,
               token_wallet_id=token_wallet.id,
           )
       )

       return token_wallet, token_transaction


def get_token_domain_service(
       token_wallet_repo: TokenWalletRepository = Depends(get_token_wallet_repository),
       token_transaction_repo: TokenTransactionRepository = Depends(get_token_transaction_repository),
) -> TokenDomainService:
   return TokenDomainService(
       token_wallet_repo=token_wallet_repo,
       token_transaction_repo=token_transaction_repo,
   )