
"""
Adapter read-only verso servizi produzione.

Serve per evitare:

executor → api router dependency
"""

from app.services.production_queries import (
    get_sequence_compatibility,
    get_machine_load,
)


def _normalize_payload(payload):
    if payload is None:
        return {}
    if not isinstance(payload, dict):
        raise ValueError("invalid_payload")
    return payload


def read_sequence_compat(service, payload):
    payload_map = _normalize_payload(payload)
    return get_sequence_compatibility(service, **payload_map)



def read_machine_load(service, payload):
    payload_map = _normalize_payload(payload)
    return get_machine_load(service, **payload_map)
