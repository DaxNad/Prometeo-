CREATE OR REPLACE VIEW vw_complessivi_stato AS
SELECT
    c.complessivo_articolo,
    array_agg(c.parziale_articolo ORDER BY c.sequenza_unione) AS parziali_previsti,
    count(c.parziale_articolo) AS numero_parziali
FROM bom_complessivi c
GROUP BY c.complessivo_articolo;
