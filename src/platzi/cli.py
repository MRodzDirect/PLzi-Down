import asyncio

import typer
from rich import print
from typing_extensions import Annotated

from platzi import AsyncPlatzi, Cache
from platzi.settings import ProxySettings, load_settings, save_settings

app = typer.Typer(rich_markup_mode="rich")
settings_app = typer.Typer()
proxy_app = typer.Typer()
settings_app.add_typer(proxy_app, name="proxy")
app.add_typer(settings_app, name="settings")


@app.command()
def login():
    """
    Open a browser window to Login to Platzi.

    Usage:
        platzi login
    """
    asyncio.run(_login())


@app.command()
def logout():
    """
    Delete the Platzi session from the local storage.

    Usage:
        platzi logout
    """
    asyncio.run(_logout())


@app.command()
def download(
    url: Annotated[
        str,
        typer.Argument(
            help="The URL of the course to download",
            show_default=False,
        ),
    ],
    # TODO: Define a Quality enum (e.g. 360p, 720p, 1080p,...)
    # and use it here instead of str
    quality: Annotated[
        str,
        typer.Option(
            "--quality",
            "-q",
            help="The quality of the video to download.",
            show_default=True,
        ),
    ] = "720",
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            "-w",
            help="Overwrite files if exist.",
            show_default=True,
        ),
    ] = False,
):
    """
    Download a Platzi course from the given URL.

    Arguments:
        url: str - The URL of the course to download.

    Usage:
        platzi download <url>

    Example:
        platzi download https://platzi.com/cursos/python/
    """
    asyncio.run(_download(url, quality=quality, overwrite=overwrite))


@app.command()
def clear_cache():
    """
    Clear the Platzi CLI cache.

    Usage:
        platzi clear-cache
    """
    Cache.clear()
    print("[green]Cache cleared successfully 🗑️[/green]")


@proxy_app.command("show")
def proxy_show():
    """
    Show proxy settings.
    """
    settings = load_settings()
    print(settings.proxy.model_dump_json(indent=4))


@proxy_app.command("set")
def proxy_set(
    proxy: Annotated[
        list[str],
        typer.Option(
            "--proxy",
            "-p",
            help="Proxy URL. Repeat the option to build a rotating pool.",
        ),
    ] = [],
    rotation_seconds: Annotated[
        int,
        typer.Option(
            "--rotation-seconds",
            help="Rotate to the next proxy after this number of seconds.",
            min=1,
        ),
    ] = 300,
    enabled: Annotated[
        bool,
        typer.Option(
            "--enable/--disable",
            help="Enable or disable proxy usage.",
        ),
    ] = True,
    browser_enabled: Annotated[
        bool,
        typer.Option(
            "--browser/--no-browser",
            help="Apply proxy pool to browser scraping pages too.",
        ),
    ] = True,
):
    """
    Configure rotating proxy settings.
    """
    settings = load_settings()
    filtered_proxy_urls = [clean for item in proxy if (clean := item.strip())]
    proxy_urls = filtered_proxy_urls if filtered_proxy_urls else settings.proxy.pool

    if enabled and not proxy_urls:
        raise typer.BadParameter("Provide at least one --proxy value when enabling.")

    settings.proxy = ProxySettings(
        enabled=enabled,
        pool=proxy_urls,
        rotation_seconds=rotation_seconds,
        browser_enabled=browser_enabled,
    )
    save_settings(settings)
    print("[green]Proxy settings saved[/green]")


@proxy_app.command("clear")
def proxy_clear():
    """
    Clear proxy settings.
    """
    settings = load_settings()
    settings.proxy = ProxySettings()
    save_settings(settings)
    print("[green]Proxy settings cleared[/green]")


async def _login():
    async with AsyncPlatzi() as platzi:
        await platzi.login()


async def _logout():
    async with AsyncPlatzi() as platzi:
        await platzi.logout()


async def _download(url: str, **kwargs):
    async with AsyncPlatzi() as platzi:
        await platzi.download(url, **kwargs)
