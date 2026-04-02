CREATE OR REPLACE VIEW vw_machine_load_summary AS

WITH parsed AS (

    SELECT
        articolo,
        postazione_critica,

        COALESCE(
            NULLIF(
                regexp_replace(note, '.*ZAW1_CYCLES=([0-9]+).*', '\1'),
                note
            )::numeric,
            0
        ) AS zaw1_cycles,

        COALESCE(
            NULLIF(
                regexp_replace(note, '.*ZAW2_CYCLES=([0-9]+).*', '\1'),
                note
            )::numeric,
            0
        ) AS zaw2_cycles,

        COALESCE(
            NULLIF(
                regexp_replace(note, '.*HENN_CYCLES=([0-9]+).*', '\1'),
                note
            )::numeric,
            0
        ) AS henn_cycles,

        COALESCE(
            NULLIF(
                regexp_replace(note, '.*PIDMILL_CYCLES=([0-9]+).*', '\1'),
                note
            )::numeric,
            0
        ) AS pidmill_cycles

    FROM component_usage_registry
    WHERE postazione_critica IS NOT NULL
),

normalized AS (

    SELECT articolo, 'ZAW-1' AS station, MAX(zaw1_cycles) AS total_cycles
    FROM parsed
    WHERE zaw1_cycles > 0
    GROUP BY articolo

    UNION ALL

    SELECT articolo, 'ZAW-2' AS station, MAX(zaw2_cycles) AS total_cycles
    FROM parsed
    WHERE zaw2_cycles > 0
    GROUP BY articolo

    UNION ALL

    SELECT articolo, 'HENN' AS station, MAX(henn_cycles) AS total_cycles
    FROM parsed
    WHERE henn_cycles > 0
    GROUP BY articolo

    UNION ALL

    SELECT articolo, 'PIDMILL' AS station, MAX(pidmill_cycles) AS total_cycles
    FROM parsed
    WHERE pidmill_cycles > 0
    GROUP BY articolo

)

SELECT
    articolo,
    station,
    total_cycles
FROM normalized
ORDER BY station, articolo;
