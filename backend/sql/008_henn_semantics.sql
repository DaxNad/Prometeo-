
CREATE TABLE IF NOT EXISTS henn_groups (
    articolo text,
    codice_henn text,
    sequenza integer,
    fonte text,
    note text
);


CREATE OR REPLACE VIEW vw_henn_group_load AS
SELECT
    hg.articolo,

    COUNT(*) AS henn_cycles,

    CASE
        WHEN COUNT(*) > 1 THEN 1
        ELSE 0
    END AS multi_cycle_flag,

    STRING_AGG(
        hg.codice_henn,
        ' | '
        ORDER BY hg.sequenza
    ) AS gruppi_henn

FROM henn_groups hg

GROUP BY hg.articolo;


CREATE OR REPLACE VIEW vw_tl_henn_board AS
SELECT

    v.articolo,

    v.henn_cycles,

    v.multi_cycle_flag,

    CASE
        WHEN v.henn_cycles >= 3 THEN 'CARICO_ALTO'
        WHEN v.henn_cycles = 2 THEN 'CARICO_MEDIO'
        ELSE 'CARICO_BASE'
    END AS classe_carico,

    CASE
        WHEN v.multi_cycle_flag = 1 THEN
            'VERIFICARE_CONTINUITA_HENN'
        ELSE
            'FLUSSO_STANDARD'
    END AS azione_tl,

    v.gruppi_henn

FROM vw_henn_group_load v;

