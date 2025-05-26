from app.core.config import token_settings

def calculate_token_cost(is_high_res: bool, is_user_hair_model: bool) -> int:
    token: int = token_settings.BASE_TOKENS_PER_GENERATION
    if is_high_res:
        token *= 2
    if is_user_hair_model:
        token *= 2
    return token