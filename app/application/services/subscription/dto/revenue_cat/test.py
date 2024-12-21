# class Test(BaseModel):
#     # 기본 필드 (null이 아닌 필드들)
#     event_timestamp_ms: int
#     environment: str
#     type: EventType
#     id: str
#     app_id: str
#     app_user_id: str
#     original_app_user_id: str
#     aliases: List[str]
#     period_type: str
#     product_id: str
#     store: str
#     purchased_at_ms: int
#     expiration_at_ms: int
#     subscriber_attributes: Dict[str, SubscriberAttribute]
#
#     # Optional 필드들 (null이 올 수 있는 필드들)
#     commission_percentage: Optional[float]
#     country_code: Optional[str]
#     currency: Optional[str]
#     entitlement_id: Optional[str]
#     entitlement_ids: Optional[List[str]]
#     is_family_share: Optional[bool]
#     offer_code: Optional[str]
#     original_transaction_id: Optional[str]
#     presented_offering_id: Optional[str]
#     price: Optional[float]
#     price_in_purchased_currency: Optional[float]
#     renewal_number: Optional[int]
#     takehome_percentage: Optional[float]
#     tax_percentage: Optional[float]
#     transaction_id: Optional[str]
