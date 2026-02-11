from fastapi import APIRouter, HTTPException
from app.models.schemas import PredictionRequest, PredictionResponse
from app.services.prediction import detector
from app.core.logger import logger

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok", "message": "Factify is running"}

@router.post("/predict", response_model=PredictionResponse)
async def predict_news(request: PredictionRequest):
    try:
        logger.info(f"Received prediction request for text length: {len(request.text)}")
        
        label, probability = detector.predict(request.text)
        
        return PredictionResponse(
            label=label,
            probability=probability,
            text=request.text
        )
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
