import pytest
from unittest.mock import MagicMock
from app.core.limiter import get_client_ip, limiter

ARTICLE = (
    "Officials confirmed the new transport policy will take effect next "
    "month across the northern regions of the country."
)


@pytest.fixture(autouse=True)
def stub_detector(monkeypatch):
    monkeypatch.setattr(
        "app.api.endpoints.detector.predict",
        lambda text: ("REAL", 0.88),
    )


def _post(client, ip, text=ARTICLE):
    return client.post(
        "/predict",
        json={"text": text},
        headers={"X-Forwarded-For": ip},
    )


def test_requests_under_the_limit_succeed(client):
    for _ in range(5):
        assert _post(client, "10.0.0.1").status_code == 200


def test_exceeding_the_limit_returns_429(client):
    for _ in range(20):
        assert _post(client, "10.0.0.2").status_code == 200

    blocked = _post(client, "10.0.0.2")
    assert blocked.status_code == 429
    assert blocked.json() == {
        "detail": "Rate limit exceeded. Please try again shortly."
    }
    assert blocked.headers["Retry-After"] == "60"


def test_different_forwarded_ips_get_separate_buckets(client):
    for _ in range(20):
        assert _post(client, "10.0.0.3").status_code == 200

    assert _post(client, "10.0.0.3").status_code == 429
    assert _post(client, "10.0.0.4").status_code == 200


def test_health_endpoints_are_never_limited(client):
    for _ in range(30):
        assert client.get("/health").status_code == 200
        assert client.get("/").status_code == 200


def test_model_info_is_not_limited(client):
    for _ in range(30):
        assert client.get("/api/model-info").status_code == 200


def test_rate_limiting_disabled(client, monkeypatch):
    monkeypatch.setattr(limiter, "enabled", False)
    for _ in range(25):
        assert _post(client, "10.0.0.5").status_code == 200


def test_get_client_ip_uses_first_forwarded_entry():
    request = MagicMock()
    request.headers = {"X-Forwarded-For": "203.0.113.7, 70.41.3.18"}
    assert get_client_ip(request) == "203.0.113.7"


def test_get_client_ip_falls_back_to_remote_address():
    request = MagicMock()
    request.headers = {}
    request.client.host = "198.51.100.9"
    assert get_client_ip(request) == "198.51.100.9"


def test_get_client_ip_ignores_blank_forwarded_header():
    request = MagicMock()
    request.headers = {"X-Forwarded-For": "  ,  "}
    request.client.host = "198.51.100.10"
    assert get_client_ip(request) == "198.51.100.10"
