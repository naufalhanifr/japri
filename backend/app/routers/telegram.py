import hmac
import logging
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.concurrency import run_in_threadpool

from .. import telegram_bot, telegram_link
from ..audit import Actor
from ..deps import get_conn, get_notifier, get_now, get_settings, require_admin
from ..errors import AppError
from ..timeutil import to_db, to_wib_iso

log = logging.getLogger("japri.telegram")
SECRET_HEADER = "x-telegram-bot-api-secret-token"

webhook_router = APIRouter()
admin_router = APIRouter()


def require_secret(request: Request, settings=Depends(get_settings)):
    sent = request.headers.get(SECRET_HEADER, "")
    expected = settings.telegram_webhook_secret
    if not expected or not hmac.compare_digest(sent.encode(), expected.encode()):
        raise AppError(403, "forbidden", "Permintaan ditolak.")


def _flush(client, actions):
    """Balasan dikirim setelah data tersimpan. Gagal kirim balasan tidak membatalkan apa pun."""
    if client is None:
        return
    for action in actions:
        try:
            if action[0] == "answer":
                client.answer_callback(action[1])
            else:
                client.send_message(action[1], action[2], action[3])
        except Exception as exc:
            log.error("balasan Telegram gagal: %s", getattr(exc, "code", type(exc).__name__))


def _process(conn, settings, now, notifier, client, update):
    update_id = update.get("update_id") if isinstance(update, dict) else None
    if isinstance(update_id, bool) or not isinstance(update_id, int):
        return
    inserted = conn.execute(
        "INSERT OR IGNORE INTO telegram_update (update_id, received_at) VALUES (?, ?)", (update_id, to_db(now))
    )
    if inserted.rowcount == 0:
        return
    try:
        actions = telegram_bot.handle_update(conn, settings, now, notifier, update)
    except Exception:
        conn.execute("DELETE FROM telegram_update WHERE update_id = ?", (update_id,))
        raise
    _flush(client, actions)


@webhook_router.post("/api/telegram/webhook", dependencies=[Depends(require_secret)])
async def webhook(request: Request, conn=Depends(get_conn), settings=Depends(get_settings), now=Depends(get_now),
                  notifier=Depends(get_notifier)):
    try:
        update = await request.json()
    except ValueError:
        update = None
    await run_in_threadpool(_process, conn, settings, now, notifier, request.app.state.telegram, update)
    return Response(status_code=200)


@admin_router.post("/drivers/{driver_id}/telegram-link", status_code=201)
def create_link(driver_id: int, conn=Depends(get_conn), settings=Depends(get_settings), now=Depends(get_now),
                session=Depends(require_admin)):
    return telegram_link.create_code(conn, Actor.admin(session.admin.id, session.admin.email), now, settings, driver_id)


@admin_router.get("/telegram-messages")
def list_messages(
    status: Optional[Literal["pending", "sent", "failed", "skipped"]] = None,
    driver_id: Optional[int] = None,
    booking_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    conn=Depends(get_conn),
):
    where, params = ["1 = 1"], {}
    for column, value in (("m.status", status), ("m.driver_id", driver_id), ("m.booking_id", booking_id)):
        if value is not None:
            key = column.split(".")[1]
            where.append(f"{column} = :{key}")
            params[key] = value
    where_sql = " WHERE " + " AND ".join(where)
    join = " FROM telegram_message m JOIN driver d ON d.id = m.driver_id JOIN booking b ON b.id = m.booking_id"
    total = conn.execute("SELECT COUNT(*)" + join + where_sql, params).fetchone()[0]
    rows = conn.execute(
        "SELECT m.*, d.name AS driver_name, b.destination, b.start_at" + join + where_sql
        + " ORDER BY m.id DESC LIMIT :limit OFFSET :offset",
        {**params, "limit": page_size, "offset": (page - 1) * page_size},
    ).fetchall()
    failed = conn.execute("SELECT COUNT(*) FROM telegram_message WHERE status = 'failed'").fetchone()[0]
    items = [
        {
            "id": r["id"], "kind": r["kind"], "status": r["status"], "error_code": r["error_code"],
            "error_detail": r["error_detail"], "attempts": r["attempts"], "to_group": bool(r["to_group"]),
            "driver": {"id": r["driver_id"], "name": r["driver_name"]},
            "booking": {"id": r["booking_id"], "destination": r["destination"], "start_at": to_wib_iso(r["start_at"])},
            "created_at": to_wib_iso(r["created_at"]),
            "sent_at": to_wib_iso(r["sent_at"]) if r["sent_at"] else None,
        }
        for r in rows
    ]
    return {"items": items, "page": page, "page_size": page_size, "total": total, "failed_count": failed}
