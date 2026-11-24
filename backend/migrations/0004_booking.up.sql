CREATE TABLE booking (
    id INTEGER PRIMARY KEY,
    driver_id INTEGER NOT NULL REFERENCES driver (id),
    requester_name TEXT NOT NULL CHECK (length(requester_name) BETWEEN 1 AND 100),
    division_id INTEGER NOT NULL REFERENCES division (id),
    destination TEXT NOT NULL CHECK (length(destination) BETWEEN 1 AND 200),
    notes TEXT CHECK (notes IS NULL OR length(notes) BETWEEN 1 AND 500),
    schedule_type TEXT NOT NULL CHECK (schedule_type IN ('per_jam', 'full_day')),
    start_at TEXT NOT NULL,
    end_at TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'active', 'completed', 'cancelled')),
    source TEXT NOT NULL DEFAULT 'web' CHECK (source IN ('web', 'telegram_group')),
    ack_at TEXT,
    completed_at TEXT,
    cancelled_at TEXT,
    created_by_admin_id INTEGER NOT NULL REFERENCES admin (id),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    CHECK (end_at > start_at)
);
CREATE INDEX booking_driver_status_start ON booking (driver_id, status, start_at);
CREATE INDEX booking_division ON booking (division_id);
CREATE INDEX booking_status_start ON booking (status, start_at);
CREATE INDEX booking_range ON booking (start_at, end_at);
CREATE INDEX booking_end ON booking (end_at);
