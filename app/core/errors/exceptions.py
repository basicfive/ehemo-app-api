class NoInferenceConsumerException(Exception):
    def __init__(self):
        self.message = "No active inference consumers connected to queue"
        super().__init__(self.message)

    def __str__(self):
        return self.message