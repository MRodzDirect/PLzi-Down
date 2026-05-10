import time
from urllib.parse import unquote, urlsplit

import rnet


class ProxyPool:
    def __init__(
        self,
        pool: list[str] | None = None,
        rotation_seconds: int = 300,
        enabled: bool = False,
    ):
        self.pool = [url.strip() for url in (pool or []) if url.strip()]
        self.rotation_seconds = max(1, rotation_seconds)
        self.enabled = enabled
        self._index = 0
        self._last_rotation_at: float | None = None

    def current_url(self) -> str | None:
        if not self.enabled or not self.pool:
            return None

        now = time.monotonic()

        if self._last_rotation_at is None:
            self._last_rotation_at = now
            return self.pool[self._index]

        if now - self._last_rotation_at >= self.rotation_seconds:
            self._index = (self._index + 1) % len(self.pool)
            self._last_rotation_at = now

        return self.pool[self._index]


def build_rnet_proxy(proxy_url: str) -> rnet.Proxy:
    return rnet.Proxy.all(proxy_url)


def build_playwright_proxy(proxy_url: str) -> dict[str, str]:
    parsed = urlsplit(proxy_url)
    if not parsed.scheme or not parsed.hostname or not parsed.port:
        raise ValueError("proxy must include scheme, host and port")

    server = f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
    data = {"server": server}
    if parsed.username:
        data["username"] = unquote(parsed.username)
    if parsed.password:
        data["password"] = unquote(parsed.password)
    return data
