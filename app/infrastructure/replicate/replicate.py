import replicate

def replicate_predict(replicate_model: str, message: str, webhook_url: str):
    deployment = replicate.deployments.get(replicate_model)
    prediction = deployment.predictions.create(
        input={"message": message},
        webhook=webhook_url,
        webhook_events_filter=["completed"],
    )
