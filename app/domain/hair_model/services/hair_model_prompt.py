import random
from typing import List

from app.domain.hair_model.models.hair import Gender, Length, SpecificColor, LoRAModel
from app.domain.hair_model.models.scene import Background, PostureAndClothing

def _build_prompt(
        gender_prompt: str,
        length_prompt: str,
        color_prompt: str,
        posture_and_clothing_prompt: str,
        background_prompt: str,
        # lora_model_prompt: str
) -> str:
    """
    A 25-year-old Korean woman with
    (brown: 1.2)
    (long flowing:1.6) (ohwx hair:1.3) that falls far past her chest,
    close-up shot, looking over shoulder,
    in a cozy cowl-neck sweater,
    against white wall
    """
    age: int = random.randint(20, 29)
    skin_prompt = "detailed uneven rough skin, ultra detailed skin, natural facial shadows"

    return f"A {age}-year-old Korean {gender_prompt} with ({color_prompt}:1.2) {length_prompt}, {skin_prompt}, {posture_and_clothing_prompt}, {background_prompt}"

def create_prompts(
        length: Length,
        gender: Gender,
        background: Background,
        # lora_model: LoRAModel,
        specific_color_list: List[SpecificColor],
        posture_and_clothing_list: List[PostureAndClothing],
        *,
        count: int
):

    prompt_list = []

    for idx, _ in enumerate(range(count)):
        prompt: str = _build_prompt(
            gender_prompt=gender.prompt,
            length_prompt=length.prompt,
            color_prompt=specific_color_list[idx % len(specific_color_list)].prompt,
            posture_and_clothing_prompt=posture_and_clothing_list[idx].prompt,
            background_prompt=background.prompt,
            # lora_model_prompt=lora_model.prompt
        )
        prompt_list.append(prompt)
    return prompt_list

