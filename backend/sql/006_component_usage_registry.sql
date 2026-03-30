CREATE TABLE IF NOT EXISTS component_usage_registry (

    id SERIAL PRIMARY KEY,

    codice_componente TEXT NOT NULL,
    tipo_componente TEXT,
    famiglia_componente TEXT,

    articolo TEXT NOT NULL,
    codice_articolo TEXT,
    disegno TEXT,

    complessivo_articolo TEXT,

    fase TEXT,
    postazione_critica TEXT,

    quantita_per_articolo NUMERIC,

    condiviso BOOLEAN DEFAULT TRUE,
    criticita TEXT,
    note TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cur_codice_componente
ON component_usage_registry(codice_componente);

CREATE INDEX IF NOT EXISTS idx_cur_articolo
ON component_usage_registry(articolo);

CREATE INDEX IF NOT EXISTS idx_cur_complessivo
ON component_usage_registry(complessivo_articolo);
