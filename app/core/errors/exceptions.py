import json

class CustomServerException(Exception):
    def __init__(self, message: str, context: str):
        self.message = message
        self.context = context
        super().__init__(self.message)

    def __str__(self):
        content = {
            "message":self.message,
            "context":self.context
        }
        return json.dumps(content, ensure_ascii=False)

class NoInferenceConsumerException(CustomServerException):
    def __init__(self, context: str = None):
        message = "No Inference server is connected to queue"
        super().__init__(message, context)

class FCMException(CustomServerException):
    def __init__(self, context: str = None):
        message = "FCM Service error occurred"
        super().__init__(message, context)
