
"""
Production read-only queries shared across:

- api_production
- executor layer
- atlas diagnostics
"""

from typing import Any


def get_sequence_compatibility(service, *args, **kwargs) -> Any:
    """
    Wrapper esplicito per sequence compatibility.
    Evita dipendenza diretta da router FastAPI.
    """

    return service.sequence_compat_check(*args, **kwargs)



def get_machine_load(service, *args, **kwargs) -> Any:
    """
    Wrapper esplicito per machine load.
    Boundary stabile tra dominio e layer HTTP.
    """

    return service.machine_load(*args, **kwargs)
