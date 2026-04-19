
"""
Adapter read-only verso servizi produzione.

Serve per evitare:

executor → api router dependency
"""

from app.services.production_queries import (
    get_sequence_compatibility,
    get_machine_load,
)


def read_sequence_compat(service, payload):

    return get_sequence_compatibility(service, **payload)



def read_machine_load(service, payload):

    return get_machine_load(service, **payload)
