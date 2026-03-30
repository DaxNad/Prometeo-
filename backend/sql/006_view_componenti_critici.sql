CREATE OR REPLACE VIEW vw_componenti_condivisi_critici AS
SELECT
    cur.codice_componente,
    cur.tipo_componente,
    cur.postazione_critica,
    COUNT(DISTINCT cur.articolo) AS numero_articoli,
    STRING_AGG(DISTINCT cur.articolo, ' | ' ORDER BY cur.articolo) AS articoli_collegati,
    STRING_AGG(DISTINCT COALESCE(cur.complessivo_articolo, '-'), ' | ' ORDER BY COALESCE(cur.complessivo_articolo, '-')) AS complessivi_collegati,
    MAX(cur.criticita) AS criticita,
    'VERIFICA_COMPONENTE_PRIMA_LANCIO' AS alert_operativo
FROM component_usage_registry cur
GROUP BY
    cur.codice_componente,
    cur.tipo_componente,
    cur.postazione_critica
HAVING COUNT(DISTINCT cur.articolo) > 1;
