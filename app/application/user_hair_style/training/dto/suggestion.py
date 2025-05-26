from pydantic import BaseModel
from typing import List

class NamingSuggestions(BaseModel):
    title_suggestions: List[str]
    description_suggestions: List[str]
    length_prompt_suggestions: List[str]