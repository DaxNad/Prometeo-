CREATE OR REPLACE VIEW vw_tl_variant_alerts AS
SELECT
    s.articolo,
    s.famiglia_processo,
    COUNT(v.id) AS numero_varianti,
    STRING_AGG(v.codice_variante, ' | ' ORDER BY v.codice_variante) AS varianti,
    STRING_AGG(COALESCE(v.disegno_variante, '-'), ' | ' ORDER BY v.codice_variante) AS disegni_varianti,
    'CONFERMA_VARIANTE_PRIMA_AVVIO' AS alert_operativo
FROM bom_specs s
JOIN bom_variants v
  ON v.articolo = s.articolo
GROUP BY s.articolo, s.famiglia_processo
HAVING COUNT(v.id) > 1;
