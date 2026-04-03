CREATE OR REPLACE VIEW vw_zaw1_sequence_ranked AS
WITH base AS (
    SELECT
        cur.codice_componente,
        cur.articolo,
        cd.quantita,
        cd.data_spedizione,
        cd.priorita_cliente,
        cur.complessivo_articolo,
        CASE
            WHEN UPPER(COALESCE(cd.priorita_cliente, '')) = 'ALTA' THEN 1
            WHEN UPPER(COALESCE(cd.priorita_cliente, '')) = 'MEDIA' THEN 2
            WHEN UPPER(COALESCE(cd.priorita_cliente, '')) = 'BASSA' THEN 3
            ELSE 9
        END AS priorita_rank
    FROM component_usage_registry cur
    JOIN customer_demand cd
      ON cd.articolo = cur.articolo
    WHERE cur.postazione_critica = 'ZAW-1'
),
component_clusters AS (
    SELECT
        codice_componente,
        ARRAY_AGG(DISTINCT articolo ORDER BY articolo) AS sequenza_articoli,
        COUNT(DISTINCT articolo) AS numero_articoli_cluster
    FROM base
    GROUP BY codice_componente
),
merged_clusters AS (
    SELECT
        STRING_AGG(codice_componente, ' | ' ORDER BY codice_componente) AS componenti_driver,
        sequenza_articoli,
        MAX(numero_articoli_cluster) AS numero_articoli_cluster
    FROM component_clusters
    GROUP BY sequenza_articoli
),
article_level AS (
    SELECT
        articolo,
        MAX(quantita) AS quantita,
        MIN(data_spedizione) AS data_spedizione,
        MIN(priorita_rank) AS priorita_rank,
        CASE MIN(priorita_rank)
            WHEN 1 THEN 'ALTA'
            WHEN 2 THEN 'MEDIA'
            WHEN 3 THEN 'BASSA'
            ELSE NULL
        END AS priorita_cliente,
        MAX(COALESCE(complessivo_articolo, '-')) AS complessivo_articolo
    FROM base
    GROUP BY articolo
),
expanded AS (
    SELECT
        mc.componenti_driver,
        mc.numero_articoli_cluster,
        a.articolo,
        a.quantita,
        a.data_spedizione,
        a.priorita_cliente,
        a.priorita_rank,
        a.complessivo_articolo
    FROM merged_clusters mc
    JOIN article_level a
      ON a.articolo = ANY(mc.sequenza_articoli)
)
SELECT
    ROW_NUMBER() OVER (
        PARTITION BY componenti_driver
        ORDER BY
            data_spedizione ASC,
            priorita_rank ASC,
            quantita DESC,
            articolo ASC
    ) AS rank_suggerito,
    componenti_driver,
    articolo,
    quantita,
    data_spedizione,
    priorita_cliente,
    complessivo_articolo,
    'ZAW-1' AS postazione_critica,
    CASE
        WHEN numero_articoli_cluster > 1
        THEN 'SEQUENZA_OPERATIVA_CONDIVISA'
        ELSE 'SEQUENZA_OPERATIVA_SINGOLA'
    END AS tipo_output
FROM expanded
ORDER BY
    componenti_driver,
    rank_suggerito;
