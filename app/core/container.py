from typing import Dict, Type, Any, Callable
from sqlalchemy.orm import Session

from app.infrastructure.s3.s3_client import S3Client
from app.infrastructure.fcm.fcm_service import FCMService

class DependencyContainer:
   """의존성 관리를 위한 컨테이너 클래스"""

   def __init__(self, session_factory: Callable[[], Session]):
       self._session_factory = session_factory
       # 세션과 무관한 서비스들만 캐싱
       self._service_instances: Dict[Type, Any] = {}

   def get_repository_with_session(self, repo_class: Type, session: Session) -> Any:
       """특정 세션을 사용하는 Repository 인스턴스를 생성"""
       return repo_class(db=session)

   def get_repository(self, repo_class: Type) -> Any:
       """새로운 세션으로 Repository 인스턴스를 생성"""
       session = self._session_factory()
       return repo_class(db=session)

   @property
   def s3_client(self) -> S3Client:
       if S3Client not in self._service_instances:
           self._service_instances[S3Client] = S3Client()
       return self._service_instances[S3Client]

   @property
   def fcm_service(self) -> FCMService:
       if FCMService not in self._service_instances:
           self._service_instances[FCMService] = FCMService()
       return self._service_instances[FCMService]

   def cleanup(self):
       """리소스 정리"""
       self._service_instances.clear()