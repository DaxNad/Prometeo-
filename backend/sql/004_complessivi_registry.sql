CREATE TABLE IF NOT EXISTS bom_complessivi (

    id SERIAL PRIMARY KEY,

    complessivo_articolo TEXT NOT NULL,
    complessivo_codice TEXT,
    complessivo_disegno TEXT,

    parziale_articolo TEXT NOT NULL,
    parziale_codice TEXT,
    parziale_disegno TEXT,

    ruolo_parziale TEXT,
    sequenza_unione INTEGER,
    postazione_unione TEXT,

    obbligatorio BOOLEAN DEFAULT TRUE,
    note TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

CREATE INDEX IF NOT EXISTS idx_complessivo_articolo
ON bom_complessivi(complessivo_articolo);

CREATE INDEX IF NOT EXISTS idx_parziale_articolo
ON bom_complessivi(parziale_articolo);
