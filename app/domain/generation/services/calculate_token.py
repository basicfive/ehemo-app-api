def calculate_required_token(is_high_res: bool, is_user_hair_model: bool) -> int:
    token: int = 1
    if is_high_res:
        token *= 2
    if is_user_hair_model:
        token *= 2
    return token