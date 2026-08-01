import time
import pytest
from cachetools import TTLCache
from app.core import cache as cache_module
from app.core.cache import cached, clear_cache, cache_stats, make_cache_key
from app.core.config import settings


@pytest.fixture
def counter():
    return {"calls": 0}


def test_cache_hit_skips_wrapped_function(counter):
    @cached(prefix="unit")
    def expensive(text):
        counter["calls"] += 1
        return ("REAL", 0.9)

    text = "A sufficiently long article body used for cache testing."
    assert expensive(text) == ("REAL", 0.9)
    assert expensive(text) == ("REAL", 0.9)
    assert counter["calls"] == 1


def test_normalized_inputs_share_a_key(counter):
    @cached(prefix="unit")
    def expensive(text):
        counter["calls"] += 1
        return ("FAKE", 0.1)

    expensive("Breaking News   About\nSomething")
    expensive("  breaking news about something  ")
    assert counter["calls"] == 1


def test_different_texts_do_not_collide(counter):
    @cached(prefix="unit")
    def expensive(text):
        counter["calls"] += 1
        return ("REAL", 0.9)

    expensive("first distinct article body")
    expensive("second distinct article body")
    assert counter["calls"] == 2


def test_make_cache_key_is_a_prefixed_sha256():
    key = make_cache_key("predict", "  Hello   World  ")
    prefix, digest = key.split(":")
    assert prefix == "predict"
    assert len(digest) == 64
    assert key == make_cache_key("predict", "hello world")


def test_ttl_expiry_causes_a_miss(counter, monkeypatch):
    monkeypatch.setattr(
        cache_module, "_cache", TTLCache(maxsize=10, ttl=0.05)
    )

    @cached(prefix="unit")
    def expensive(text):
        counter["calls"] += 1
        return ("REAL", 0.9)

    expensive("an article that should expire quickly")
    time.sleep(0.1)
    expensive("an article that should expire quickly")
    assert counter["calls"] == 2


@pytest.mark.parametrize("bad_result", [None, "", (), ("ERROR", 0.0)])
def test_unsuccessful_results_are_not_cached(counter, bad_result):
    @cached(prefix="unit")
    def failing(text):
        counter["calls"] += 1
        return bad_result

    failing("an article that fails to be classified properly")
    failing("an article that fails to be classified properly")
    assert counter["calls"] == 2
    assert cache_stats()["size"] == 0


def test_non_string_arguments_bypass_the_cache(counter):
    @cached(prefix="unit")
    def expensive(number):
        counter["calls"] += 1
        return ("REAL", 0.9)

    expensive(1)
    expensive(1)
    assert counter["calls"] == 2


def test_keyword_argument_is_used_for_the_key(counter):
    @cached(prefix="unit")
    def expensive(text=None):
        counter["calls"] += 1
        return ("REAL", 0.9)

    expensive(text="a keyword supplied article body for hashing")
    expensive(text="A KEYWORD SUPPLIED ARTICLE BODY FOR HASHING")
    assert counter["calls"] == 1


def test_cache_stats_and_clear_cache(counter):
    @cached(prefix="unit")
    def expensive(text):
        counter["calls"] += 1
        return ("REAL", 0.9)

    empty = cache_stats()
    assert empty["hits"] == 0
    assert empty["misses"] == 0
    assert empty["hit_rate"] == 0.0
    assert empty["maxsize"] == settings.CACHE_MAXSIZE
    assert empty["ttl"] == settings.CACHE_TTL_SECONDS

    expensive("a stats article body long enough to be realistic")
    expensive("a stats article body long enough to be realistic")

    stats = cache_stats()
    assert stats["size"] == 1
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["hit_rate"] == 0.5

    clear_cache()
    cleared = cache_stats()
    assert cleared["size"] == 0
    assert cleared["hits"] == 0
    assert cleared["misses"] == 0


def test_cache_disabled_is_a_pass_through(counter, monkeypatch):
    monkeypatch.setattr(settings, "CACHE_ENABLED", False)

    @cached(prefix="unit")
    def expensive(text):
        counter["calls"] += 1
        return ("REAL", 0.9)

    expensive("a disabled cache article body used twice")
    expensive("a disabled cache article body used twice")
    assert counter["calls"] == 2
    assert cache_stats()["size"] == 0


def test_endpoint_caches_repeat_predictions(client, monkeypatch):
    calls = {"count": 0}

    def fake_predict(text):
        calls["count"] += 1
        return ("REAL", 0.87)

    monkeypatch.setattr(
        "app.api.endpoints.detector.predict", fake_predict
    )

    payload = {"text": "The same article submitted twice in a row."}
    first = client.post("/predict", json=payload)
    second = client.post("/predict", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()
    assert calls["count"] == 1
