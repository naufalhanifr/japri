import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import migrate, outbox
from .config import Settings
from .db import connect
from .errors import install_error_handlers
from .notifier import OutboxNotifier
from .public import TTLCache
from .routers.admin import admin_router, login_router
from .routers.public import public_router
from .routers.telegram import webhook_router
from .telegram import TelegramClient
from .timeutil import utcnow


def ensure_schema_current(db_path):
    conn = connect(db_path)
    try:
        todo = migrate.pending(conn)
    finally:
        conn.close()
    if todo:
        raise RuntimeError("Skema database belum terbaru. Jalankan: python -m app.cli migrate")


def _configure_logging():
    log = logging.getLogger("japri")
    log.setLevel(logging.INFO)
    if not log.handlers and not logging.getLogger().handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
        log.addHandler(handler)


def create_app(settings=None, clock=utcnow, notifier=None, telegram=None):
    """`telegram`: klien Bot API. Kosong: dibuat dari token di environment, atau tidak ada bila token kosong."""
    settings = settings or Settings.from_env()
    _configure_logging()
    ensure_schema_current(settings.db_path)
    if telegram is None and settings.telegram_bot_token:
        telegram = TelegramClient(settings.telegram_bot_token, settings.telegram_api_base)

    @asynccontextmanager
    async def lifespan(app):
        # Satu worker di satu proses menjaga urutan kirim per driver (SA 6.3).
        worker = asyncio.create_task(outbox.run_forever(settings.db_path, telegram, clock)) if telegram else None
        yield
        if worker:
            worker.cancel()

    docs = {} if settings.enable_docs else {"docs_url": None, "redoc_url": None, "openapi_url": None}
    app = FastAPI(title="Japri API", lifespan=lifespan, **docs)
    app.state.settings = settings
    app.state.clock = clock
    app.state.notifier = notifier or OutboxNotifier(settings)
    app.state.telegram = telegram
    app.state.public_cache = TTLCache(settings.public_cache_seconds)
    install_error_handlers(app)
    app.include_router(login_router)
    app.include_router(admin_router)
    app.include_router(public_router)
    app.include_router(webhook_router)
    return app
