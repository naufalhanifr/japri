from datetime import date, datetime, timedelta, timezone

import pytest

from app.config import Settings
from app.timeutil import WIB, from_db, to_db, to_wib_iso, wib_date, wib_day_range_utc


def test_settings_defaults_match_sa():
    s = Settings()
    assert (s.session_ttl_minutes, s.session_idle_minutes) == (480, 30)
    assert (s.login_max_failures, s.login_window_minutes) == (10, 15)
    assert s.cookie_secure is True and s.enable_docs is False


def test_settings_from_env():
    s = Settings.from_env(
        {
            "JAPRI_DB_PATH": "/x/j.db",
            "JAPRI_LOGIN_MAX_FAILURES": "3",
            "JAPRI_COOKIE_SECURE": "false",
            "JAPRI_TRUSTED_PROXIES": "10.0.0.1, 10.0.0.2",
        }
    )
    assert s.db_path == "/x/j.db" and s.login_max_failures == 3 and s.cookie_secure is False
    assert s.trusted_proxies == ("10.0.0.1", "10.0.0.2")


@pytest.mark.parametrize(
    "env", [{"JAPRI_LOGIN_MAX_FAILURES": "abc"}, {"JAPRI_LOGIN_MAX_FAILURES": "0"}, {"JAPRI_COOKIE_SECURE": "maybe"}]
)
def test_settings_rejects_bad_values(env):
    with pytest.raises(ValueError):
        Settings.from_env(env)


def test_db_time_roundtrip_and_wib_offset():
    dt = datetime(2026, 11, 22, 8, 0, 0, tzinfo=timezone.utc)
    assert to_db(dt) == "2026-11-22T08:00:00Z"
    assert from_db(to_db(dt)) == dt
    assert to_wib_iso("2026-11-22T08:00:00Z") == "2026-11-22T15:00:00+07:00"
    assert to_db(datetime(2026, 11, 22, 15, 0, tzinfo=WIB)) == "2026-11-22T08:00:00Z"


def test_naive_datetime_rejected():
    with pytest.raises(ValueError):
        to_db(datetime(2026, 11, 22, 8, 0))


def test_wib_day_boundary_at_midnight():
    before = datetime(2026, 11, 22, 16, 59, 59, tzinfo=timezone.utc)  # 23:59:59 WIB
    after = before + timedelta(seconds=1)  # 00:00:00 WIB hari berikutnya
    assert wib_date(before) == date(2026, 11, 22)
    assert wib_date(after) == date(2026, 11, 23)


def test_wib_day_range_is_half_open_24h():
    start, end = wib_day_range_utc(date(2026, 11, 23))
    assert to_db(start) == "2026-11-22T17:00:00Z"
    assert to_db(end) == "2026-11-23T17:00:00Z"
