class NullNotifier:
    """Titik panggil pesan ke driver. Backend 4/4 menggantinya dengan antrean pesan Telegram; di sini tidak mengirim apa pun."""

    def enqueue(self, conn, *, kind, booking_id, driver_id, now):
        return None
