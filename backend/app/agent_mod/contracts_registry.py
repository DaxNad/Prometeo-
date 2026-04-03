from __future__ import annotations

SERVICE_SQL_CONTRACTS = {
    "sequence_planner": {
        "views": [
            "vw_tl_zaw1_board",
            "vw_tl_zaw2_board",
        ],
        "columns": {
            "vw_tl_zaw1_board": [
                "articolo",
                "quantita",
                "data_spedizione",
                "priorita_cliente",
            ],
            "vw_tl_zaw2_board": [
                "articolo",
                "quantita",
                "data_spedizione",
                "priorita_cliente",
            ],
        },
    },
}

API_MODULE_CONTRACTS = {
    "critical_modules": [
        "app.main",
        "app.api_production",
    ]
}

API_ENDPOINT_CONTRACTS = {
    "/health": [
        "ok",
        "service",
        "version",
        "postgres_reachable",
        "agent_runtime_enabled",
    ],
    "/production/sequence": [
        "ok",
        "planner_stage",
    ],
    "/production/turn-plan": [
        "ok",
        "planner_stage",
    ],
    "/production/machine-load": [],
}

RUNTIME_DATA_CONTRACTS = {
    "backend/app/data/global_sequence.json": "json",
    "backend/app/data/turn_plan.json": "json",
}
