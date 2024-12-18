from pydantic import BaseModel


class FCMConstants(BaseModel):
    SUCCESS_TITLE: str = "AI 모델 이미지 생성이 완료되었어요"
    SUCCESS_BODY: str = "생성된 이미지를 확인해보세요"

    CATEGORY: str = "GENERATION_RESULT"
    IDENTIFIER_PREFIX: str = "request_"

    FAILURE_TITLE: str = "AI 모델 이미지 생성에 실패했어요"
    FAILURE_BODY: str = "토큰은 반환되었으니, 잠시 후에 다시 시도해주세요"

    TOKEN_REFILL_TITLE: str = "이번 달 토큰이 충전되었어요"
    TOKEN_REFILL_BODY: str = "새로운 헤어모델 이미지를 생성해보세요"

class TokenTransactionConstants(BaseModel):
    REFILL_MESSAGE: str = "월간 토큰 추가"
    CONSUME_MESSAGE: str = "이미지 생성 토큰 사용"
    REFUND_MESSAGE: str = "이미지 생성 실패 토큰 반환"


fcm_consts = FCMConstants()
token_transaction_consts = TokenTransactionConstants()
