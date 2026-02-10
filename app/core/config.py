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
    
    class Config:
        case_sensitive = True

settings = Settings()
