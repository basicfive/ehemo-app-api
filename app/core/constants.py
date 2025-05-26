from enum import Enum
from pydantic import BaseModel

class FCMMessageType(Enum):
    GENERATION = "GENERATION"
    TRAINING = "TRAINING"

class GenerationMessageData(BaseModel):
    type: FCMMessageType = FCMMessageType.GENERATION
    generation_request_id: int
    
    def model_dump_str(self) -> dict[str, str]:
        """FCM data 필드를 위해 모든 값을 문자열로 변환"""
        data = self.model_dump(mode='json')
        return {key: str(value) for key, value in data.items()}

class TrainingMessageData(BaseModel):
    type: FCMMessageType = FCMMessageType.TRAINING
    user_hair_style_id: int
    
    def model_dump_str(self) -> dict[str, str]:
        """FCM data 필드를 위해 모든 값을 문자열로 변환"""
        data = self.model_dump(mode='json')
        return {key: str(value) for key, value in data.items()}

class FCMConstants:
    # token
    TOKEN_REFILL_TITLE: str = "이번 달 토큰이 충전되었어요"
    TOKEN_REFILL_BODY: str = "새로운 헤어모델 이미지를 제작해보세요"

    # generation
    GENERATION_SUCCESS_TITLE: str = "요청하신 이미지가 제작되었어요"
    GENERATION_SUCCESS_BODY: str = "제작된 이미지를 확인해보세요"

    GENERATION_FAILURE_TITLE: str = "모델 이미지 제작 중에 문제가 생겼어요"
    GENERATION_FAILURE_BODY: str = "토큰은 반환되었으니, 잠시 후에 다시 시도해주세요"

    # training
    USER_HAIRSTYLE_REGISTER_COMPLETED_TITLE: str = "새로운 헤어스타일 등록이 완료되었어요"
    USER_HAIRSTYLE_REGISTER_COMPLETED_BODY: str = "등록된 스타일로 헤어모델 이미지를 제작해보세요"

    USER_HAIRSTYLE_TRAINING_FAILURE_TITLE: str = "새로운 헤어스타일이 등록되지 않았어요"
    USER_HAIRSTYLE_TRAINING_FAILURE_BODY: str = "문제를 조치 중이니, 잠시 뒤에 다시 시도해주세요"

class TokenTransactionConstants:
    REFILL_MESSAGE: str = "월간 토큰 추가"
    CONSUME_MESSAGE: str = "이미지 제작 토큰 사용"
    REFUND_MESSAGE: str = "이미지 제작 실패 토큰 반환"

class StoreUrls:
    IOS: str = "https://apps.apple.com/kr/app/%EC%97%90%ED%97%A4%EB%AA%A8-%EC%82%AC%EC%A7%84-%ED%80%84%EB%A6%AC%ED%8B%B0-ai-%ED%97%A4%EC%96%B4%EB%AA%A8%EB%8D%B8/id6739270884?l=en-GB"
    ANDROID: str = "https://play.google.com/store/apps/details?id=com.basicfive.ehemo_app_client"
    WEB: str = "https://play.google.com/store/apps/details?id=com.basicfive.ehemo_app_client"