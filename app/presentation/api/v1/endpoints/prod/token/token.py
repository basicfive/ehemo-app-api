from fastapi import APIRouter, Depends
from typing import List

from app.application.token.token_info import TokenInfoUseCase, get_token_info_usecase
from app.application.token.dto.token_info_dto import UserTokenResponse, TokenHistory
from app.application.user.auth import validate_user_token

router = APIRouter()

# /prod/token/

@router.get("/amount", response_model=UserTokenResponse)
def get_user_token(
        user_id: int = Depends(validate_user_token),
        usecase: TokenInfoUseCase = Depends(get_token_info_usecase)
) -> UserTokenResponse:
    return usecase.get_user_token_amount(user_id=user_id)

@router.get("/history", response_model=List[TokenHistory])
def get_user_token_history(
        user_id: int = Depends(validate_user_token),
        usecase: TokenInfoUseCase = Depends(get_token_info_usecase)
) -> List[TokenHistory]:
    return usecase.get_all_user_token_history(user_id=user_id)