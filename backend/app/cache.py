"""Shared Redis singleton — used by rate limiter and brute-force protection.

Falls back to None when REDIS_URL is not set or Redis is unreachable.
Call get_redis() on each use; the first call initialises the connection pool.
"""
import logging
import threading

_log = logging.getLogger(__name__)

_client = None
_init_lock = threading.Lock()
_initialised = False


def get_redis():
    """Return a sync Redis client or None (in-process fallback active)."""
    global _client, _initialised
    if _initialised:
        return _client
    with _init_lock:
        if _initialised:
            return _client
        _initialised = True
        try:
            from .config import get_settings
            url = get_settings().redis_url
            if not url:
                return None
            import redis as _redis
            client = _redis.from_url(url, socket_connect_timeout=1, decode_responses=True)
            client.ping()
            _client = client
        except Exception as e:
            # REDIS_URL was explicitly set — a silent fall-through would leave
            # rate limiting and brute-force lockout per-process in a multi-replica
            # deployment. Keep the fallback (availability) but say so loudly.
            _log.error("REDIS_URL is set but Redis is unusable (%s: %s). "
                       "Falling back to in-process limits — NOT multi-replica safe.",
                       type(e).__name__, e)
            _client = None
    return _client


def reset_for_tests() -> None:
    """Force re-initialisation — called from test fixtures that inject a fake Redis."""
    global _client, _initialised
    _client = None
    _initialised = False
