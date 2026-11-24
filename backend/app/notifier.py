from . import bookings, messages
from .timeutil import to_db

_GROUP_KINDS = ("booking_created", "booking_updated", "booking_cancelled")


class NullNotifier:
    """Tidak mengirim apa pun. Dipakai tes yang tidak menguji pesan; aplikasi memakai OutboxNotifier."""

    def enqueue(self, conn, *, kind, booking_id, driver_id, now, changed=None, before=None):
        return None


class OutboxNotifier:
    """Menulis baris `telegram_message` di transaksi yang sama dengan perubahan booking. Pengiriman oleh worker."""

    def __init__(self, settings):
        self.group_chat_id = settings.telegram_group_chat_id

    def enqueue(self, conn, *, kind, booking_id, driver_id, now, changed=None, before=None):
        """Mengembalikan {status, error_code} pesan yang dicatat, atau None bila tidak ada yang dikirim.

        `before`: isi booking sebelum diedit, dipakai pesan pembatalan ke driver lama agar menyebut jadwal yang dulu.
        """
        row = bookings._get(conn, booking_id)
        if before:
            row = {**dict(row), **before, "division_name": conn.execute(
                "SELECT name FROM division WHERE id = ?", (before["division_id"],)).fetchone()[0]}
        link = conn.execute(
            "SELECT telegram_chat_id, telegram_user_id FROM driver_telegram_link WHERE driver_id = ?", (driver_id,)
        ).fetchone()
        to_group = kind == "booking_confirmed" or (
            kind in _GROUP_KINDS and row["source"] == "telegram_group" and row["ack_at"] is None
        )
        if to_group:
            # Ganti driver pada booking yang belum dikonfirmasi: pengumuman baru untuk driver baru sudah cukup.
            if kind == "booking_cancelled" and driver_id != row["driver_id"]:
                return None
            text = messages.group_text(kind, row, link["telegram_user_id"] if link else None)
            chat_id, error = self.group_chat_id, "group_not_set"
        else:
            text = messages.private_text(kind, row, changed or ())
            chat_id, error = (link["telegram_chat_id"] if link else None), "not_linked"
        status, error_code = ("pending", None) if chat_id is not None else ("failed", error)
        conn.execute(
            "INSERT INTO telegram_message (driver_id, booking_id, kind, to_group, chat_id, text, status, error_code, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (driver_id, booking_id, kind, int(to_group), chat_id, text, status, error_code, to_db(now)),
        )
        return {"status": status, "error_code": error_code}
