from typing import List

from app.domain.token.models.token import TokenTransaction, TokenWallet
from app.infrastructure.repositories.user.user import UserRepository
from app.infrastructure.repositories.token.token import TokenTransactionRepository
from app.application.token.dto.token_info_dto import TokenHistory, UserTokenResponse

class TokenInfoUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        token_transaction_repo: TokenTransactionRepository,
    ):
        self.user_repo = user_repo
        self.token_transaction_repo = token_transaction_repo

    def get_user_token_amount(self, user_id: int) -> UserTokenResponse:
        user = self.user_repo.get_with_token_wallets(user_id)
        token_wallet: TokenWallet = user.current_token_wallet
        return UserTokenResponse(token=token_wallet.remaining_token)
    
    def get_all_user_token_history(self, user_id: int) -> List[TokenHistory]:
        user = self.user_repo.get_with_token_wallets(user_id)
        token_wallet: TokenWallet = user.current_token_wallet
        token_transactions: List[TokenTransaction] = self.token_transaction_repo.get_all_by_wallet(token_wallet.id)
        return [
            TokenHistory(
                amount=transaction.amount,
                balance_after=transaction.balance_after,
                description=transaction.description,
                transaction_date=transaction.created_at,
            ) for transaction in token_transactions
        ]

from fastapi import Depends
from app.infrastructure.repositories.user.user import get_user_repository
from app.infrastructure.repositories.token.token import get_token_transaction_repository

def get_token_info_usecase(
    user_repo: UserRepository = Depends(get_user_repository),
    token_transaction_repo: TokenTransactionRepository = Depends(get_token_transaction_repository),
) -> TokenInfoUseCase:
    return TokenInfoUseCase(
        user_repo=user_repo,
        token_transaction_repo=token_transaction_repo,
    )