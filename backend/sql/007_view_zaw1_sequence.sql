CREATE OR REPLACE VIEW vw_zaw1_sequence_suggestions AS

SELECT

    cur.codice_componente,

    cur.postazione_critica,

    ARRAY_AGG(
        DISTINCT cd.articolo
        ORDER BY cd.articolo
    ) AS sequenza_articoli,

    SUM(cd.quantita) AS volume_totale,

    COUNT(DISTINCT cd.articolo) AS numero_articoli,

    'RIDUZIONE_CAMBI_ZAW1' AS motivo

FROM component_usage_registry cur

JOIN customer_demand cd
ON cd.articolo = cur.articolo

WHERE cur.postazione_critica = 'ZAW-1'

GROUP BY
    cur.codice_componente,
    cur.postazione_critica

HAVING COUNT(DISTINCT cd.articolo) > 1;
