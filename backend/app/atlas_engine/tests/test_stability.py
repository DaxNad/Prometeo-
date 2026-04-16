from typing import List

from backend.app.atlas_engine.services.atlas_service import AtlasService
from backend.app.atlas_engine.contracts import AtlasScenarioRequest, AtlasOrder, AtlasEvent
from backend.app.atlas_engine.adapters.ortools_adapter import ORToolsAdapter, PenaltyConfig
from backend.app.atlas_engine.builders.snapshot_builder import build_snapshot
from backend.app.atlas_engine.builders.constraint_builder import build_constraints
from backend.app.atlas_engine.builders.objective_builder import build_objective


def _hamming_topk(a: List[str], b: List[str], k: int) -> int:
    n = min(k, len(a), len(b))
    return sum(1 for i in range(n) if a[i] != b[i])


def test_identical_input_identical_output():
    req = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="S1", station="ZAW-1", priority="ALTA", quantity=4),
            AtlasOrder(order_id="S2", station="ZAW-1", priority="MEDIA", quantity=3),
            AtlasOrder(order_id="S3", station="ZAW-1", priority="BASSA", quantity=2),
        ],
    )
    p1 = AtlasService.make_plan(req, adapter="ortools")
    p2 = AtlasService.make_plan(req, adapter="ortools")
    assert p1.sequence == p2.sequence
    # breakdown stability: totals in the same order_id sequence are equal
    s1 = {x["order_id"]: x.get("total") for x in p1.meta.get("scores", [])}
    s2 = {x["order_id"]: x.get("total") for x in p2.meta.get("scores", [])}
    assert s1 == s2


def test_small_coefficient_variation_controls_ranking_change():
    # Due elementi quasi pari, la piccola variazione di coefficiente non deve stravolgere il top-k
    req = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="V10", station="ZAW-1", priority="MEDIA", quantity=10),
            AtlasOrder(order_id="V09", station="ZAW-1", priority="MEDIA", quantity=9),
        ],
        capacities={"station_queue_pressure": 1},
    )
    snap = build_snapshot(req)
    cons = build_constraints(snap)
    obj = build_objective(snap)
    base = ORToolsAdapter(config=PenaltyConfig(station_pressure_penalty=0.10)).solve(snap, cons, obj)
    slight = ORToolsAdapter(config=PenaltyConfig(station_pressure_penalty=0.11)).solve(snap, cons, obj)
    # Al massimo una differenza nelle prime 2 posizioni
    assert _hamming_topk(base["sequence"], slight["sequence"], 2) <= 1


def test_dominant_feasible_keeps_first_under_minor_pressure():
    req = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="D1", station="ZAW-1", priority="ALTA", quantity=2),
            AtlasOrder(order_id="D2", station="ZAW-1", priority="MEDIA", quantity=50),
        ],
    )
    p0 = AtlasService.make_plan(req, adapter="ortools")
    req_cap = AtlasScenarioRequest(
        station="ZAW-1",
        orders=req.orders,
        capacities={"station_queue_pressure": 2},
    )
    p1 = AtlasService.make_plan(req_cap, adapter="ortools")
    assert p0.sequence[0] == "D1"
    assert p1.sequence[0] == "D1"


def test_soft_limit_and_group_precedence_do_not_oscillate():
    # 1 feasible + 3 blocked nello stesso gruppo
    req = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="G0", station="ZAW-1", priority="MEDIA", code="GX"),
            AtlasOrder(order_id="G1", station="ZAW-1", priority="MEDIA", status="bloccato", code="GX"),
            AtlasOrder(order_id="G2", station="ZAW-1", priority="MEDIA", status="bloccato", code="GX"),
            AtlasOrder(order_id="G3", station="ZAW-1", priority="MEDIA", status="bloccato", code="GX"),
        ],
    )
    p1 = AtlasService.make_plan(req, adapter="ortools")
    p2 = AtlasService.make_plan(req, adapter="ortools")
    assert p1.sequence == p2.sequence
    # Il feasible resta primo e i bloccati sono in coda in ordine deterministico
    assert p1.sequence[0] == "G0"
