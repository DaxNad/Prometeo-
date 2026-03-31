ALTER TABLE bom_variants
    ADD COLUMN IF NOT EXISTS disegno_variante TEXT,
    ADD COLUMN IF NOT EXISTS nome_variante TEXT,
    ADD COLUMN IF NOT EXISTS mercato TEXT,
    ADD COLUMN IF NOT EXISTS cliente TEXT,
    ADD COLUMN IF NOT EXISTS stato_processo TEXT,
    ADD COLUMN IF NOT EXISTS marcatura_tubo_centro TEXT,
    ADD COLUMN IF NOT EXISTS file_assemblaggio TEXT,
    ADD COLUMN IF NOT EXISTS note TEXT,
    ADD COLUMN IF NOT EXISTS source_file TEXT,
    ADD COLUMN IF NOT EXISTS raw_json JSONB,
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

CREATE UNIQUE INDEX IF NOT EXISTS ux_bom_variants_articolo_codice_variante
ON bom_variants (articolo, codice_variante);

CREATE INDEX IF NOT EXISTS ix_bom_variants_articolo
ON bom_variants (articolo);

CREATE INDEX IF NOT EXISTS ix_bom_variants_disegno_variante
ON bom_variants (disegno_variante);
