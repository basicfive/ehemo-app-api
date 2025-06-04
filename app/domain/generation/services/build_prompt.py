from typing import List
from pydantic import BaseModel

from app.domain.generation.enums.prompt_component import PromptComponentType
from app.domain.common.enums.gender import Gender
from app.domain.generation.schemas.prompt.prompt_component_question import PromptComponentQuestionInDB
from app.domain.generation.dto.request_generation import PromptComponentAnswer
from app.domain.generation.models.prompt import PromptComponentQuestion, LengthPromptEnhancement
from app.infrastructure.repositories.generation.prompt import PromptComponentQuestionRepository, LengthPromptEnhancementRepository
from app.infrastructure.repositories.generation.prompt import ClothingPromptExampleRepository, PosePromptExampleRepository

def replace_hair_with_ohwx_hair(
        english_prompt: str,
) -> str:
    """
    hair -> ohwx hair
    """
    return english_prompt.replace("hair", "ohwx hair")

class PromptCompentQuestionAnswer(BaseModel):
    question: PromptComponentQuestionInDB
    answer_info: PromptComponentAnswer

class BuildPromptService:
    def __init__(
            self,
            prompt_component_question_repo: PromptComponentQuestionRepository,
            length_prompt_enhancement_repo: LengthPromptEnhancementRepository,
            clothing_prompt_example_repo: ClothingPromptExampleRepository,
            pose_prompt_example_repo: PosePromptExampleRepository,
    ):
        self.prompt_component_question_repo = prompt_component_question_repo
        self.length_prompt_enhancement_repo = length_prompt_enhancement_repo
        self.clothing_prompt_example_repo = clothing_prompt_example_repo
        self.pose_prompt_example_repo = pose_prompt_example_repo

    def build_korean_prompt(
            self,
            gender: Gender,
            prompt_component_answers: List[PromptComponentAnswer],
    ) -> str:
        """
        응답한 질문 순서에 맞춰서 프롬프트를 정렬, 이어붙임.
        기장의 경우 일치하는 keyword 가 있는 경우 enhance_prompt 를 추가함.
        """
        # 1. 응답 순서 정렬
        prompt_question_answer_list_sorted = self._sort_prompt_component_question_answer(prompt_component_answers)

        # 2. 프롬프트 연결 (랜덤 선택된 값 -> example 중에서 랜덤 프롬프트를 가져온다.)
        korean_prompt = self._concat_prompt(gender, prompt_question_answer_list_sorted)

        # 3. 기장의 경우 성별에 맞춰서 기장 프롬프트 개선 (긴머리 -> 어깨 아래로 흘러내리는 긴머리)
        # (이렇게 하지 않으면 flux 에서 충분히 긴 머리가 나오지 않음)
        length_prompt_enhancements: List[LengthPromptEnhancement] = self.length_prompt_enhancement_repo.get_all_by_gender(gender)

        for length_prompt_enhancement in length_prompt_enhancements:
            if length_prompt_enhancement.keyword in korean_prompt:
                korean_prompt = korean_prompt.replace(length_prompt_enhancement.keyword, length_prompt_enhancement.enhance_prompt)
                break

        return korean_prompt

    def _sort_prompt_component_question_answer(
            self,
            prompt_component_answers: List[PromptComponentAnswer],
    ) -> List[PromptCompentQuestionAnswer]:
         # 1. 응답 순서 정렬
        prompt_component_question_ids: List[int] = [answer.prompt_component_question_id for answer in prompt_component_answers]
        prompt_component_questions: List[PromptComponentQuestion] = self.prompt_component_question_repo.get_by_ids(prompt_component_question_ids)
        prompt_component_questions_in_db: List[PromptComponentQuestionInDB] = [
            PromptComponentQuestionInDB.model_validate(question)
            for question in prompt_component_questions
        ]

        prompt_question_map = {q.id: q for q in prompt_component_questions_in_db}
        prompt_question_answer_list: List[PromptCompentQuestionAnswer] = []

        for answer in prompt_component_answers:
            prompt_question = prompt_question_map[answer.prompt_component_question_id]
            prompt_question_answer_list.append(
                PromptCompentQuestionAnswer(
                    question=prompt_question,
                    answer_info=answer
                )
            )

        return sorted(prompt_question_answer_list, key=lambda x: x.question.order)

    def _concat_prompt(
            self,
            gender: Gender,
            prompt_question_answer_list_sorted: List[PromptCompentQuestionAnswer],
    ) -> str:
        # 2. 프롬프트 생성
        gender_prompt = "남성" if gender == Gender.MALE else "여성"
        korean_prompt = f"25세 한국 {gender_prompt} 의 사진, "

        for question_answer in prompt_question_answer_list_sorted:
            if question_answer.answer_info.is_not_selected:
                # 사용자가 선택하지 않은 경우 프롬프트에 추가하지 않음.
                continue
            
            to_concat_prompt = question_answer.answer_info.answer

            if question_answer.answer_info.is_random:
                # 사용자가 랜덤을 선택한 경우 example 중에서 랜덤 프롬프트를 가져온다.
                if question_answer.question.component_type == PromptComponentType.CLOTHING:
                    # 의상 랜덤이라면
                    clothing_prompt_example = self.clothing_prompt_example_repo.get_random_by_gender(gender)
                    to_concat_prompt = clothing_prompt_example.prompt
                elif question_answer.question.component_type == PromptComponentType.POSE:
                    # 자세 랜덤이라면
                    pose_prompt_example = self.pose_prompt_example_repo.get_random()
                    to_concat_prompt = pose_prompt_example.prompt

                # 이외의 경우 랜덤 답변을 허용하지 않음.
                # raise ValueError(f"랜덤 답변을 허용하지 않는 질문입니다. 질문: {question_answer.question.question}")

                # FIXED -> 에러를 굳이 발생시킬 필요가 없음. 
                # (프론트에서 과거 요청 불러오기 해서 "랜덤" 파싱해서, 본래 is_random 값을 True 표시하지 않는 component type 도 True가 되기에 에러가 발생할 수 있음.

            if question_answer.question.component_type == PromptComponentType.HAIR_COLOR:
                # 색상에는 머리색이라는 명시
                to_concat_prompt += " 머리색"
            elif question_answer.question.component_type == PromptComponentType.BACKGROUND:
                to_concat_prompt += " 배경"
            elif question_answer.question.component_type == PromptComponentType.CLOTHING:
                to_concat_prompt += " 을 입고 있음"
            
            korean_prompt += f"{to_concat_prompt}, "

        # 마지막에 있는 ", "만 제거
        if korean_prompt.endswith(", "):
            return korean_prompt[:-2]
        else:
            return korean_prompt


from fastapi import Depends
from app.infrastructure.repositories.generation.prompt import get_prompt_component_question_repository
from app.infrastructure.repositories.generation.prompt import get_length_prompt_enhancement_repository
from app.infrastructure.repositories.generation.prompt import get_clothing_prompt_example_repository
from app.infrastructure.repositories.generation.prompt import get_pose_prompt_example_repository

def get_build_prompt_service(
        prompt_component_question_repo: PromptComponentQuestionRepository = Depends(get_prompt_component_question_repository),
        length_prompt_enhancement_repo: LengthPromptEnhancementRepository = Depends(get_length_prompt_enhancement_repository),
        clothing_prompt_example_repo: ClothingPromptExampleRepository = Depends(get_clothing_prompt_example_repository),
        pose_prompt_example_repo: PosePromptExampleRepository = Depends(get_pose_prompt_example_repository),
) -> BuildPromptService:
    return BuildPromptService(
        prompt_component_question_repo,
        length_prompt_enhancement_repo,
        clothing_prompt_example_repo,
        pose_prompt_example_repo,
    )
