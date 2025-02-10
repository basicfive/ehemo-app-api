import random
from typing import List

from app.domain.hair_model.models.hair import Gender, Length, SpecificColor, LoRAModel
from app.domain.hair_model.models.scene import Background, PostureAndClothing

def _concat_prompt(
        gender_prompt: str,
        length_prompt: str,
        color_prompt: str,
        posture_and_clothing_prompt: str,
        background_prompt: str,
        # lora_model_prompt: str
) -> str:
    age: int = random.randint(20, 29)
    """
    A 25-year-old Korean woman with blonde long ohwx hair,
    close-up shot, looking over shoulder, in a cozy cowl-neck sweater, hair falling in soft layers with subtle highlights,
    against white wall <lora:fx_layered_1-000200:1>
    """
    # return f"A {age}-year-old Korean {gender_prompt} with {color_prompt} {length_prompt} ohwx hair, {posture_and_clothing_prompt}, against {background_prompt} {lora_model_prompt}"
    skin_prompt = "detailed uneven rough skin, ultra detailed skin, natural facial shadows"
    length_detail = "that falls far past her chest, hair reaching down to her waist"

    if length_prompt == "long flowing":
        return f"A {age}-year-old Korean {gender_prompt} with {color_prompt} ({length_prompt}:1.2) (ohwx hair: 1.2) {length_detail}, {skin_prompt}, {posture_and_clothing_prompt}, {background_prompt}"
    if length_prompt == "":
        return f"A {age}-year-old Korean {gender_prompt} with {color_prompt} (ohwx hair: 1.2), {skin_prompt}, {posture_and_clothing_prompt}, {background_prompt}"
    return f"A {age}-year-old Korean {gender_prompt} with {color_prompt} ({length_prompt}:1.2) (ohwx hair: 1.2), {skin_prompt}, {posture_and_clothing_prompt}, {background_prompt}"

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
        prompt: str = _concat_prompt(
            gender_prompt=gender.prompt,
            length_prompt=length.prompt,
            color_prompt=specific_color_list[idx % len(specific_color_list)].prompt,
            posture_and_clothing_prompt=posture_and_clothing_list[idx].prompt,
            background_prompt=background.prompt,
            # lora_model_prompt=lora_model.prompt
        )
        prompt_list.append(prompt)
    return prompt_list

