CREATE TABLE IF NOT EXISTS bom_specs (
    id BIGSERIAL PRIMARY KEY,
    articolo TEXT NOT NULL UNIQUE,
    codice_articolo TEXT,
    disegno TEXT,
    rev TEXT,
    documento_tipo TEXT,
    data_sba TEXT,
    qta_lotto INTEGER,
    qta_imballo INTEGER,
    codice_imballo TEXT,
    cluster_name TEXT,
    famiglia_processo TEXT,
    cp_required BOOLEAN,
    cp_note TEXT,
    source_file TEXT,
    raw_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bom_components (
    id BIGSERIAL PRIMARY KEY,
    articolo TEXT NOT NULL,
    parent_articolo TEXT,
    codice_componente TEXT,
    tipo TEXT,
    ruolo TEXT,
    quantita NUMERIC(12,2),
    lunghezza_mm NUMERIC(12,2),
    postazione TEXT,
    tooling TEXT,
    note TEXT,
    extra JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS bom_operations (
    id BIGSERIAL PRIMARY KEY,
    articolo TEXT NOT NULL,
    seq_no INTEGER NOT NULL,
    fase TEXT NOT NULL,
    famiglia_operazione TEXT,
    materiale_riferimento TEXT,
    tooling TEXT,
    macchina TEXT,
    solo_per TEXT,
    note TEXT,
    extra JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS bom_markings (
    id BIGSERIAL PRIMARY KEY,
    articolo TEXT NOT NULL,
    seq_no INTEGER,
    tipo TEXT,
    valore TEXT,
    posizione TEXT,
    dettaglio TEXT,
    codice_riferimento TEXT,
    note TEXT,
    extra JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS bom_controls (
    id BIGSERIAL PRIMARY KEY,
    articolo TEXT NOT NULL,
    seq_no INTEGER,
    fase TEXT,
    tipo TEXT,
    obbligatorio BOOLEAN,
    campionamento TEXT,
    vincolo TEXT,
    note TEXT,
    extra JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS bom_variants (
    id BIGSERIAL PRIMARY KEY,
    articolo TEXT NOT NULL,
    codice_variante TEXT,
    chiave TEXT NOT NULL,
    valore TEXT,
    extra JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_bom_specs_articolo
ON bom_specs(articolo);

CREATE INDEX IF NOT EXISTS idx_bom_specs_famiglia
ON bom_specs(famiglia_processo);

CREATE INDEX IF NOT EXISTS idx_bom_components_articolo
ON bom_components(articolo);

CREATE INDEX IF NOT EXISTS idx_bom_components_codice
ON bom_components(codice_componente);

CREATE INDEX IF NOT EXISTS idx_bom_operations_articolo
ON bom_operations(articolo);

CREATE INDEX IF NOT EXISTS idx_bom_operations_fase
ON bom_operations(fase);

CREATE INDEX IF NOT EXISTS idx_bom_markings_articolo
ON bom_markings(articolo);

CREATE INDEX IF NOT EXISTS idx_bom_controls_articolo
ON bom_controls(articolo);

CREATE INDEX IF NOT EXISTS idx_bom_variants_articolo
ON bom_variants(articolo);
