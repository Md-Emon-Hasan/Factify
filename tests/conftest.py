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
