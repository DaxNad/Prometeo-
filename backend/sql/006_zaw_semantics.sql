/*
PROMETEO — ZAW SEMANTICS
version: v1
*/

CREATE TABLE IF NOT EXISTS zaw_groups (

    id SERIAL PRIMARY KEY,

    articolo TEXT NOT NULL,

    qc_code TEXT,
    oring_code TEXT,
    crt_code TEXT,

    numero_cicli NUMERIC DEFAULT 1,

    fonte TEXT,
    note TEXT,

    created_at TIMESTAMP DEFAULT NOW()

);


CREATE INDEX IF NOT EXISTS idx_zaw_groups_articolo
ON zaw_groups(articolo);



CREATE OR REPLACE VIEW vw_zaw_group_load AS

SELECT

    articolo,

    COUNT(*) AS zaw_cycles,

    COUNT(DISTINCT qc_code) AS qc_distinti,

    COUNT(DISTINCT crt_code) AS crt_distinti,

    STRING_AGG(

        qc_code || '+' || COALESCE(crt_code, 'NO_CRT'),

        ' | '

        ORDER BY qc_code, crt_code

    ) AS gruppi_zaw,

    CASE

        WHEN COUNT(*) > 1 THEN 1
        ELSE 0

    END AS multi_cycle_flag

FROM zaw_groups

GROUP BY articolo;



CREATE OR REPLACE VIEW vw_zaw1_sequence_ranked AS

WITH base AS (

    SELECT

        cur.codice_componente,
        cd.articolo,
        cd.quantita,
        cd.data_spedizione,
        cd.priorita_cliente,
        cur.complessivo_articolo,

        CASE

            WHEN upper(COALESCE(cd.priorita_cliente, '')) = 'ALTA' THEN 1
            WHEN upper(COALESCE(cd.priorita_cliente, '')) = 'MEDIA' THEN 2
            WHEN upper(COALESCE(cd.priorita_cliente, '')) = 'BASSA' THEN 3

            ELSE 9

        END AS priorita_rank

    FROM component_usage_registry cur

    JOIN customer_demand cd
        ON cd.articolo = cur.articolo

    WHERE cur.postazione_critica = 'ZAW-1'

),

component_clusters AS (

    SELECT

        base.codice_componente,

        array_agg(
            DISTINCT base.articolo
            ORDER BY base.articolo
        ) AS sequenza_articoli

    FROM base

    GROUP BY base.codice_componente

    HAVING COUNT(DISTINCT base.articolo) > 1

),

merged_clusters AS (

    SELECT

        string_agg(

            component_clusters.codice_componente,

            ' | '

            ORDER BY component_clusters.codice_componente

        ) AS componenti_driver,

        component_clusters.sequenza_articoli

    FROM component_clusters

    GROUP BY component_clusters.sequenza_articoli

),

article_level AS (

    SELECT

        base.articolo,

        MAX(base.quantita) AS quantita,

        MIN(base.data_spedizione) AS data_spedizione,

        MIN(base.priorita_rank) AS priorita_rank,

        CASE MIN(base.priorita_rank)

            WHEN 1 THEN 'ALTA'
            WHEN 2 THEN 'MEDIA'
            WHEN 3 THEN 'BASSA'

            ELSE NULL

        END AS priorita_cliente,

        MAX(
            COALESCE(base.complessivo_articolo, '-')
        ) AS complessivo_articolo

    FROM base

    GROUP BY base.articolo

),

expanded AS (

    SELECT

        mc.componenti_driver,

        a.articolo,
        a.quantita,
        a.data_spedizione,
        a.priorita_cliente,
        a.priorita_rank,

        a.complessivo_articolo,

        COALESCE(z.zaw_cycles, 1) AS zaw_cycles,

        COALESCE(z.multi_cycle_flag, 0) AS multi_cycle_flag,

        z.gruppi_zaw

    FROM merged_clusters mc

    JOIN article_level a

        ON a.articolo = ANY (
            mc.sequenza_articoli
        )

    LEFT JOIN vw_zaw_group_load z

        ON z.articolo = a.articolo

)

SELECT

    row_number()

        OVER (

            PARTITION BY componenti_driver

            ORDER BY

                data_spedizione,
                priorita_rank,

                zaw_cycles DESC,

                quantita DESC,

                articolo

        ) AS rank_suggerito,


    componenti_driver,

    articolo,

    quantita,

    data_spedizione,

    priorita_cliente,

    complessivo_articolo,

    'ZAW-1' AS postazione_critica,

    'SEQUENZA_OPERATIVA_CONSIGLIATA' AS tipo_output,


    zaw_cycles,

    multi_cycle_flag,

    gruppi_zaw


FROM expanded

ORDER BY componenti_driver, rank_suggerito;



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


    'ZAW1_CLUSTER_COMPONENTI' AS origine_logica,


    zaw_cycles,

    multi_cycle_flag,

    gruppi_zaw


FROM vw_zaw1_sequence_ranked

ORDER BY rank_suggerito;

