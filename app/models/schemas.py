from pydantic import BaseModel

class PredictionRequest(BaseModel):
    text: str

class PredictionResponse(BaseModel):
    label: str
    probability: float
    text: str
