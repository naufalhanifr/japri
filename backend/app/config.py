import os
from dataclasses import dataclass, field

PREFIX = "JAPRI_"


def _int(env, name, default, minimum=1):
    raw = env.get(PREFIX + name)
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except ValueError:
        raise ValueError(f"{PREFIX}{name} harus bilangan bulat") from None
    if value < minimum:
        raise ValueError(f"{PREFIX}{name} minimal {minimum}")
    return value


def _bool(env, name, default):
    raw = env.get(PREFIX + name)
    if raw is None or raw == "":
        return default
    if raw.lower() in ("1", "true", "yes"):
        return True
    if raw.lower() in ("0", "false", "no"):
        return False
    raise ValueError(f"{PREFIX}{name} harus true atau false")


def _opt_int(env, name):
    raw = env.get(PREFIX + name)
    if raw is None or raw.strip() == "":
        return None
    try:
        return int(raw)
    except ValueError:
        raise ValueError(f"{PREFIX}{name} harus bilangan bulat") from None


@dataclass(frozen=True)
class Settings:
    db_path: str = "data/japri.db"
    # SA 8: secret hanya dari environment (file milik root), tidak pernah ke repo, log, API, atau audit.
    telegram_bot_token: str = field(default="", repr=False)
    telegram_webhook_secret: str = field(default="", repr=False)
    telegram_bot_username: str = ""
    telegram_group_chat_id: int = None
    telegram_api_base: str = "https://api.telegram.org"
    link_token_ttl_hours: int = 72
    # SA 2.2: nilai awal Proposed / Needs confirmation.
    session_ttl_minutes: int = 480
    session_idle_minutes: int = 30
    # SA 4.3: nilai awal Proposed / Needs confirmation.
    login_max_failures: int = 10
    login_window_minutes: int = 15
    cookie_secure: bool = True
    trusted_proxies: tuple = ("127.0.0.1", "::1")
    enable_docs: bool = False

    @classmethod
    def from_env(cls, env=None):
        env = os.environ if env is None else env
        d = cls()
        proxies = env.get(PREFIX + "TRUSTED_PROXIES")
        return cls(
            db_path=env.get(PREFIX + "DB_PATH") or d.db_path,
            telegram_bot_token=env.get(PREFIX + "TELEGRAM_BOT_TOKEN", "").strip(),
            telegram_webhook_secret=env.get(PREFIX + "TELEGRAM_WEBHOOK_SECRET", "").strip(),
            telegram_bot_username=env.get(PREFIX + "TELEGRAM_BOT_USERNAME", "").strip().lstrip("@"),
            telegram_group_chat_id=_opt_int(env, "TELEGRAM_GROUP_CHAT_ID"),
            telegram_api_base=(env.get(PREFIX + "TELEGRAM_API_BASE") or d.telegram_api_base).rstrip("/"),
            link_token_ttl_hours=_int(env, "LINK_TOKEN_TTL_HOURS", d.link_token_ttl_hours),
            session_ttl_minutes=_int(env, "SESSION_TTL_MINUTES", d.session_ttl_minutes),
            session_idle_minutes=_int(env, "SESSION_IDLE_MINUTES", d.session_idle_minutes),
            login_max_failures=_int(env, "LOGIN_MAX_FAILURES", d.login_max_failures),
            login_window_minutes=_int(env, "LOGIN_WINDOW_MINUTES", d.login_window_minutes),
            cookie_secure=_bool(env, "COOKIE_SECURE", d.cookie_secure),
            trusted_proxies=tuple(p.strip() for p in proxies.split(",") if p.strip())
            if proxies is not None
            else d.trusted_proxies,
            enable_docs=_bool(env, "ENABLE_DOCS", d.enable_docs),
        )
