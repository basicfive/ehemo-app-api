from app.core.config import training_settings

def calculate_training_epoch(image_count: int) -> int:
    if image_count < training_settings.MINIMUM_IMAGE_CNT_FOR_QUALITY_GUARANTEE:
        # 이미지 갯수가 70개 이하인 경우 - 퀄리티 보장을 위해 epoch을 증가
        return int(training_settings.MINIMUM_TRAINING_STEPS / image_count)
    else:
        # 이미지 갯수가 70개 이상인 경우 - 이미지 갯수 * epoch (200)
        return int(training_settings.MINIMUM_EPOCH)

def calculate_training_total_steps(image_count: int) -> int:
    epoch: int = calculate_training_epoch(image_count)
    return epoch * image_count
