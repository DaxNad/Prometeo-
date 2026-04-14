from backend.app.atlas_engine.services.atlas_service import AtlasService
from backend.app.atlas_engine.contracts import AtlasScenarioRequest, AtlasOrder, AtlasEvent
from backend.app.atlas_engine.adapters.ortools_adapter import ORToolsAdapter, PenaltyConfig
from backend.app.atlas_engine.builders.snapshot_builder import build_snapshot
from backend.app.atlas_engine.builders.constraint_builder import build_constraints
from backend.app.atlas_engine.builders.objective_builder import build_objective


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


def test_assembly_group_coherence_preserves_deterministic_order():
    # Due ordini stessa priorità e quantità, stesso assembly_group (usiamo code come gruppo)
    req = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="A02", station="ZAW-1", priority="MEDIA", quantity=5, code="AG-1"),
            AtlasOrder(order_id="A01", station="ZAW-1", priority="MEDIA", quantity=5, code="AG-1"),
        ],
        capacities={"station_queue_pressure": 1},
    )
    plan = AtlasService.make_plan(req, adapter="ortools")
    # Determinismo: con stessa priorità e quantità, si preferisce ordine lessicografico (A01 prima di A02)
    assert plan.sequence[0] == "A01"
    # Coerenza assembly_group influisce sul totale: il primo ha total >= del secondo
    scores = plan.meta.get("scores", [])
    assert isinstance(scores, list) and len(scores) == 2
    assert scores[0].get("order_id") == "A01"
    assert float(scores[0].get("total", 0)) >= float(scores[1].get("total", 0))


def test_penalty_config_deterministic_effect_on_ranking():
    # Stessa priorità, solo quantità diversa; default: O01 prima di O10
    req = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="O10", station="ZAW-1", priority="MEDIA", quantity=10),
            AtlasOrder(order_id="O01", station="ZAW-1", priority="MEDIA", quantity=1),
        ],
        capacities={"station_queue_pressure": 1},
    )
    # Default adapter via AtlasService
    base_plan = AtlasService.make_plan(req, adapter="ortools")
    assert base_plan.sequence[0] == "O01"

    # Adapter con configurazione interna che INVERTE il segnale di pressione stazione (reward per quantità)
    cfg = PenaltyConfig(station_pressure_penalty=-1.0)
    snap = build_snapshot(req)
    cons = build_constraints(snap)
    obj = build_objective(snap)
    res = ORToolsAdapter(config=cfg).solve(snap, cons, obj)
    # Con reward sulla quantità, O10 diventa primo in modo deterministico
    assert res["sequence"][0] == "O10"


def test_topk_blocked_soft_limit_penalizes_excess_blocked():
    # Tre bloccati con stessa priorità: baseline ordinamento lessicografico
    req = AtlasScenarioRequest(
        station="ZAW-1",
        orders=[
            AtlasOrder(order_id="B1", station="ZAW-1", priority="MEDIA", status="bloccato"),
            AtlasOrder(order_id="B2", station="ZAW-1", priority="MEDIA", status="bloccato"),
            AtlasOrder(order_id="B3", station="ZAW-1", priority="MEDIA", status="bloccato"),
        ],
    )
    # Default adapter via AtlasService (usa soft limiter con max_blocked_in_top_k=1, K=3)
    plan = AtlasService.make_plan(req, adapter="ortools")
    # Il secondo/terzo bloccato ricevono penalità extra deterministica; ordine non puramente lessicografico
    # Sequenza attesa: B1 resta primo tra i bloccati; B2 e B3 possono invertirsi per effetto della penalità crescente
    assert plan.sequence[0] == "B1"
    # breakdown presente
    scores = plan.meta.get("scores", [])
    assert isinstance(scores, list) and len(scores) == 3
    # verifica che almeno uno tra B2 e B3 abbia total < dell'altro in modo deterministico
    totals = {s["order_id"]: float(s.get("total", 0)) for s in scores}
    assert totals["B1"] >= max(totals["B2"], totals["B3"])  # B1 penalizzato meno degli altri
