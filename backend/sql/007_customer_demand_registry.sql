CREATE TABLE IF NOT EXISTS customer_demand (

    id SERIAL PRIMARY KEY,

    articolo TEXT NOT NULL,
    codice_articolo TEXT,

    quantita INTEGER,
    data_spedizione DATE,

    priorita_cliente TEXT,

    note TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cd_articolo
ON customer_demand(articolo);

CREATE INDEX IF NOT EXISTS idx_cd_data
ON customer_demand(data_spedizione);
