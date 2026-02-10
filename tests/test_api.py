from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Factify is running"}

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Factify" in response.text

@patch("app.services.prediction.detector.predict")
def test_predict_success(mock_predict):
    mock_predict.return_value = ("REAL", 0.95)
    
    response = client.post("/predict", json={"text": "Real news"})
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "REAL"

@patch("app.services.prediction.detector.predict")
def test_predict_error(mock_predict):
    mock_predict.side_effect = Exception("Prediction failed")
    response = client.post("/predict", json={"text": "Error news"})
    assert response.status_code == 500

def test_startup_shutdown_events():
    # TestClient as context manager triggers startup and shutdown events
    with TestClient(app) as _:
        pass
