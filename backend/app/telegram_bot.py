"""Pesan masuk dari Telegram (SA 6.2, 6.4, 6.6). Identitas selalu dari `from.id`, bukan dari isi pesan atau nama."""

import re
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta

from . import bookings, messages, telegram_link
from .audit import Actor
from .errors import AppError
from .timeutil import WIB

_COMMAND = re.compile(r"^/([A-Za-z0-9_]+)(?:@([A-Za-z0-9_]+))?(?:\s+(.*))?$", re.DOTALL)
_CODE = re.compile(r"^[A-Za-z0-9_-]{%d}$" % telegram_link.CODE_LENGTH)
_DONE_DATA = re.compile(r"^done:(\d{1,18})$")
_RESERVED = ("start", "selesai", "help", "oke")
_MAX_BUTTONS = 10
_MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "mei": 5, "jun": 6, "jul": 7, "agu": 8, "ags": 8, "agt": 8,
           "sep": 9, "okt": 10, "nov": 11, "des": 12}
_WHEN = re.compile(
    r"^(?P<d1>.+?)\s+(?P<t1>\d{1,2}[:.]\d{2})\s*(?:-|–|—|s/d|sampai)\s*(?:(?P<d2>.+?)\s+)?(?P<t2>\d{1,2}[:.]\d{2})$",
    re.IGNORECASE,
)
_BOOKING_ERRORS = {
    "booking_in_past": "Booking tidak bisa untuk tanggal yang sudah lewat.",
    "invalid_range": "Jam selesai harus setelah jam mulai.",
    "range_too_long": "Rentang booking maksimal 366 hari.",
}


@dataclass
class Context:
    conn: object
    settings: object
    now: object
    notifier: object
    out: list = field(default_factory=list)

    def send(self, chat_id, text, markup=None):
        self.out.append(("send", chat_id, text, markup))


class _Unreadable(Exception):
    pass


def handle_update(conn, settings, now, notifier, update):
    """Proses satu update. Hasilnya daftar balasan ("send", chat_id, teks, tombol) dan ("answer", id) untuk dikirim setelah commit."""
    ctx = Context(conn, settings, now, notifier)
    if isinstance(update.get("message"), dict):
        _message(ctx, update["message"])
    elif isinstance(update.get("callback_query"), dict):
        _callback(ctx, update["callback_query"])
    return ctx.out


def parse_command(text, bot_username):
    """(perintah huruf kecil, argumen). (None, None) bila bukan perintah atau ditujukan ke bot lain."""
    m = _COMMAND.match(text.strip())
    if not m:
        return None, None
    if m[2] and bot_username and m[2].lower() != bot_username.lower():
        return None, None
    return m[1].lower(), (m[3] or "").strip()


def _linked_driver(conn, user_id):
    return conn.execute(
        "SELECT d.id, d.name, l.telegram_chat_id, l.telegram_user_id FROM driver_telegram_link l "
        "JOIN driver d ON d.id = l.driver_id WHERE l.telegram_user_id = ?",
        (user_id,),
    ).fetchone()


def _obj(value):
    return value if isinstance(value, dict) else {}


def _message(ctx, msg):
    chat, sender = _obj(msg.get("chat")), _obj(msg.get("from"))
    if not isinstance(chat.get("id"), int) or not isinstance(sender.get("id"), int):
        return
    if not isinstance(msg.get("text"), str):
        return
    if chat.get("type") == "private":
        _private(ctx, msg, chat["id"], sender)
    elif chat.get("type") in ("group", "supergroup") and chat["id"] == ctx.settings.telegram_group_chat_id:
        _group(ctx, msg, chat["id"], sender["id"])


def _private(ctx, msg, chat_id, sender):
    text = msg["text"].strip()
    cmd, arg = parse_command(text, ctx.settings.telegram_bot_username)
    if text.startswith("/") and cmd is None:
        return
    driver = _linked_driver(ctx.conn, sender["id"])
    if cmd == "start":
        if arg:
            return _link(ctx, chat_id, sender, arg)
        ctx.send(chat_id, messages.LINK_ALREADY.format(name=driver["name"]) if driver else messages.LINK_NOT_LINKED)
    elif driver is None:
        if _CODE.match(text):
            _link(ctx, chat_id, sender, text)
    elif cmd == "selesai" or text.lower() == "selesai":
        _selesai(ctx, driver, chat_id)
    else:
        ctx.send(chat_id, messages.HELP)


def _link(ctx, chat_id, sender, code):
    name = " ".join(p for p in (sender.get("first_name"), sender.get("last_name")) if p) or "Telegram"
    result, driver_name = telegram_link.link_account(
        ctx.conn, ctx.now, code, chat_id, sender["id"], sender.get("username"), name
    )
    if result == "ok":
        ctx.send(chat_id, messages.LINK_OK.format(name=driver_name))
    else:
        ctx.send(chat_id, messages.LINK_TAKEN if result == "taken" else messages.LINK_INVALID)


def _selesai(ctx, driver, chat_id):
    rows = bookings.running_for_driver(ctx.conn, driver["id"], ctx.now)
    if not rows:
        ctx.send(chat_id, messages.NONE_RUNNING)
    elif len(rows) == 1:
        _close(ctx, driver, chat_id, rows[0]["id"])
    else:
        buttons = [[{"text": messages.button_label(r), "callback_data": f"done:{r['id']}"}] for r in rows[:_MAX_BUTTONS]]
        buttons.append([{"text": "Batal", "callback_data": "cancel"}])
        text = messages.PICK
        if len(rows) > _MAX_BUTTONS:
            text += "\n" + messages.PICK_MORE.format(n=len(rows) - _MAX_BUTTONS)
        ctx.send(chat_id, text, {"inline_keyboard": buttons})


def _close(ctx, driver, chat_id, booking_id):
    try:
        bookings.complete(
            ctx.conn, Actor.driver(driver["id"], driver["name"]), ctx.now, ctx.notifier, booking_id,
            owner_driver_id=driver["id"],
        )
    except AppError as exc:
        row = bookings._get(ctx.conn, booking_id) if exc.code != "not_found" else None
        if row is None:
            ctx.send(chat_id, messages.DONE_UNKNOWN)
        elif exc.code == "booking_not_started":
            ctx.send(chat_id, messages.DONE_NOT_STARTED)
        else:
            state = {"completed": "Selesai", "cancelled": "Dibatalkan"}.get(row["status"], "belum dikonfirmasi")
            ctx.send(chat_id, messages.DONE_ALREADY.format(state=state))
        return
    ctx.send(chat_id, messages.done_text(bookings._get(ctx.conn, booking_id)))


def _callback(ctx, query):
    ctx.out.append(("answer", query.get("id")))
    sender, message = _obj(query.get("from")), _obj(query.get("message"))
    chat_id = _obj(message.get("chat")).get("id")
    if not isinstance(sender.get("id"), int):
        return
    driver = _linked_driver(ctx.conn, sender["id"])
    if driver is None or chat_id != driver["telegram_chat_id"]:
        return
    data = query.get("data")
    m = _DONE_DATA.match(data) if isinstance(data, str) else None
    if m:
        _close(ctx, driver, chat_id, int(m[1]))


def _group(ctx, msg, chat_id, user_id):
    cmd, arg = parse_command(msg["text"], ctx.settings.telegram_bot_username)
    if cmd is None:
        return
    if cmd == "oke":
        return _oke(ctx, msg, chat_id, user_id)
    if cmd in _RESERVED:
        return
    admin = ctx.conn.execute(
        "SELECT id, email FROM admin WHERE telegram_user_id = ? AND is_active = 1", (user_id,)
    ).fetchone()
    if admin is None:
        return
    driver = ctx.conn.execute(
        "SELECT d.id, d.name, d.is_active, d.is_on_leave, l.driver_id AS linked FROM driver d "
        "LEFT JOIN driver_telegram_link l ON l.driver_id = d.id WHERE d.command_alias = ?",
        (cmd,),
    ).fetchone()
    if driver is None:
        return ctx.send(chat_id, "Kode driver tidak dikenal.")
    if not driver["is_active"] or driver["is_on_leave"]:
        return ctx.send(chat_id, f"{_esc(driver['name'])} tidak bisa dibooking (nonaktif atau sedang cuti).")
    if driver["linked"] is None:
        return ctx.send(chat_id, f"{_esc(driver['name'])} belum terhubung ke Telegram, belum bisa menerima booking dari grup.")
    hint = messages.FORMAT_HINT.format(alias=cmd)
    try:
        data = _parse_booking(ctx, arg, driver["id"])
    except _Unreadable as exc:
        return ctx.send(chat_id, f"{_esc(str(exc))}\n{_esc(hint)}")
    try:
        bookings.create(
            ctx.conn, Actor.admin(admin["id"], admin["email"]), ctx.now, ctx.notifier, data,
            status="pending", source="telegram_group",
        )
    except AppError as exc:
        ctx.send(chat_id, f"{_esc(_BOOKING_ERRORS.get(exc.code, exc.message))}\n{_esc(hint)}")


def _esc(text):
    return messages.escape(text)


def _parse_booking(ctx, arg, driver_id):
    parts = [p.strip() for p in arg.split(";")]
    missing = [label for label, value in zip(("tujuan", "waktu", "pemesan", "Divisi"), parts + [""] * 4) if not value]
    if missing:
        raise _Unreadable("Data kurang: " + ", ".join(missing) + ".")
    destination, when, requester, division, notes = parts[0], parts[1], parts[2], parts[3], ";".join(parts[4:]).strip()
    if len(destination) > 200 or len(requester) > 100 or len(notes) > 500:
        raise _Unreadable("Tujuan maksimal 200 karakter, pemesan 100, catatan 500.")
    row = ctx.conn.execute(
        "SELECT id FROM division WHERE is_active = 1 AND lower(name) = lower(?)", (division,)
    ).fetchone()
    if row is None:
        names = [r["name"] for r in ctx.conn.execute("SELECT name FROM division WHERE is_active = 1 ORDER BY sort_order, name")]
        raise _Unreadable("Divisi tidak dikenal. Pilihan: " + ", ".join(names) + ".")
    start_date, start_time, end_date, end_time = _parse_when(when, ctx.now.astimezone(WIB).date())
    return {
        "driver_id": driver_id, "requester_name": requester, "division_id": row["id"], "destination": destination,
        "notes": notes or None, "schedule_type": "per_jam", "start_date": start_date, "end_date": end_date,
        "start_time": start_time, "end_time": end_time,
    }


def _parse_when(text, today):
    m = _WHEN.match(text.strip())
    if not m:
        raise _Unreadable("Tanggal dan jam tidak terbaca.")
    start_date = _parse_date(m["d1"], today)
    end_date = _parse_date(m["d2"], today) if m["d2"] else start_date
    return start_date, _parse_time(m["t1"]), end_date, _parse_time(m["t2"])


def _parse_time(text):
    hour, minute = re.split(r"[:.]", text)
    try:
        return time(int(hour), int(minute))
    except ValueError:
        raise _Unreadable("Jam tidak terbaca.") from None


def _parse_date(text, today):
    text = " ".join(text.lower().replace(",", " ").split())
    offsets = {"hari ini": 0, "besok": 1, "lusa": 2}
    try:
        if text in offsets:
            return today + timedelta(days=offsets[text])
        if m := re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", text):
            return date(int(m[1]), int(m[2]), int(m[3]))
        if m := re.fullmatch(r"(\d{1,2})/(\d{1,2})(?:/(\d{4}))?", text):
            return date(int(m[3] or today.year), int(m[2]), int(m[1]))
        if (m := re.fullmatch(r"(\d{1,2}) ([a-z]+)\.?(?: (\d{4}))?", text)) and m[2][:3] in _MONTHS:
            return date(int(m[3] or today.year), _MONTHS[m[2][:3]], int(m[1]))
    except ValueError:
        pass
    raise _Unreadable("Tanggal tidak terbaca.")


def _oke(ctx, msg, chat_id, user_id):
    driver = _linked_driver(ctx.conn, user_id)
    if driver is None:
        return
    booking = None
    replied = _obj(msg.get("reply_to_message")).get("message_id")
    if replied is not None:
        hit = ctx.conn.execute(
            "SELECT booking_id FROM telegram_message WHERE to_group = 1 AND chat_id = ? AND telegram_message_id = ? "
            "AND kind IN ('booking_created', 'booking_updated')",
            (chat_id, replied),
        ).fetchone()
        if hit:
            booking = bookings._get(ctx.conn, hit["booking_id"])
    if booking is None:
        pending = ctx.conn.execute(
            "SELECT id FROM booking WHERE driver_id = ? AND status = 'pending' ORDER BY id", (driver["id"],)
        ).fetchall()
        if not pending:
            return ctx.send(chat_id, "Tidak ada booking yang menunggu konfirmasi.")
        if len(pending) > 1:
            return ctx.send(chat_id, "Balas pesan booking yang dimaksud dengan /oke.")
        booking = bookings._get(ctx.conn, pending[0]["id"])
    if booking["driver_id"] != driver["id"]:
        return
    if booking["status"] == "cancelled":
        return ctx.send(chat_id, "Booking ini sudah dibatalkan.")
    try:
        bookings.confirm(ctx.conn, Actor.driver(driver["id"], driver["name"]), ctx.now, ctx.notifier, booking["id"])
    except AppError:
        ctx.send(chat_id, "Booking ini sudah dikonfirmasi.")
