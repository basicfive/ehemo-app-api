from dataclasses import dataclass

from app.domain import User

@dataclass
class FailedJobResult:
    user: User
    image_generation_job_id: int
    generation_request_id: int