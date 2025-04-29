from google import genai
from google.genai import types
import os
from pydantic import BaseModel
import asyncio
from functools import partial

class GoogleGenaiConfig(BaseModel):
    api_key: str = os.getenv("GEMINI_API_KEY")
    model: str = "gemini-2.0-flash"
    system_instruction: str = "너는 한국어 -> 영어 번역기야. 제공하는 문장을 영어로 번역해서 번역한 내용만 전달해."

google_genai_config = GoogleGenaiConfig()


client = genai.Client(api_key=google_genai_config.api_key)

def gemini_translate_prompt(korean_prompt: str) -> str:
    response = client.models.generate_content(
        model=google_genai_config.model,
        config=types.GenerateContentConfig(system_instruction=google_genai_config.system_instruction),
        contents=korean_prompt,
    )
    return response.text

async def async_gemini_translate_prompt(korean_prompt: str) -> str:
    """
    비동기 환경에서 Gemini API 호출을 위한 래퍼 함수
    """
    # run_in_executor를 사용하여 동기식 함수를 비동기 컨텍스트에서 실행
    loop = asyncio.get_event_loop()
    func = partial(gemini_translate_prompt, korean_prompt)
    return await loop.run_in_executor(None, func)
