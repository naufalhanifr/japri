CREATE TABLE telegram_link_token (
    id INTEGER PRIMARY KEY,
    driver_id INTEGER NOT NULL REFERENCES driver (id),
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TEXT NOT NULL,
    used_at TEXT,
    created_by_admin_id INTEGER NOT NULL REFERENCES admin (id),
    created_at TEXT NOT NULL
);
CREATE INDEX telegram_link_token_driver ON telegram_link_token (driver_id);

-- Antrean sekaligus log kirim. Tanpa coba ulang otomatis (keputusan PO M4): satu percobaan, hasilnya sent atau failed.
-- skipped: pesan jadwal baru atau diubah yang belum terkirim ketika booking-nya sudah dibatalkan.
CREATE TABLE telegram_message (
    id INTEGER PRIMARY KEY,
    driver_id INTEGER NOT NULL REFERENCES driver (id),
    booking_id INTEGER NOT NULL REFERENCES booking (id),
    kind TEXT NOT NULL CHECK (kind IN (
        'booking_created', 'booking_updated', 'booking_cancelled', 'booking_completed_by_admin', 'booking_confirmed'
    )),
    to_group INTEGER NOT NULL DEFAULT 0 CHECK (to_group IN (0, 1)),
    chat_id INTEGER,
    text TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'sent', 'failed', 'skipped')),
    attempts INTEGER NOT NULL DEFAULT 0,
    error_code TEXT,
    error_detail TEXT,
    telegram_message_id INTEGER,
    created_at TEXT NOT NULL,
    sent_at TEXT
);
CREATE INDEX telegram_message_status ON telegram_message (status, id);
CREATE INDEX telegram_message_driver ON telegram_message (driver_id, id);
CREATE INDEX telegram_message_booking ON telegram_message (booking_id, id);
CREATE INDEX telegram_message_sent ON telegram_message (chat_id, telegram_message_id);

CREATE TABLE telegram_update (
    update_id INTEGER PRIMARY KEY,
    received_at TEXT NOT NULL
);
CREATE INDEX telegram_update_received ON telegram_update (received_at);
