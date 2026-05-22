CREATE TABLE IF NOT EXISTS controlled_import_audit_events (
    id BIGSERIAL PRIMARY KEY,
    audit_event_id TEXT NOT NULL UNIQUE,
    audit_event_type TEXT NOT NULL,
    actor TEXT NOT NULL,
    source TEXT NOT NULL,
    timestamp_utc TIMESTAMPTZ NOT NULL,
    preview_reference TEXT NOT NULL,
    dry_run_reference TEXT NOT NULL,
    confirmation_token_hash TEXT,
    strong_confirmation_status TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    write_mode TEXT NOT NULL,
    rollback_id TEXT NOT NULL,
    before_state_hash TEXT,
    before_state_ref TEXT,
    after_state_hash TEXT,
    after_state_ref TEXT,
    side_effects_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
    persistence_status TEXT NOT NULL,
    apply_allowed BOOLEAN NOT NULL DEFAULT FALSE,
    apply_executed BOOLEAN NOT NULL DEFAULT FALSE,
    failure_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT controlled_import_audit_risk_level_check
        CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'BLOCKED')),
    CONSTRAINT controlled_import_audit_write_mode_check
        CHECK (write_mode IN ('PREVIEW_ONLY', 'APPLY')),
    CONSTRAINT controlled_import_audit_confirmation_status_check
        CHECK (
            strong_confirmation_status IN (
                'NOT_REQUIRED_FOR_PREVIEW',
                'REQUIRED',
                'CONFIRMED',
                'MISSING',
                'INVALID'
            )
        ),
    CONSTRAINT controlled_import_audit_persistence_status_check
        CHECK (persistence_status IN ('PENDING', 'RECORDED', 'FAILED', 'BLOCKED')),
    CONSTRAINT controlled_import_audit_no_apply_without_confirmation_check
        CHECK (
            apply_executed = FALSE
            OR (
                apply_allowed = TRUE
                AND strong_confirmation_status = 'CONFIRMED'
                AND confirmation_token_hash IS NOT NULL
                AND rollback_id <> ''
            )
        )
);

CREATE INDEX IF NOT EXISTS idx_controlled_import_audit_event_id
    ON controlled_import_audit_events (audit_event_id);

CREATE INDEX IF NOT EXISTS idx_controlled_import_audit_rollback_id
    ON controlled_import_audit_events (rollback_id);

CREATE INDEX IF NOT EXISTS idx_controlled_import_audit_confirmation_token_hash
    ON controlled_import_audit_events (confirmation_token_hash);

CREATE INDEX IF NOT EXISTS idx_controlled_import_audit_timestamp_utc
    ON controlled_import_audit_events (timestamp_utc);
