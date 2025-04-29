from typing import Callable

class BaseRouter:
    def handle(self, body: bytes) -> Callable:
        raise NotImplementedError