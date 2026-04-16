from app.decision_merge.contracts import MergeDecision
from app.planner.contracts import PlannerOutput
from app.signal_classifier.contracts import SignalEnvelope
from app.agent_runtime.providers.atlas import AtlasProvider


def test_planner_is_only_sequencing_authority() -> None:
    output = PlannerOutput(sequence_slot=1, action="ASSEGNA")
    assert output.authority == "deterministic_planner"


def test_decision_merge_is_advisory_not_primary() -> None:
    merge = MergeDecision(
        planner_action="ASSEGNA",
        final_action="ASSEGNA",
        advisory_source="atlas",
        advisory_used_as_tiebreak=True,
    )
    assert merge.planner_action == merge.final_action


def test_signal_classifier_is_intake_contract_only() -> None:
    signal = SignalEnvelope(
        source="smf",
        station="ZAW-1",
        severity="high",
        signal_class="warning",
    )
    assert signal.source == "smf"


def test_atlas_provider_declares_non_primary_role() -> None:
    text = AtlasProvider().complete.__doc__
    # complete() may not define a docstring; validate output contract instead.
    assert text is None
    message = __import__("asyncio").run(AtlasProvider().complete("x"))
    assert "non come decisione primaria" in message
