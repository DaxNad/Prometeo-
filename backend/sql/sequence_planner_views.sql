DROP VIEW IF EXISTS vw_tl_zaw1_board;
DROP VIEW IF EXISTS vw_tl_zaw2_board;

CREATE VIEW vw_tl_zaw1_board AS
SELECT
    1 AS priorita_operativa,
    codice::text AS articolo,
    ''::text AS componenti_condivisi,
    qta AS quantita,
    CASE
        WHEN NULLIF(BTRIM(due_date), '') IS NULL THEN NULL::date
        WHEN BTRIM(due_date) ~ '^\d{4}-\d{2}-\d{2}$' THEN BTRIM(due_date)::date
        ELSE NULL::date
    END AS data_spedizione,
    CASE
        WHEN UPPER(BTRIM(semaforo)) = 'ROSSO' THEN 'ALTA'
        WHEN UPPER(BTRIM(semaforo)) = 'GIALLO' THEN 'MEDIA'
        WHEN UPPER(BTRIM(semaforo)) = 'VERDE' THEN 'BASSA'
        ELSE 'MEDIA'
    END::text AS priorita_cliente,
    codice::text AS complessivo_articolo,
    postazione::text AS postazione_critica,
    stato::text AS azione_tl,
    'board_state'::text AS origine_logica
FROM board_state
WHERE postazione = 'ZAW-1';

CREATE VIEW vw_tl_zaw2_board AS
SELECT
    1 AS priorita_operativa,
    codice::text AS articolo,
    ''::text AS componenti_condivisi,
    qta AS quantita,
    CASE
        WHEN NULLIF(BTRIM(due_date), '') IS NULL THEN NULL::date
        WHEN BTRIM(due_date) ~ '^\d{4}-\d{2}-\d{2}$' THEN BTRIM(due_date)::date
        ELSE NULL::date
    END AS data_spedizione,
    CASE
        WHEN UPPER(BTRIM(semaforo)) = 'ROSSO' THEN 'ALTA'
        WHEN UPPER(BTRIM(semaforo)) = 'GIALLO' THEN 'MEDIA'
        WHEN UPPER(BTRIM(semaforo)) = 'VERDE' THEN 'BASSA'
        ELSE 'MEDIA'
    END::text AS priorita_cliente,
    codice::text AS complessivo_articolo,
    postazione::text AS postazione_critica,
    stato::text AS azione_tl,
    'board_state'::text AS origine_logica
FROM board_state
WHERE postazione = 'ZAW-2';
