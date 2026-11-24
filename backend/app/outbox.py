import asyncio
import logging
from datetime import timedelta

from .db import connect
from .telegram import TelegramError
from .timeutil import to_db

log = logging.getLogger("japri.outbox")
POLL_SECONDS = 2
UPDATE_KEEP_DAYS = 7
_STALE_KINDS = ("booking_created", "booking_updated")


def send_pending(conn, client, now):
    """Kirim semua pesan `pending` berurutan menurut id (menjaga urutan per driver). Satu percobaan per pesan, tanpa coba ulang."""
    sent = 0
    rows = conn.execute("SELECT id FROM telegram_message WHERE status = 'pending' ORDER BY id").fetchall()
    for (message_id,) in rows:
        msg = conn.execute(
            "SELECT m.*, b.status AS booking_status FROM telegram_message m JOIN booking b ON b.id = m.booking_id "
            "WHERE m.id = ? AND m.status = 'pending'",
            (message_id,),
        ).fetchone()
        if msg is None:
            continue
        if msg["kind"] in _STALE_KINDS and msg["booking_status"] == "cancelled":
            conn.execute("UPDATE telegram_message SET status = 'skipped' WHERE id = ?", (message_id,))
            continue
        stamp = to_db(now())
        try:
            telegram_message_id = client.send_message(msg["chat_id"], msg["text"])
        except TelegramError as exc:
            conn.execute(
                "UPDATE telegram_message SET status = 'failed', attempts = 1, error_code = ?, error_detail = ? WHERE id = ?",
                (exc.code, exc.detail, message_id),
            )
            continue
        conn.execute(
            "UPDATE telegram_message SET status = 'sent', attempts = 1, telegram_message_id = ?, sent_at = ? WHERE id = ?",
            (telegram_message_id, stamp, message_id),
        )
        sent += 1
    return sent


def run_once(db_path, client, now):
    conn = connect(db_path)
    try:
        sent = send_pending(conn, client, now)
        conn.execute("DELETE FROM telegram_update WHERE received_at < ?", (to_db(now() - timedelta(days=UPDATE_KEEP_DAYS)),))
        return sent
    finally:
        conn.close()


async def run_forever(db_path, client, now):
    while True:
        try:
            await asyncio.to_thread(run_once, db_path, client, now)
        except Exception as exc:
            log.error("worker pesan Telegram gagal: %s", type(exc).__name__)
        await asyncio.sleep(POLL_SECONDS)
