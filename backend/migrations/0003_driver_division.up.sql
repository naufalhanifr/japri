CREATE TABLE driver (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(name) BETWEEN 1 AND 100),
    phone TEXT NOT NULL,
    vehicle_type TEXT NOT NULL CHECK (length(vehicle_type) BETWEEN 1 AND 50),
    vehicle_plate TEXT NOT NULL CHECK (length(vehicle_plate) BETWEEN 1 AND 15),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    is_on_leave INTEGER NOT NULL DEFAULT 0 CHECK (is_on_leave IN (0, 1)),
    command_alias TEXT NOT NULL UNIQUE CHECK (length(command_alias) BETWEEN 1 AND 32),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE division (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE CHECK (length(name) BETWEEN 1 AND 100),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    sort_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE driver_telegram_link (
    driver_id INTEGER PRIMARY KEY REFERENCES driver (id),
    telegram_chat_id INTEGER NOT NULL UNIQUE,
    telegram_user_id INTEGER NOT NULL,
    telegram_username TEXT,
    telegram_name TEXT NOT NULL,
    linked_at TEXT NOT NULL
);
