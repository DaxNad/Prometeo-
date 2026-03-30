CREATE OR REPLACE VIEW vw_zaw1_component_load AS

SELECT

    cur.codice_componente,

    cur.postazione_critica,

    COUNT(DISTINCT cd.articolo) AS numero_articoli_coinvolti,

    SUM(cd.quantita) AS domanda_totale,

    STRING_AGG(
        cd.articolo || ':' || cd.quantita,
        ' | ' ORDER BY cd.articolo
    ) AS dettaglio_domanda

FROM component_usage_registry cur

JOIN customer_demand cd
ON cd.articolo = cur.articolo

WHERE cur.postazione_critica = 'ZAW-1'

GROUP BY
    cur.codice_componente,
    cur.postazione_critica;
