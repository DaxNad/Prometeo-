CREATE OR REPLACE VIEW vw_tl_zaw2_board AS
SELECT
    rank_suggerito AS priorita_operativa,
    articolo,
    disegno,
    componenti_driver AS componenti_condivisi,
    quantita,
    data_spedizione,
    priorita_cliente,
    complessivo_articolo,
    postazione_critica,
    CASE
        WHEN rank_suggerito = 1
        THEN 'AVVIO_IMMEDIATO'
        WHEN rank_suggerito <= 3
        THEN 'PREPARARE_CAMBIO_SERIE'
        ELSE 'PIANIFICARE'
    END AS azione_tl,
    'ZAW2_CLUSTER_COMPONENTI' AS origine_logica
FROM vw_zaw2_sequence_ranked
ORDER BY priorita_operativa;
