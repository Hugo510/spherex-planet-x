"""Cliente HTTP compartido (keep-alive, reintentos con backoff). Todo el acceso a datos es anónimo."""

from __future__ import annotations

import os
import time

import httpx

USER_AGENT = "spherex-honest-comparator/0.1 (NASA Space Apps 2026; anonymous)"
_client: httpx.Client | None = None


def offline() -> bool:
    return os.environ.get("SPHEREX_OFFLINE") == "1"


def client() -> httpx.Client:
    global _client
    if _client is None:
        _client = httpx.Client(
            timeout=httpx.Timeout(120.0, connect=30.0),
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
            limits=httpx.Limits(max_connections=12, max_keepalive_connections=12),
        )
    return _client


def get(url: str, *, headers: dict | None = None, retries: int = 4, params: dict | None = None) -> httpx.Response:
    last: Exception | None = None
    for i in range(retries):
        try:
            r = client().get(url, headers=headers, params=params)
            if r.status_code in (200, 206):
                return r
            if 400 <= r.status_code < 500 and r.status_code != 429:
                r.raise_for_status()
            last = RuntimeError(f"HTTP {r.status_code} {url[:120]}")
        except httpx.HTTPStatusError:
            raise
        except Exception as e:  # noqa: BLE001 — errores transitorios de red
            last = e
        time.sleep(1.5 * (2**i))
    raise RuntimeError(f"fallo tras {retries} intentos: {url[:160]}: {last}")


def post(url: str, data: dict, *, retries: int = 5) -> httpx.Response:
    last: Exception | None = None
    for i in range(retries):
        try:
            r = client().post(url, data=data, timeout=httpx.Timeout(300.0, connect=30.0))  # el TAP tarda > 2 min en campos densos
            if r.status_code == 200:
                return r
            last = RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
            if 400 <= r.status_code < 500 and r.status_code != 429:
                break
        except Exception as e:  # noqa: BLE001
            last = e
        time.sleep(2.0 * (2**i))
    raise RuntimeError(f"fallo POST {url}: {last}")
