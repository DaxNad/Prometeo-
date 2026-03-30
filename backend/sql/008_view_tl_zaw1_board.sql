CREATE OR REPLACE VIEW vw_tl_zaw1_board AS
SELECT
    rank_suggerito AS priorita_operativa,

    articolo,

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

    'ZAW1_CLUSTER_COMPONENTI' AS origine_logica

FROM vw_zaw1_sequence_ranked

ORDER BY
    priorita_operativa;
