from typing import Optional

from app.domain import GenerationRequest

class FCMMessageFlag:
    def __init__(
            self,
            to_send: bool,
            generation_request: Optional[GenerationRequest] = None,
    ):
        self.to_send=to_send
        self.generation_request=generation_request