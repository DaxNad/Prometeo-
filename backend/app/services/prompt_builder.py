def build_agent_runtime_prompt(
    *,
    source: str,
    line_id: str,
    event_type: str,
    severity: str,
    payload: dict,
    inspection: dict,
    local_decision_action: str,
) -> str:
    station = payload.get("station") or inspection.get("station") or "NA"
    order_id = payload.get("order_id") or inspection.get("order_id") or "NA"
    description = payload.get("description") or inspection.get("description") or ""
    components = payload.get("components") or inspection.get("components") or []
    qty = payload.get("qty") or inspection.get("qty") or "NA"
    due_date = payload.get("due_date") or inspection.get("due_date") or "NA"

    components_str = ", ".join(str(x) for x in components) if components else "non specificati"

    return f"""
Sei PROMETEO.
Rispondi solo in italiano.
Rispondi in modo sintetico, operativo, senza introduzioni.
Restituisci solo tre righe:
AZIONE_TL: ...
MOTIVO: ...
PRIORITA: ...

Vincolo:
- non cambiare il senso dell'azione locale già decisa da PROMETEO
- mantieni coerenza con il contesto operativo reale reparto

Contesto runtime:
source: {source}
line_id: {line_id}
event_type: {event_type}
severity: {severity}

Dati evento:
station: {station}
order_id: {order_id}
description: {description}
components: {components_str}
qty: {qty}
due_date: {due_date}

Decisione locale già calcolata:
action: {local_decision_action}

Inspection:
{inspection}

Genera una spiegazione TL sintetica coerente con l'azione locale.
""".strip()
