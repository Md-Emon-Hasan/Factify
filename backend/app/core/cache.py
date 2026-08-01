import functools
import hashlib
import threading
from cachetools import TTLCache
from app.core.config import settings
from app.core.logger import logger

# TTLCache is not thread-safe and sync endpoints run in FastAPI's threadpool
_lock = threading.Lock()
_cache = TTLCache(
    maxsize=settings.CACHE_MAXSIZE,
    ttl=settings.CACHE_TTL_SECONDS,
)

_hits = 0
_misses = 0

_MISS = object()


def make_cache_key(prefix, text):
    normalized = " ".join(text.strip().lower().split())
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"


def _is_cacheable(result):
    if result is None:
        return False
    if isinstance(result, (str, bytes, list, tuple, dict, set)):
        if len(result) == 0:
            return False
        # The detector reports failures as ("ERROR", 0.0)
        if isinstance(result, (list, tuple)):
            first = result[0]
            if isinstance(first, str) and first.upper() == "ERROR":
                return False
    return True


def _extract_text(args, kwargs):
    for value in args:
        if isinstance(value, str):
            return value
    for value in kwargs.values():
        if isinstance(value, str):
            return value
    return None


def _cache_get(key):
    global _hits, _misses
    with _lock:
        value = _cache.get(key, _MISS)
        if value is _MISS:
            _misses += 1
            return _MISS
        _hits += 1
        return value


def _cache_set(key, value):
    with _lock:
        _cache[key] = value


def cached(prefix):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not settings.CACHE_ENABLED:
                return func(*args, **kwargs)

            text = _extract_text(args, kwargs)
            if text is None:
                return func(*args, **kwargs)

            key = make_cache_key(prefix, text)
            value = _cache_get(key)
            if value is not _MISS:
                logger.info(f"Cache hit for {key}")
                return value

            logger.info(f"Cache miss for {key}")
            result = func(*args, **kwargs)
            if _is_cacheable(result):
                _cache_set(key, result)
            return result

        return wrapper
    return decorator


def clear_cache():
    global _hits, _misses
    with _lock:
        _cache.clear()
        _hits = 0
        _misses = 0


def cache_stats():
    with _lock:
        total = _hits + _misses
        hit_rate = (_hits / total) if total else 0.0
        return {
            "size": len(_cache),
            "maxsize": _cache.maxsize,
            "ttl": _cache.ttl,
            "hits": _hits,
            "misses": _misses,
            "hit_rate": round(hit_rate, 4),
        }
