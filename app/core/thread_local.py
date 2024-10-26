import threading

# 1. 클래스 필드값으로 사용하는 법
# class ThreadLocalManager:
#     _thread_local = None
#     _lock = threading.Lock()
#
#     @classmethod
#     def get_thread_local(cls):
#         if cls._thread_local is None:
#             with cls._lock:
#                 if cls._thread_local is None:
#                     cls._thread_local = threading.local()
#         return cls._thread_local

# 2. 싱글톤 인스턴스로 사용하는 방법
from typing import Dict
class ThreadLocalSingleton:
    _instance = None
    _lock = threading.Lock()
    _thread_instances: Dict[int, str] = {}  # 쓰레드 ID: 인스턴스 정보를 추적

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.thread_local = threading.local()
        return cls._instance
