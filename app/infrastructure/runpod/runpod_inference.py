import requests
from app.core.config import runpod_settings
from app.infrastructure.runpod.dto import InferencePayload, RunpodRequest

def request_runpod(payload: InferencePayload):
    runpod_endpoint = runpod_settings.RUNPOD_ENDPOINT
    print(f"🚀 Sending request: {payload.model_dump(mode='json')}")

    request = RunpodRequest(
        input=payload.model_dump(mode="json"),
    )

    response = requests.post(
        runpod_endpoint,
        json=request.model_dump(mode="json"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {runpod_settings.RUNPOD_API_KEY}"
        }
    )
    print(response.json())


