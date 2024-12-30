class FCMConstants:
    SUCCESS_TITLE: str = "AI 모델 이미지 생성이 완료되었어요"
    SUCCESS_BODY: str = "생성된 이미지를 확인해보세요"

    CATEGORY: str = "GENERATION_RESULT"
    IDENTIFIER_PREFIX: str = "request_"

    FAILURE_TITLE: str = "AI 모델 이미지 생성에 실패했어요"
    FAILURE_BODY: str = "토큰은 반환되었으니, 잠시 후에 다시 시도해주세요"

    TOKEN_REFILL_TITLE: str = "이번 달 토큰이 충전되었어요"
    TOKEN_REFILL_BODY: str = "새로운 헤어모델 이미지를 생성해보세요"

class TokenTransactionConstants:
    REFILL_MESSAGE: str = "월간 토큰 추가"
    CONSUME_MESSAGE: str = "이미지 생성 토큰 사용"
    REFUND_MESSAGE: str = "이미지 생성 실패 토큰 반환"

class StoreUrls:
    IOS: str = "https://apps.apple.com/kr/app/%EC%97%90%ED%97%A4%EB%AA%A8-%EC%82%AC%EC%A7%84-%ED%80%84%EB%A6%AC%ED%8B%B0-ai-%ED%97%A4%EC%96%B4%EB%AA%A8%EB%8D%B8/id6739270884?l=en-GB"
    ANDROID: str = "https://play.google.com/store/apps/details?id=com.basicfive.ehemo_app_client"
    WEB: str = "https://play.google.com/store/apps/details?id=com.basicfive.ehemo_app_client"