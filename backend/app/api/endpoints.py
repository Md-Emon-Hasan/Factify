from fastapi import APIRouter, HTTPException, Request
from app.models.schemas import (
    PredictionRequest,
    PredictionResponse,
    ModelInfoResponse,
)
from app.services.prediction import detector
from app.core.cache import cached
from app.core.config import settings
from app.core.limiter import limiter
from app.core.logger import logger

router = APIRouter()


@cached(prefix="predict")
def _run_prediction(text):
    return detector.predict(text)


@router.get("/health")
async def health_check():
    return {"status": "ok", "message": "Factify is running"}


@router.post("/predict", response_model=PredictionResponse)
@limiter.limit(settings.RATE_LIMIT_PREDICT)
def predict_news(request: Request, payload: PredictionRequest):
    # Kept sync so FastAPI runs the CPU-bound inference in its threadpool
    try:
        logger.info(
            f"Received prediction request for text length: "
            f"{len(payload.text)}"
        )

        label, probability = _run_prediction(payload.text)

        return PredictionResponse(
            label=label,
            probability=probability,
            text=payload.text
        )
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/model-info", response_model=ModelInfoResponse)
async def model_info():
    return ModelInfoResponse(
        model_name=settings.MODEL_NAME,
        architecture=settings.MODEL_ARCHITECTURE,
        accuracy=settings.MODEL_ACCURACY,
        max_sequence_length=getattr(
            detector, "max_length", settings.MAX_SEQUENCE_LENGTH
        ),
        vocabulary_size=settings.VOCAB_SIZE,
        model_loaded=detector.model is not None,
    )
