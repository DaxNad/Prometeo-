from backend.app.atlas_engine.services.atlas_service import AtlasService
from backend.app.atlas_engine.contracts import AtlasScenarioRequest, AtlasOrder, AtlasEvent


def test_make_plan_ortools_deterministic_feasible_first():
    req = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="O2", station="ZAW-1", priority="MEDIA"),
            AtlasOrder(order_id="O1", station="ZAW-1", priority="ALTA", status="bloccato"),
            AtlasOrder(order_id="O3", station="ZAW-1", priority="BASSA"),
        ],
        events=[AtlasEvent(station="ZAW-1", title="operational", status="OPEN")],
    )
    # OR-Tools adapter deterministico: fattibile prima, bloccato in coda, priorità applicata
    plan = AtlasService.make_plan(req, adapter="ortools")
    # Feasible-first: O1 (bloccato) va in fondo, prima viene O2 (MEDIA) poi O3 (BASSA)
    assert plan.sequence[-1] == "O1"
    assert plan.sequence[0:2] == ["O2", "O3"]
    assert plan.meta.get("adapter") == "ortools"
    assert "explain" in plan.meta


def test_make_plan_ortools_shared_pressure_and_open_event_signals():
    req = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="O2", station="ZAW-1", priority="MEDIA"),
            AtlasOrder(order_id="O1", station="ZAW-1", priority="ALTA", status="bloccato"),
            AtlasOrder(order_id="O3", station="ZAW-1", priority="BASSA"),
        ],
        events=[AtlasEvent(station="ZAW-1", title="operational", status="OPEN")],
        capacities={"shared_component_pressure": True},
    )
    plan = AtlasService.make_plan(req, adapter="ortools")
    # blocked after feasible items
    assert plan.sequence[-1] == "O1"
    # shared pressure and open event reflected in meta.scoring
    scoring = plan.meta.get("scoring", {})
    assert scoring.get("penalty_shared_pressure") is True
    assert scoring.get("penalty_open_event") is True
    # explain payload contains operational event reason (post-hoc, not from solve)
    expl = plan.meta.get("explain", {})
    reasons = expl.get("reasons", [])
    assert any("operational event present" in r for r in reasons)


def test_blocked_item_cannot_be_first_when_feasible_exists():
    req = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="O_blocked_high", station="ZAW-1", priority="ALTA", status="bloccato"),
            AtlasOrder(order_id="O_feasible_low", station="ZAW-1", priority="BASSA"),
        ],
    )
    plan = AtlasService.make_plan(req, adapter="ortools")
    assert plan.sequence[0] != "O_blocked_high"


def test_station_queue_pressure_affects_ranking_and_scores():
    # Senza pressione: due ordini stessa priorità → tie-break per order_id
    base_req = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="O10", station="ZAW-1", priority="MEDIA", quantity=10),
            AtlasOrder(order_id="O01", station="ZAW-1", priority="MEDIA", quantity=1),
        ],
    )
    base_plan = AtlasService.make_plan(base_req, adapter="ortools")
    assert base_plan.sequence[0] == "O01"

    # Con pressione coda significativa, l'ordine con quantità maggiore riceve penalità maggiore
    press_req = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="O10", station="ZAW-1", priority="MEDIA", quantity=10),
            AtlasOrder(order_id="O01", station="ZAW-1", priority="MEDIA", quantity=1),
        ],
        capacities={"station_queue_pressure": 5},
    )
    press_plan = AtlasService.make_plan(press_req, adapter="ortools")
    assert press_plan.sequence[0] == "O01"  # rimane davanti, l'altro viene ulteriormente penalizzato
    # breakdown punteggi presente e con chiavi attese
    assert isinstance(press_plan.meta.get("scores"), list) and len(press_plan.meta["scores"]) == 2
    for item in press_plan.meta["scores"]:
        for k in (
            "order_id",
            "priority_reward",
            "blocked_penalty",
            "shared_component_penalty",
            "open_event_penalty",
            "station_pressure_penalty",
            "total",
        ):
            assert k in item
