
CREATE TABLE IF NOT EXISTS pidmill_groups (
    articolo text,
    codice_pidmill text,
    sequenza integer,
    anticipabile integer default 0,
    fonte text,
    note text
);


CREATE OR REPLACE VIEW vw_pidmill_group_load AS
SELECT

    pg.articolo,

    COUNT(*) AS pidmill_cycles,

    CASE
        WHEN COUNT(*) > 1 THEN 1
        ELSE 0
    END AS multi_cycle_flag,

    MAX(pg.anticipabile) AS anticipabile_flag,

    STRING_AGG(
        pg.codice_pidmill,
        ' | '
        ORDER BY pg.sequenza
    ) AS gruppi_pidmill

FROM pidmill_groups pg

GROUP BY pg.articolo;



CREATE OR REPLACE VIEW vw_tl_pidmill_board AS
SELECT

    v.articolo,

    v.pidmill_cycles,

    v.multi_cycle_flag,

    v.anticipabile_flag,

    CASE
        WHEN v.pidmill_cycles >= 3 THEN 'CARICO_ALTO'
        WHEN v.pidmill_cycles = 2 THEN 'CARICO_MEDIO'
        ELSE 'CARICO_BASE'
    END AS classe_carico,

    CASE
        WHEN v.anticipabile_flag = 1 THEN
            'OPERAZIONE_ANTICIPABILE'
        WHEN v.multi_cycle_flag = 1 THEN
            'VERIFICARE_CONTINUITA_MULTI_TURNO'
        ELSE
            'FLUSSO_STANDARD'
    END AS azione_tl,

    v.gruppi_pidmill

FROM vw_pidmill_group_load v;

