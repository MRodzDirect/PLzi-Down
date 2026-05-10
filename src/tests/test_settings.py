from platzi.settings import AppSettings, ProxySettings, load_settings, save_settings


def test_settings_roundtrip(tmp_path):
    settings_path = tmp_path / "settings.json"
    expected = AppSettings(
        proxy=ProxySettings(
            enabled=True,
            pool=["socks5://127.0.0.1:9001", "socks5://127.0.0.1:9002"],
            rotation_seconds=120,
            browser_enabled=False,
        )
    )

    save_settings(expected, path=settings_path)
    loaded = load_settings(path=settings_path)
    assert loaded == expected


def test_load_settings_returns_default_when_missing(tmp_path):
    settings_path = tmp_path / "missing.json"
    loaded = load_settings(path=settings_path)
    assert loaded == AppSettings()
