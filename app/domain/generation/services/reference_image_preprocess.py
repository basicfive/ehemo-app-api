import io
import logging
from math import sqrt, floor
from typing import Optional

from PIL import Image, ImageOps


class ReferenceImagePreprocessService:
    """
    참조 이미지 전처리: 면적(픽셀 수) 기준으로 1024x1024의 120%를 초과할 때만
    종횡비를 유지하여 축소한 JPEG 바이트를 반환한다. 그 외에는 None 반환.
    """

    def __init__(self, max_side_pixels: int = 1024, buffer_ratio: float = 1.2):
        self.max_side_pixels = max_side_pixels
        self.buffer_ratio = buffer_ratio

    def maybe_downscale(self, image_bytes: bytes) -> Optional[bytes]:
        try:
            with Image.open(io.BytesIO(image_bytes)) as im:
                im = ImageOps.exif_transpose(im)

                if im.mode not in ("RGB", "L"):
                    im = im.convert("RGB")

                width, height = im.size
                total_pixels = width * height
                max_total_pixels = self.max_side_pixels * self.max_side_pixels

                # 20% 버퍼 이내면 축소하지 않음
                if total_pixels <= int(max_total_pixels * self.buffer_ratio):
                    return None

                scale = sqrt(max_total_pixels / float(total_pixels))
                new_w = max(1, floor(width * scale))
                new_h = max(1, floor(height * scale))

                resized = im.resize((new_w, new_h), Image.Resampling.LANCZOS)

                out = io.BytesIO()
                resized.save(out, format="JPEG", quality=90, optimize=True, progressive=True)
                out.seek(0)
                return out.read()
        except Exception as e:
            logging.exception("Failed to preprocess reference image: %s", e)
            return None


def get_reference_image_preprocess_service() -> ReferenceImagePreprocessService:
    return ReferenceImagePreprocessService()


