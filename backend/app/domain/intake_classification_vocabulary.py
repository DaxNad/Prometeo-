from __future__ import annotations

import re
from typing import Any


ARTICLE_FIELD_ALIASES = frozenset(
    {
        "article",
        "articolo",
        "article_code",
        "codice",
        "customer_code",
        "codice_cliente",
        "drawing",
        "disegno",
        "revision",
        "rev",
        "revision_date",
        "description",
        "descrizione",
        "material",
        "materiale",
    }
)
ROUTE_FIELD_ALIASES = frozenset(
    {
        "operation",
        "operazione",
        "route_step",
        "fase",
        "station",
        "station_assignment",
        "sequence",
        "operation_sequence",
        "ciclo_operativo",
    }
)
COMPONENT_FIELD_ALIASES = frozenset(
    {
        "component",
        "component_code",
        "componente",
        "codice_componente",
        "bom_item",
        "distinta",
        "material_component",
        "part",
    }
)
TOOL_FIELD_ALIASES = frozenset(
    {
        "tool",
        "tools",
        "tooling",
        "machine",
        "macchina",
        "attrezzatura",
        "attrezzature",
        "dima",
        "calibro",
        "fixture",
        "utensile",
    }
)
QUALITY_FIELD_ALIASES = frozenset(
    {
        "quality_control",
        "quality_controls",
        "collaudo",
        "controllo",
        "controllo_qualita",
        "test",
        "inspection",
    }
)
CONSTRAINT_FIELD_ALIASES = frozenset(
    {
        "constraint",
        "constraints",
        "vincolo",
        "vincoli",
        "requisito",
        "condition",
        "precondition",
        "tolerance",
        "tolleranza",
    }
)
HUMAN_CONFIRMATION_FIELD_ALIASES = frozenset(
    {
        "confirmation",
        "conferma",
        "human_confirmation",
        "operational_confirmation",
    }
)

ROUTE_OPERATIONS = frozenset(
    {
        "LAVAGGIO",
        "INSERIMENTO GUAINA",
        "MARCATURA",
        "ASSEMBLAGGIO",
        "INSERIMENTO INNESTO RAPIDO",
        "SACCHETTO",
    }
)

QUALITY_PHRASES = (
    "COLLAUDO VISIVO",
    "COLLAUDO A PRESSIONE",
    "COLLAUDO A PRESSIONE VERTICALE",
    "CONTROLLO DIMENSIONALE",
    "PROVA TENUTA",
    "VERIFICA PRESSIONE",
)
QUALITY_DEFINITION_MARKERS = (
    "COLLAUDO",
    "CONTROLLO DIMENSIONALE",
    "CONTROLLO VISIVO",
    "PROVA TENUTA",
    "VERIFICA PRESSIONE",
)
HISTORICAL_NOTE_MARKERS = (
    "ESEGUITO IERI",
    "ESEGUITO OGGI",
    "GIA ESEGUITO",
    "GIÀ ESEGUITO",
)
GENERIC_CONFIRMATION_MARKERS = (
    "VA BENE",
    "OK",
    "CONFERMO",
)
CONSTRAINT_TERMS = (
    "VINCOLO",
    "RICHIEDE",
    "NON USARE",
    "NON ESEGUIRE",
    "NON ASSEMBLARE",
    "SOLO CON",
    "SOLO SE",
    "OBBLIGATOR",
    "INCOMPATIBILE",
    "LIMITE",
    "TOLLERANZA",
)
TOOL_TERMS = (
    "MACCHINA",
    "ATTREZZATURA",
    "TOOLING",
    "DIMA",
    "CALIBRO",
    "FIXTURE",
    "CRIMP",
)
OPERATION_TOOL_AMBIGUOUS_VALUES = frozenset({"MACCHINA CRIMP RING ZAW"})


def comparison_token(value: Any) -> str:
    text = str(value or "").strip()
    text = re.sub(r"\s+", " ", text)
    text = text.upper().replace("-", "_")
    return text.rstrip(":.")
