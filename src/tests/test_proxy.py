from platzi.proxy import ProxyPool


def test_proxy_pool_returns_none_when_disabled():
    pool = ProxyPool(pool=["socks5://127.0.0.1:9050"], rotation_seconds=30, enabled=False)
    assert pool.current_url() is None


def test_proxy_pool_rotates_by_time(monkeypatch):
    state = {"now": 0.0}

    def fake_monotonic():
        return state["now"]

    monkeypatch.setattr("platzi.proxy.time.monotonic", fake_monotonic)

    pool = ProxyPool(
        pool=["socks5://127.0.0.1:9001", "socks5://127.0.0.1:9002"],
        rotation_seconds=10,
        enabled=True,
    )

    assert pool.current_url() == "socks5://127.0.0.1:9001"
    state["now"] = 9.0
    assert pool.current_url() == "socks5://127.0.0.1:9001"
    state["now"] = 10.0
    assert pool.current_url() == "socks5://127.0.0.1:9002"
    state["now"] = 21.0
    assert pool.current_url() == "socks5://127.0.0.1:9001"
