CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status TEXT NOT NULL DEFAULT 'OPEN',
    title TEXT NOT NULL DEFAULT 'PROMETEO EVENT',
    area TEXT NOT NULL DEFAULT 'PROD',
    note TEXT NULL,
    code TEXT NULL,
    station TEXT NULL,
    shift TEXT NULL,
    closed_at TIMESTAMPTZ NULL,
    kind TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_events_ts_desc
    ON events (ts DESC);

CREATE INDEX IF NOT EXISTS idx_events_status
    ON events (status);

CREATE INDEX IF NOT EXISTS idx_events_kind
    ON events (kind);

CREATE INDEX IF NOT EXISTS idx_events_station
    ON events (station);

CREATE INDEX IF NOT EXISTS idx_events_code
    ON events (code);

CREATE INDEX IF NOT EXISTS idx_events_shift
    ON events (shift);

CREATE INDEX IF NOT EXISTS idx_events_closed_at
    ON events (closed_at);

CREATE INDEX IF NOT EXISTS idx_events_open_station
    ON events (station, ts DESC)
    WHERE status = 'OPEN';

CREATE INDEX IF NOT EXISTS idx_events_open_code
    ON events (code, ts DESC)
    WHERE status = 'OPEN';

CREATE INDEX IF NOT EXISTS idx_events_payload_gin
    ON events
    USING GIN (payload);

ALTER TABLE events
    DROP CONSTRAINT IF EXISTS chk_events_status;

ALTER TABLE events
    DROP CONSTRAINT IF EXISTS chk_events_shift;

ALTER TABLE events
    DROP CONSTRAINT IF EXISTS chk_events_kind;

ALTER TABLE events
    DROP CONSTRAINT IF EXISTS chk_events_station_format;

ALTER TABLE events
    DROP CONSTRAINT IF EXISTS chk_events_closed_logic;

ALTER TABLE events
    ADD CONSTRAINT chk_events_status
    CHECK (status IN ('OPEN', 'DONE'));

ALTER TABLE events
    ADD CONSTRAINT chk_events_shift
    CHECK (shift IS NULL OR shift IN ('MAT', 'POM', 'NOT'));

ALTER TABLE events
    ADD CONSTRAINT chk_events_kind
    CHECK (kind IN ('OPEN', 'DONE', 'ALERT', 'INFO', 'BLOCK', 'QUALITY', 'MAINT', 'SYSTEM'));

ALTER TABLE events
    ADD CONSTRAINT chk_events_station_format
    CHECK (
        station IS NULL
        OR station ~ '^[A-Z0-9]+(?:-[A-Z0-9]+)*$'
    );

ALTER TABLE events
    ADD CONSTRAINT chk_events_closed_logic
    CHECK (
        (status = 'OPEN' AND closed_at IS NULL)
        OR
        (status = 'DONE')
    );
