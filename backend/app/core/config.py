import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Factify"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    LOGS_DIR: str = os.path.join(BASE_DIR, "logs")
    
    # Model Paths
    # Use os.path.join for cross-platform compatibility
    MODEL_PATH: str = os.path.join(BASE_DIR, "models", "saved_models", "fake_news_detector.h5")
    TOKENIZER_PATH: str = os.path.join(BASE_DIR, "models", "saved_models", "tokenizer.pickle")

    # Model Metadata (reported by /api/model-info)
    MODEL_NAME: str = "fake_news_detector"
    MODEL_ARCHITECTURE: str = "LSTM-GRU Hybrid"
    MODEL_ACCURACY: float = 0.99
    MAX_SEQUENCE_LENGTH: int = 100
    VOCAB_SIZE: int = 10000

    # Response Caching (in-memory, TTL based)
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 3600
    CACHE_MAXSIZE: int = 500

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PREDICT: str = "20/minute"

    # Model Warm-up
    MODEL_WARMUP_ENABLED: bool = True
    MODEL_WARMUP_TEXT: str = "the quick brown fox jumps over the lazy dog"

    # Input Validation Thresholds
    MIN_INPUT_LENGTH: int = 50
    MIN_WORD_COUNT: int = 10
    MAX_INPUT_LENGTH: int = 20000

    class Config:
        case_sensitive = True

settings = Settings()
