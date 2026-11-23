import logging

from fastapi import FastAPI

from . import migrate
from .config import Settings
from .db import connect
from .errors import install_error_handlers
from .notifier import NullNotifier
from .public import TTLCache
from .routers.admin import admin_router, login_router
from .routers.public import public_router
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


def create_app(settings=None, clock=utcnow, notifier=None):
    settings = settings or Settings.from_env()
    _configure_logging()
    ensure_schema_current(settings.db_path)
    docs = {} if settings.enable_docs else {"docs_url": None, "redoc_url": None, "openapi_url": None}
    app = FastAPI(title="Japri API", **docs)
    app.state.settings = settings
    app.state.clock = clock
    app.state.notifier = notifier or NullNotifier()
    app.state.public_cache = TTLCache(settings.public_cache_seconds)
    install_error_handlers(app)
    app.include_router(login_router)
    app.include_router(admin_router)
    app.include_router(public_router)
    return app
