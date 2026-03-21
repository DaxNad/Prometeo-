CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    line TEXT NOT NULL,
    station TEXT NOT NULL,
    event_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL,
    note TEXT,
    source TEXT,
    opened_at TIMESTAMP NOT NULL,
    closed_at TIMESTAMP NULL,
    closed_by TEXT NULL
);

CREATE INDEX IF NOT EXISTS idx_events_status ON events(status);
CREATE INDEX IF NOT EXISTS idx_events_line ON events(line);
CREATE INDEX IF NOT EXISTS idx_events_station ON events(station);
CREATE INDEX IF NOT EXISTS idx_events_opened_at ON events(opened_at DESC);
