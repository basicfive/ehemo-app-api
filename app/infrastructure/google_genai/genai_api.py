from google import genai
from google.genai import types
import os
from pydantic import BaseModel
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
