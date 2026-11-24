"""Teks pesan bot (user flow T1 sampai T6, TG1 sampai TG5). Semua teks HTML dengan nilai pengguna di-escape."""

from html import escape

from .timeutil import WIB, from_db

_DAYS = ("Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu")
_MONTHS = ("Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des")

FIELD_LABELS = {
    "requester_name": "Pemesan",
    "division_id": "Divisi",
    "destination": "Tujuan",
    "notes": "Catatan",
    "schedule_type": "Jenis jadwal",
    "start_at": "Jadwal",
    "end_at": "Jadwal",
}

LINK_OK = "Akun Anda terhubung sebagai {name}. Jadwal tugas akan dikirim ke sini. Setelah tugas selesai, kirim kata <b>Selesai</b>."
LINK_INVALID = "Kode atau tautan ini tidak berlaku. Minta admin membuat tautan baru."
LINK_NOT_LINKED = "Akun ini belum terhubung ke driver mana pun. Minta admin mengirim tautan atau kode untuk Anda."
LINK_ALREADY = "Akun Anda sudah terhubung sebagai {name}."
LINK_TAKEN = "Akun Telegram ini sudah terhubung ke driver lain."
HELP = "Kirim <b>Selesai</b> untuk menutup booking."
NONE_RUNNING = "Tidak ada booking yang sedang berjalan."
PICK = "Pilih booking yang sudah selesai:"
PICK_MORE = "Masih ada {n} booking berjalan lain. Selesaikan yang di atas dulu, lalu kirim Selesai lagi."
DONE = "Booking selesai: {what}. Terima kasih."
DONE_ALREADY = "Booking ini sudah {state}."
DONE_NOT_STARTED = "Booking ini belum berjalan."
DONE_UNKNOWN = "Booking tidak ditemukan."
FORMAT_HINT = (
    "Format: /{alias} tujuan; tanggal jam-mulai-jam-selesai; pemesan; Divisi; catatan (boleh kosong)\n"
    "Contoh: /{alias} Bandara Halim; 30 Okt 15:30-17:30; Maya; SDM"
)


def when(booking):
    start = from_db(booking["start_at"]).astimezone(WIB)
    end = from_db(booking["end_at"]).astimezone(WIB)
    full = booking["schedule_type"] == "full_day"
    if start.date() == end.date():
        label = f"{_DAYS[start.weekday()]}, {start.day} {_MONTHS[start.month - 1]}"
        hours = f"{start:%H:%M}–{end:%H:%M}"
        return f"{label} · Full day ({hours})" if full else f"{label} · {hours}"
    def one(dt):
        return f"{_DAYS[dt.weekday()][:3]} {dt.day} {_MONTHS[dt.month - 1]} {dt:%H:%M}"
    span = f"{one(start)} – {one(end)}"
    return f"Full day · {span}" if full else span


def _lines(title, booking, extra=()):
    lines = [f"<b>{title}</b>", escape(when(booking)), f"Pemesan: {escape(booking['requester_name'])} ({escape(booking['division_name'])})"]
    lines.append(f"Tujuan: {escape(booking['destination'])}")
    if booking["notes"]:
        lines.append(f"Catatan: {escape(booking['notes'])}")
    return "\n".join(lines + list(extra))


def private_text(kind, booking, changed=()):
    """Pesan ke chat pribadi driver (T2 sampai T5b). Tanpa nomor telepon driver."""
    if kind == "booking_created":
        return _lines("Jadwal baru", booking)
    if kind == "booking_cancelled":
        return _lines("Jadwal dibatalkan", booking)
    if kind == "booking_completed_by_admin":
        return _lines("Booking ditandai selesai oleh admin", booking)
    labels = list(dict.fromkeys(FIELD_LABELS[f] for f in changed if f in FIELD_LABELS))
    extra = [f"Berubah: {', '.join(labels)}"] if labels else []
    if booking["status"] == "completed":
        return _lines("Booking selesai diperbarui", booking, extra + ["Booking ini sudah berstatus Selesai."])
    return _lines("Jadwal diubah", booking, extra)


def mention(booking, telegram_user_id):
    name = escape(booking["driver_name"])
    return f'<a href="tg://user?id={int(telegram_user_id)}">{name}</a>' if telegram_user_id else name


def _group_summary(booking):
    text = f"{escape(when(booking))} · {escape(booking['destination'])}"
    return text


def group_text(kind, booking, telegram_user_id=None):
    """Pesan bot di grup (TG1, TG2, TG4, TG5)."""
    who = mention(booking, telegram_user_id)
    detail = f"{_group_summary(booking)} · Pemesan {escape(booking['requester_name'])} ({escape(booking['division_name'])})"
    if booking["notes"]:
        detail += f" · Catatan: {escape(booking['notes'])}"
    if kind == "booking_created":
        return f"Jadwal untuk {who}: {detail}. {who}, balas /oke untuk menerima."
    if kind == "booking_updated":
        return f"Jadwal diperbarui: {detail}. {who}, balas /oke untuk menerima."
    if kind == "booking_confirmed":
        return f"Dikonfirmasi oleh {escape(booking['driver_name'])}: {_group_summary(booking)}."
    return f"Dibatalkan oleh admin: {_group_summary(booking)} · {escape(booking['driver_name'])}."


def done_text(booking):
    return DONE.format(what=f"{escape(when(booking))} · {escape(booking['destination'])} · {escape(booking['requester_name'])}")


def button_label(booking):
    start = from_db(booking["start_at"]).astimezone(WIB)
    end = from_db(booking["end_at"]).astimezone(WIB)
    day = "" if start.date() == end.date() else f"{start.day} {_MONTHS[start.month - 1]} "
    return f"{day}{start:%H:%M}–{end:%H:%M} · {booking['destination']} · {booking['requester_name']}"[:60]
