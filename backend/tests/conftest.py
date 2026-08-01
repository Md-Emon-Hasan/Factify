import sys
import os
# Ensure app module can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_prediction_payload():
    return {"text": "This is a test news article."}


from app.core import cache as cache_module  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.core.limiter import limiter  # noqa: E402


@pytest.fixture(autouse=True)
def reset_cache():
    cache_module.clear_cache()
    yield
    cache_module.clear_cache()


@pytest.fixture(autouse=True)
def reset_limiter():
    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture(autouse=True)
def skip_warmup(monkeypatch):
    # Warm-up runs a real TF inference, too slow for the suite
    monkeypatch.setattr(settings, "MODEL_WARMUP_ENABLED", False)


@pytest.fixture(autouse=True)
def relaxed_validation(monkeypatch):
    # Keeps the older tests' short fixtures valid; test_validation.py
    # restores the real thresholds for its own cases
    monkeypatch.setattr(settings, "MIN_INPUT_LENGTH", 0)
    monkeypatch.setattr(settings, "MIN_WORD_COUNT", 0)
