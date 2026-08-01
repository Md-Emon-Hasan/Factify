import pytest
from app.core.config import settings

VALID_TEXT = (
    "Government officials announced a new economic policy today that "
    "aims to reduce inflation over the coming financial year."
)


@pytest.fixture(autouse=True)
def production_thresholds(monkeypatch):
    monkeypatch.setattr(settings, "MIN_INPUT_LENGTH", 50)
    monkeypatch.setattr(settings, "MIN_WORD_COUNT", 10)
    monkeypatch.setattr(settings, "MAX_INPUT_LENGTH", 20000)


@pytest.fixture(autouse=True)
def stub_detector(monkeypatch):
    # Patch the instance the router holds: test_services.py reloads
    # app.services.prediction, replacing that module's detector
    monkeypatch.setattr(
        "app.api.endpoints.detector.predict",
        lambda text: ("REAL", 0.91),
    )


def _detail(response):
    return response.json()["detail"]


def test_too_short_text_is_rejected(client):
    response = client.post("/predict", json={"text": "Too short."})
    assert response.status_code == 422
    assert "too short" in _detail(response).lower()
    assert "50 characters" in _detail(response)


def test_too_few_words_is_rejected(client):
    text = "Supercalifragilistic " + "a" * 60
    response = client.post("/predict", json={"text": text})
    assert response.status_code == 422
    assert "too few words" in _detail(response).lower()


def test_over_max_length_is_rejected(client):
    response = client.post("/predict", json={"text": "word " * 5000})
    assert response.status_code == 422
    assert "too long" in _detail(response).lower()
    assert "20000" in _detail(response)


def test_whitespace_only_is_rejected(client):
    response = client.post("/predict", json={"text": "   \n\t  "})
    assert response.status_code == 422
    assert "empty" in _detail(response).lower()


def test_non_alphabetic_text_is_rejected(client):
    response = client.post(
        "/predict", json={"text": "12345 67890 !!! ??? ... 111 222 333 444"}
    )
    assert response.status_code == 422
    assert "readable words" in _detail(response).lower()


def test_missing_field_still_returns_422(client):
    response = client.post("/predict", json={})
    assert response.status_code == 422
    assert _detail(response)


def test_error_body_keeps_the_standard_errors_list(client):
    response = client.post("/predict", json={"text": "short"})
    body = response.json()
    assert isinstance(body["detail"], str)
    assert isinstance(body["errors"], list)
    assert body["errors"][0]["loc"]


def test_valid_text_passes_through_unchanged(client):
    response = client.post("/predict", json={"text": VALID_TEXT})
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "REAL"
    assert data["probability"] == 0.91
    assert data["text"] == VALID_TEXT
