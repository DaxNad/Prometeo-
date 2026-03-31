CREATE TABLE IF NOT EXISTS bom_variants (
    id BIGSERIAL PRIMARY KEY,
    articolo TEXT NOT NULL,
    codice_variante TEXT NOT NULL,
    disegno_variante TEXT,
    nome_variante TEXT,
    mercato TEXT,
    cliente TEXT,
    stato_processo TEXT,
    marcatura_tubo_centro TEXT,
    file_assemblaggio TEXT,
    note TEXT,
    source_file TEXT,
    raw_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_bom_variants_articolo_codice_variante
ON bom_variants (articolo, codice_variante);

CREATE INDEX IF NOT EXISTS ix_bom_variants_articolo
ON bom_variants (articolo);

CREATE INDEX IF NOT EXISTS ix_bom_variants_disegno_variante
ON bom_variants (disegno_variante);
