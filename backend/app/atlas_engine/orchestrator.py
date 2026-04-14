from __future__ import annotations

from .contracts import AtlasInput, AtlasPlan
from .constants import DEFAULT_ADAPTER, NOOP_ADAPTER
from .errors import AdapterNotAvailable, SolveFailed
from .builders.snapshot_builder import build_snapshot
from .builders.constraint_builder import build_constraints
from .builders.objective_builder import build_objective
from .adapters.noop_adapter import NoopAdapter
from .adapters.ortools_adapter import ORToolsAdapter
from .adapters.pyomo_adapter import PyomoAdapter
from .fallback import generate as fallback_generate
from .explain import build_explanation


def _get_adapter(name: str):
    name = (name or DEFAULT_ADAPTER).lower()
    if name == "ortools":
        return ORToolsAdapter()
    if name == "pyomo":
        return PyomoAdapter()
    if name == "noop":
        return NoopAdapter()
    raise AdapterNotAvailable(name)


def orchestrate(inp: AtlasInput, adapter_name: str = DEFAULT_ADAPTER) -> AtlasPlan:
    snapshot = build_snapshot(inp)
    constraints = build_constraints(snapshot)
    objective = build_objective(snapshot)

    try:
        adapter = _get_adapter(adapter_name)
        result = adapter.solve(snapshot, constraints, objective)
        sequence = result.get("sequence") or []
        meta = result.get("meta") or {"adapter": adapter_name}
    except Exception as exc:  # noqa: BLE001 – routing to fallback is intended
        # fallback must keep the system alive
        sequence = fallback_generate(inp)
        meta = {"adapter": NOOP_ADAPTER, "fallback_reason": str(type(exc).__name__)}

    expl = build_explanation(inp, sequence)
    return AtlasPlan(sequence=sequence, meta={**meta, "explain": expl.model_dump()})

