from __future__ import annotations

import os

from sqlalchemy import create_engine, text


SQL = """
DELETE FROM component_usage_registry;

INSERT INTO component_usage_registry (
    codice_componente,
    articolo,
    codice_articolo,
    disegno,
    complessivo_articolo,
    fase,
    postazione_critica,
    quantita_per_articolo,
    condiviso,
    note
)
SELECT
    bc.codice_componente,
    bc.articolo,
    bc.articolo,
    NULL,
    bc.parent_articolo,
    COALESCE(bc.ruolo, bc.postazione),

    CASE

        WHEN bc.postazione IN ('ZAW1', 'ZAW-1', 'ZAW 1') THEN 'ZAW-1'
        WHEN z1.articolo IS NOT NULL
             AND (
                 bc.codice_componente = '468796'
                 OR bc.codice_componente = ANY (
                     string_to_array(
                         replace(replace(COALESCE(z1.gruppi_zaw, ''), ' | ', '+'), '+', ','),
                         ','
                     )
                 )
             )
        THEN 'ZAW-1'

        WHEN bc.postazione IN ('ZAW2', 'ZAW-2', 'ZAW 2') THEN 'ZAW-2'
        WHEN z2.articolo IS NOT NULL THEN 'ZAW-2'

        WHEN bc.postazione ILIKE '%HENN%' THEN 'HENN'
        WHEN h.articolo IS NOT NULL
             AND (
                 bc.codice_componente IN ('469122','469124')
                 OR bc.codice_componente = ANY (
                     string_to_array(
                         replace(COALESCE(h.gruppi_henn, ''), ' | ', ','),
                         ','
                     )
                 )
             )
        THEN 'HENN'

        WHEN bc.postazione ILIKE '%PIDMILL%' THEN 'PIDMILL'
        WHEN p.articolo IS NOT NULL THEN 'PIDMILL'

        WHEN bc.postazione ILIKE '%ULTRASUONI%' THEN 'ULTRASUONI'

        ELSE NULL

    END AS postazione_critica,


    COALESCE(bc.quantita::numeric, 1),

    TRUE,


    CASE

        WHEN (
            bc.postazione IN ('ZAW1', 'ZAW-1', 'ZAW 1')
            OR z1.articolo IS NOT NULL
        )
        THEN CONCAT_WS(
            ' | ',
            bc.note,
            'ZAW1_CYCLES=' || z1.zaw_cycles,
            'ZAW1_MULTI=' || z1.multi_cycle_flag,
            'ZAW1_GROUPS=' || z1.gruppi_zaw
        )


        WHEN (
            bc.postazione IN ('ZAW2', 'ZAW-2', 'ZAW 2')
            OR z2.articolo IS NOT NULL
        )
        THEN CONCAT_WS(
            ' | ',
            bc.note,
            'ZAW2_CYCLES=' || z2.zaw2_cycles,
            'ZAW2_MULTI=' || z2.multi_cycle_flag,
            'ZAW2_GROUPS=' || z2.gruppi_unione
        )


        WHEN (
            bc.postazione ILIKE '%HENN%'
            OR h.articolo IS NOT NULL
        )
        THEN CONCAT_WS(
            ' | ',
            bc.note,
            'HENN_CYCLES=' || h.henn_cycles,
            'HENN_MULTI=' || h.multi_cycle_flag,
            'HENN_GROUPS=' || h.gruppi_henn
        )


        WHEN (
            bc.postazione ILIKE '%PIDMILL%'
            OR p.articolo IS NOT NULL
        )
        THEN CONCAT_WS(
            ' | ',
            bc.note,
            'PIDMILL_CYCLES=' || p.pidmill_cycles,
            'PIDMILL_MULTI=' || p.multi_cycle_flag,
            'PIDMILL_ANTICIPABILE=' || p.anticipabile_flag,
            'PIDMILL_GROUPS=' || p.gruppi_pidmill
        )


        ELSE bc.note

    END AS note


FROM bom_components bc

LEFT JOIN vw_zaw_group_load z1
    ON z1.articolo = bc.articolo

LEFT JOIN vw_zaw2_group_load z2
    ON z2.articolo = bc.articolo

LEFT JOIN vw_henn_group_load h
    ON h.articolo = bc.articolo

LEFT JOIN vw_pidmill_group_load p
    ON p.articolo = bc.articolo


WHERE bc.codice_componente IS NOT NULL;
"""


def materialize_component_usage() -> dict:

    engine = create_engine(os.environ["DATABASE_URL"])

    with engine.begin() as conn:
        conn.execute(text(SQL))

    return {"ok": True}


def main():

    print(materialize_component_usage())


if __name__ == "__main__":
    main()

