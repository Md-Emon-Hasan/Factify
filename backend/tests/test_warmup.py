import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app, warm_up_model
from app.core.config import settings


@pytest.fixture
def warmup_enabled(monkeypatch):
    monkeypatch.setattr(settings, "MODEL_WARMUP_ENABLED", True)


def test_warm_up_runs_when_enabled(warmup_enabled):
    with patch("app.services.prediction.detector.predict") as mock_predict:
        warm_up_model()
        mock_predict.assert_called_once_with(settings.MODEL_WARMUP_TEXT)


def test_warm_up_logs_elapsed_time(warmup_enabled):
    with patch("app.services.prediction.detector.predict"):
        with patch("app.main.logger") as mock_logger:
            warm_up_model()
            messages = [
                call.args[0] for call in mock_logger.info.call_args_list
            ]
            assert any("warm-up starting" in m for m in messages)
            assert any("warm-up completed in" in m for m in messages)


def test_warm_up_failure_does_not_crash(warmup_enabled):
    with patch(
        "app.services.prediction.detector.predict",
        side_effect=Exception("boom"),
    ):
        with patch("app.main.logger") as mock_logger:
            warm_up_model()
            mock_logger.error.assert_called()


def test_app_still_starts_when_warm_up_fails(warmup_enabled):
    with patch(
        "app.services.prediction.detector.predict",
        side_effect=Exception("boom"),
    ):
        with TestClient(app) as started:
            assert started.get("/health").status_code == 200


def test_warm_up_skipped_when_disabled(monkeypatch):
    monkeypatch.setattr(settings, "MODEL_WARMUP_ENABLED", False)
    with patch("app.services.prediction.detector.predict") as mock_predict:
        with patch("app.main.logger") as mock_logger:
            warm_up_model()
            mock_predict.assert_not_called()
            mock_logger.info.assert_called_with(
                "Model warm-up disabled, skipping"
            )


def test_lifespan_runs_warm_up(warmup_enabled):
    with patch("app.main.warm_up_model") as mock_warmup:
        with TestClient(app):
            pass
        mock_warmup.assert_called_once()


def test_model_info_returns_expected_fields(client):
    response = client.get("/api/model-info")
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == settings.MODEL_NAME
    assert data["architecture"] == settings.MODEL_ARCHITECTURE
    assert data["accuracy"] == settings.MODEL_ACCURACY
    assert data["max_sequence_length"] == settings.MAX_SEQUENCE_LENGTH
    assert data["vocabulary_size"] == settings.VOCAB_SIZE
    assert isinstance(data["model_loaded"], bool)
