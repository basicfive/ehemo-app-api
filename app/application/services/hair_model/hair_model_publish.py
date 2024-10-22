# import json
#
# from app.application.query.hair_model_query import HairModelQueryService
# from app.core.utils import remove_duplicates_set, model_list_to_dict
# from app.infrastructure.repositories.hair_model.hair_model import *
#
# class HairModelPublishApplicationService:
#     def __init__(
#             self,
#             gender_repo: GenderRepository,
#             hair_style_repo: HairStyleRepository,
#             length_repo: LengthRepository,
#             hair_style_length_repo: HairStyleLengthRepository,
#             hair_design_repo: HairDesignRepository,
#             hair_design_color_repo: HairDesignColorRepository,
#             hair_variant_model_repo: HairVariantModelRepository
#     ):
#         self.gender_repo = gender_repo
#         self.hair_style_repo = hair_style_repo
#         self.length_repo = length_repo
#         self.hair_style_length_repo = hair_style_length_repo
#         self.hair_design_repo = hair_design_repo
#         self.hair_design_color_repo = hair_design_color_repo
#         self.hair_variant_model_repo = hair_variant_model_repo
#
#     # 코드 고쳐야함.
#     def publish(self):
#
#         # 1. HVM
#         hair_variant_model_list: List[HairVariantModel] = self.hair_variant_model_repo.get_all_unpublished()
#         hair_variant_model_ids: List[int] = [hair_variant_model.id for hair_variant_model in hair_variant_model_list]
#         self.hair_variant_model_repo.update_is_published(hair_variant_model_ids, is_published=True)
#         print(json.dumps(model_list_to_dict(hair_variant_model_list), indent=2))
#
#         # 2. HairDesignColor
#         hair_design_color_ids: List[int] = remove_duplicates_set(
#             [hair_variant_model.hair_design_color_id for hair_variant_model in hair_variant_model_list]
#         )
#         hair_design_color_list: List[HairDesignColor] = self.hair_design_color_repo.get_all_in(hair_design_color_ids)
#         self.hair_design_color_repo.update_is_published(hair_design_color_ids, is_published=True)
#         print(json.dumps(model_list_to_dict(hair_design_color_list), indent=2))
#
#         # 3. HairDesign
#         hair_design_ids: List[int] = remove_duplicates_set(
#             [hair_design_color.hair_design_id for hair_design_color in hair_design_color_list]
#         )
#         hair_design_list: List[HairDesign] = self.hair_design_repo.get_all_in(hair_design_ids)
#
#         hair_style_length_set: List[Tuple[int, int]] = []
#         hair_style_ids: List[int] = []
#
#         for hair_design in hair_design_list:
#             if not hair_design.length_id:
#                 hair_style_ids.append(hair_design.hair_style_id)
#                 continue
#             hair_style_length_set.append((hair_design.hair_style_id, hair_design.length_id))
#
#         # print(json.dumps(model_list_to_dict(hair_design_list), indent=2))
#         # 3. HairStyleLength
#         hair_style_length_list = self.hair_style_length_repo.get_all_by_hair_style_and_length_set(hair_style_length_set)
#
#         hair_style_length_ids: List[int] = [hair_style_length.id for hair_style_length in hair_style_length_list]
#         self.hair_style_length_repo.update_is_published(hair_style_length_ids, is_published=True)
#         print(json.dumps(model_list_to_dict(hair_style_length_list), indent=2))
#
#         # 4. HairStyle
#         hair_style_ids += [hair_style_length.hair_style_id for hair_style_length in hair_style_length_list]
#         hair_style_ids = remove_duplicates_set(hair_style_ids)
#         hair_style_list: List[HairStyle] = self.hair_style_repo.get_all_in(hair_style_ids)
#         self.hair_style_repo.update_is_published(hair_style_ids, is_published=True)
#         print(json.dumps(model_list_to_dict(hair_style_list), indent=2))
#
#         # 5. Gender
#         gender_ids: List[int] = remove_duplicates_set(
#             [hair_style.gender_id for hair_style in hair_style_list]
#         )
#         self.gender_repo.update_is_published(gender_ids, is_published=True)
#
#
# def get_hair_model_publish_service(
#         gender_repo: GenderRepository = Depends(get_gender_repository),
#         hair_style_repo: HairStyleRepository = Depends(get_hair_style_repository),
#         length_repo: LengthRepository = Depends(get_length_repository),
#         hair_style_length_repo: HairStyleLengthRepository = Depends(get_hair_style_length_repository),
#         hair_design_repo: HairDesignRepository = Depends(get_hair_design_repository),
#         hair_design_color_repo: HairDesignColorRepository = Depends(get_hair_design_color_repository),
#         hair_variant_model_repo: HairVariantModelRepository = Depends(get_hair_variant_model_repository)
# ) -> HairModelPublishApplicationService:
#     return HairModelPublishApplicationService(
#         gender_repo=gender_repo,
#         hair_style_repo=hair_style_repo,
#         length_repo=length_repo,
#         hair_style_length_repo=hair_style_length_repo,
#         hair_design_repo=hair_design_repo,
#         hair_design_color_repo=hair_design_color_repo,
#         hair_variant_model_repo=hair_variant_model_repo
#     )
#
# class HairModelPublishApplicationService:
#     def __init__(
#             self,
#             hair_model_query_service: HairModelQueryService
#     ):
#         self.hair_model_query_service = hair_model_query_service
#
#     def publish(self):
#         """
#         hair_variant_model
#         :return:
#         """
#
