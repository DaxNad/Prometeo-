CREATE OR REPLACE VIEW vw_zaw1_sequence_tl AS
WITH base AS (
    SELECT
        cur.codice_componente,
        cd.articolo,
        cd.quantita,
        cd.data_spedizione,
        cd.priorita_cliente
    FROM component_usage_registry cur
    JOIN customer_demand cd
      ON cd.articolo = cur.articolo
    WHERE cur.postazione_critica = 'ZAW-1'
),
component_clusters AS (
    SELECT
        codice_componente,
        ARRAY_AGG(DISTINCT articolo ORDER BY articolo) AS sequenza_articoli,
        SUM(quantita) AS volume_totale,
        COUNT(DISTINCT articolo) AS numero_articoli,
        MIN(data_spedizione) AS prima_spedizione
    FROM base
    GROUP BY codice_componente
    HAVING COUNT(DISTINCT articolo) > 1
),
merged AS (
    SELECT
        STRING_AGG(codice_componente, ' | ' ORDER BY codice_componente) AS componenti_driver,
        sequenza_articoli,
        MAX(volume_totale) AS volume_totale,
        MAX(numero_articoli) AS numero_articoli,
        MIN(prima_spedizione) AS prima_spedizione
    FROM component_clusters
    GROUP BY sequenza_articoli
)
SELECT
    sequenza_articoli,
    volume_totale,
    numero_articoli,
    componenti_driver,
    prima_spedizione,
    'PROPOSTA_CLUSTER_ZAW1' AS tipo_output,
    'VALIDARE_SEQUENZA_PRIMA_AVVIO' AS azione_tl
FROM merged
ORDER BY prima_spedizione, volume_totale DESC;
