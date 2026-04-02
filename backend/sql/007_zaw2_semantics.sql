
/*
PROMETEO — ZAW2 SEMANTICS
unione semilavorati
1 gruppo giunzione = 1 ciclo macchina reale
*/


CREATE TABLE IF NOT EXISTS zaw2_groups (

    id SERIAL PRIMARY KEY,

    articolo TEXT NOT NULL,

    gruppo_unione TEXT,

    componente_padre TEXT,
    componente_figlio TEXT,

    numero_cicli NUMERIC DEFAULT 1,

    sequenza INTEGER,

    fonte TEXT,
    note TEXT,

    created_at TIMESTAMP DEFAULT NOW()

);


CREATE INDEX IF NOT EXISTS idx_zaw2_groups_articolo
ON zaw2_groups(articolo);



CREATE OR REPLACE VIEW vw_zaw2_group_load AS

SELECT

    articolo,

    COUNT(*) AS zaw2_cycles,

    STRING_AGG(
        gruppo_unione,
        ' | '
        ORDER BY sequenza
    ) AS gruppi_unione,

    CASE
        WHEN COUNT(*) > 1 THEN 1
        ELSE 0
    END AS multi_cycle_flag

FROM zaw2_groups

GROUP BY articolo;



COMMENT ON VIEW vw_zaw2_group_load IS
'numero cicli reali ZAW-2 basati su unioni semilavorati';


