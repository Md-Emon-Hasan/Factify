from pydantic import BaseModel, field_validator
from app.core.config import settings


class PredictionRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, value):
        stripped = value.strip()

        if not stripped:
            raise ValueError(
                "Text cannot be empty or whitespace only."
            )

        if not any(char.isalpha() for char in stripped):
            raise ValueError(
                "Text must contain readable words, not only digits or "
                "punctuation."
            )

        if len(stripped) > settings.MAX_INPUT_LENGTH:
            raise ValueError(
                f"Text is too long ({len(stripped)} characters). Please "
                f"submit at most {settings.MAX_INPUT_LENGTH} characters."
            )

        if len(stripped) < settings.MIN_INPUT_LENGTH:
            raise ValueError(
                f"Text is too short ({len(stripped)} characters). Please "
                f"provide at least {settings.MIN_INPUT_LENGTH} characters "
                f"so the analysis is meaningful."
            )

        word_count = len(stripped.split())
        if word_count < settings.MIN_WORD_COUNT:
            raise ValueError(
                f"Text has too few words ({word_count}). Please provide at "
                f"least {settings.MIN_WORD_COUNT} words so the analysis is "
                f"meaningful."
            )

        return value


class PredictionResponse(BaseModel):
    label: str
    probability: float
    text: str


class ModelInfoResponse(BaseModel):
    model_name: str
    architecture: str
    accuracy: float
    max_sequence_length: int
    vocabulary_size: int
    model_loaded: bool

    model_config = {"protected_namespaces": ()}
