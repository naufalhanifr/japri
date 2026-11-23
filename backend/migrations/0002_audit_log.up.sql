-- actor_driver_id sengaja tanpa foreign key: tabel driver baru ada di langkah 4, dan baris audit harus tetap utuh.
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY,
    occurred_at TEXT NOT NULL,
    actor_type TEXT NOT NULL CHECK (actor_type IN ('admin', 'driver')),
    actor_admin_id INTEGER REFERENCES admin (id),
    actor_driver_id INTEGER,
    actor_label TEXT NOT NULL,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('booking', 'driver', 'driver_telegram_link')),
    entity_id INTEGER NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('create', 'update', 'cancel', 'complete', 'confirm', 'link', 'unlink')),
    before_json TEXT CHECK (before_json IS NULL OR json_valid(before_json)),
    after_json TEXT CHECK (after_json IS NULL OR json_valid(after_json)),
    changed_fields TEXT NOT NULL CHECK (json_valid(changed_fields)),
    CHECK (
        (actor_type = 'admin' AND actor_admin_id IS NOT NULL AND actor_driver_id IS NULL)
        OR (actor_type = 'driver' AND actor_driver_id IS NOT NULL AND actor_admin_id IS NULL)
    )
);
CREATE INDEX audit_log_entity ON audit_log (entity_type, entity_id, id);
CREATE INDEX audit_log_occurred_at ON audit_log (occurred_at);

CREATE TRIGGER audit_log_no_update BEFORE UPDATE ON audit_log
BEGIN
    SELECT RAISE(ABORT, 'audit_log tidak boleh diubah');
END;

CREATE TRIGGER audit_log_no_delete BEFORE DELETE ON audit_log
BEGIN
    SELECT RAISE(ABORT, 'audit_log tidak boleh dihapus');
END;
