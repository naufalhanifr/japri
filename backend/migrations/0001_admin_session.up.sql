CREATE TABLE admin (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE CHECK (email = lower(email) AND length(email) BETWEEN 3 AND 254),
    password_hash TEXT NOT NULL,
    display_name TEXT NOT NULL CHECK (length(display_name) BETWEEN 1 AND 100),
    telegram_user_id INTEGER UNIQUE,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TEXT NOT NULL
);

CREATE TABLE session (
    token_hash TEXT PRIMARY KEY,
    admin_id INTEGER NOT NULL REFERENCES admin (id),
    csrf_token TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    ip TEXT,
    user_agent TEXT
);
CREATE INDEX session_expires_at ON session (expires_at);
CREATE INDEX session_admin_id ON session (admin_id);

CREATE TABLE login_attempt (
    id INTEGER PRIMARY KEY,
    email_norm TEXT NOT NULL,
    ip TEXT NOT NULL,
    attempted_at TEXT NOT NULL,
    success INTEGER NOT NULL CHECK (success IN (0, 1))
);
CREATE INDEX login_attempt_email ON login_attempt (email_norm, attempted_at);
CREATE INDEX login_attempt_ip ON login_attempt (ip, attempted_at);
