
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



CREATE OR REPLACE VIEW vw_tl_zaw2_board AS
SELECT
    articolo,
    zaw2_cycles AS priorita_carico_zaw2,
    multi_cycle_flag,
    gruppi_unione,
    CASE
        WHEN zaw2_cycles >= 3 THEN 'CARICO_ALTO'
        WHEN zaw2_cycles = 2 THEN 'CARICO_MEDIO'
        ELSE 'CARICO_BASE'
    END AS classe_carico,
    CASE
        WHEN multi_cycle_flag = 1 THEN 'VALIDARE_CONTINUITA_MULTI_TURNO'
        ELSE 'GESTIONE_STANDARD'
    END AS azione_tl,
    'ZAW2_GROUP_UNION' AS origine_logica
FROM vw_zaw2_group_load
ORDER BY zaw2_cycles DESC, articolo;

COMMENT ON VIEW vw_tl_zaw2_board IS
'Board TL ZAW-2 con evidenza carico multi-unione e continuita multi-turno';
