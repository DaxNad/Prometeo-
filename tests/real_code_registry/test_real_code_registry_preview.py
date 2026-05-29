import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/real_code_registry/build_real_code_registry_preview.py"
OUT_JSON = ROOT / "data/local_reports/real_code_registry/real_code_registry_preview.json"

def run_preview():
    result = subprocess.run(
        ["python3", str(SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return result

def load_registry():
    return json.loads(OUT_JSON.read_text(encoding="utf-8"))

def test_technical_number_11434_is_excluded_from_records():
    run_preview()
    data = load_registry()

    record_codes = {r["code"] for r in data["records"]}
    excluded_values = {x["value"] for x in data["excluded_candidates"]}

    assert "11434" not in record_codes
    assert "11434" in excluded_values

def test_all_records_are_not_planner_safe_by_default():
    run_preview()
    data = load_registry()

    assert data["records"]
    assert all(r["planner_safe"] is False for r in data["records"])

def test_preview_does_not_write_to_runtime_targets():
    run_preview()
    data = load_registry()

    assert data["mode"] == "preview_only"
    assert data["rules"]["writes_to_planner"] is False
    assert data["rules"]["writes_to_smf"] is False
    assert data["rules"]["writes_to_db"] is False
    assert data["rules"]["promotes_to_certo"] is False


def test_bom_specs_is_observational_source_only():
    run_preview()
    data = load_registry()

    records = {r["code"]: r for r in data["records"]}
    record = records["12056"]

    assert "SMF_BOM_SPECS" in record["sources"]
    assert record["smf_bom_specs_seen"] is True
    assert record["smf_famiglia_processo"] == "DOPPIO_INNESTO_ZAW"

    assert record["planner_safe"] is False
    assert record["confidence"] == "DA_VERIFICARE"
    assert record["route_status"] in {"UNKNOWN", "DA_VERIFICARE"}


def test_tl_real_spec_intake_is_observational_source_only():
    run_preview()
    data = load_registry()

    records = {r["code"]: r for r in data["records"]}
    record = records["12511"]

    assert "TL_REAL_SPEC_INTAKE" in record["sources"]
    assert record["tl_real_spec_intake_seen"] is True
    assert record["tl_real_spec_initial_classification"] == "NEW_ENTRY_CANDIDATE_COMPLESSO"

    assert "COLLAUDO_A_PRESSIONE" in record["tl_real_spec_visible_processes"]
    assert "6429" in record["tl_real_spec_visible_components"]

    assert record["planner_safe"] is False
    assert record["confidence"] == "DA_VERIFICARE"
    assert record["route_status"] in {"UNKNOWN", "DA_VERIFICARE"}


def test_known_contradiction_rules_keep_records_non_planner_safe():
    run_preview()
    data = load_registry()

    records = {r["code"]: r for r in data["records"]}

    for code in ["12056", "12058", "12511"]:
        record = records[code]
        assert record["planner_safe"] is False
        assert record["route_status"] == "DA_VERIFICARE"
        assert record["contradictions"]

    assert records["12058"]["contradictions"][0]["planner_blocking"] is True
    assert records["12511"]["contradictions"][0]["kind"] == "KNOWN_ZAW2_FALSE_INFERENCE_RISK"

def test_cross_source_zaw_mismatch_detector_is_generic():
    from scripts.real_code_registry.build_real_code_registry_preview import (
        apply_cross_source_contradiction_detector,
    )

    records = {
        "99901": {
            "code": "99901",
            "sources": ["SMF_BOM_SPECS", "TL_REAL_SPEC_INTAKE"],
            "confidence": "DA_VERIFICARE",
            "route_status": "UNKNOWN",
            "planner_safe": False,
            "evidence_count": 2,
            "contradictions": [],
            "smf_bom_specs_seen": True,
            "smf_famiglia_processo": "PIDMILL_ZAW2",
            "tl_real_spec_intake_seen": True,
            "tl_real_spec_visible_processes": ["MARCATURA", "MACCHINA_CRIMP_RING_ZAW1", "COLLAUDO_A_PRESSIONE"],
        }
    }

    apply_cross_source_contradiction_detector(records)

    record = records["99901"]
    kinds = {c["kind"] for c in record["contradictions"]}

    assert "ZAW_STATION_MISMATCH" in kinds
    assert record["planner_safe"] is False
    assert record["route_status"] == "DA_VERIFICARE"


def test_cross_source_contradictions_block_evidence_score_promotion():
    run_preview()
    data = load_registry()

    records = {r["code"]: r for r in data["records"]}
    record = records["12511"]

    assert record["contradictions"]
    assert record["planner_safe"] is False
    assert record["confidence"] == "DA_VERIFICARE"
    assert record["route_status"] == "DA_VERIFICARE"
    assert record["evidence_score"] >= 0

def test_every_record_has_registry_evidence_pack():
    run_preview()
    data = load_registry()

    assert data["records"]
    for record in data["records"]:
        pack = record["evidence_pack"]
        assert pack["context_type"] == "REGISTRY_EVIDENCE_PACK"
        assert pack["safe_answer_mode"] == "OBSERVATIONAL_ONLY"
        assert pack["planner_allowed"] is False


def test_evidence_pack_strict_input_ready_requires_code_sources_and_evidence_refs():
    from scripts.real_code_registry.build_real_code_registry_preview import build_evidence_pack

    ready = build_evidence_pack({
        "code": "99902",
        "sources": ["LOCAL_REPORTS"],
        "evidence_refs": ["data/local_reports/example.md"],
        "contradictions": [],
        "route_status": "UNKNOWN",
    })
    missing = build_evidence_pack({
        "code": "99903",
        "sources": [],
        "evidence_refs": [],
        "contradictions": [],
        "route_status": "UNKNOWN",
    })

    assert ready["strict_input_ready"] is True
    assert missing["strict_input_ready"] is False
    assert "sources" in missing["missing_fields"]
    assert "evidence_refs" in missing["missing_fields"]


def test_evidence_pack_contradiction_summary_reflects_record_contradictions():
    run_preview()
    data = load_registry()

    records = {r["code"]: r for r in data["records"]}
    record = records["12511"]

    assert record["contradictions"]
    assert record["evidence_pack"]["contradiction_summary"]
    assert {
        item["kind"] for item in record["evidence_pack"]["contradiction_summary"]
    } == {
        item["kind"] for item in record["contradictions"]
    }


def test_evidence_pack_requires_tl_when_route_is_not_certo():
    run_preview()
    data = load_registry()

    assert data["records"]
    assert any(
        record["route_status"] != "CERTO" and record["evidence_pack"]["tl_required"] is True
        for record in data["records"]
    )


def test_evidence_pack_does_not_promote_any_record_to_certo():
    run_preview()
    data = load_registry()

    assert all(record["confidence"] != "CERTO" for record in data["records"])
    assert all(record["evidence_pack"]["planner_allowed"] is False for record in data["records"])



def test_contradictions_include_explainability_payload():
    run_preview()
    data = load_registry()
    contradicted_records = [
        record for record in data["records"]
        if record.get("contradictions")
    ]

    assert contradicted_records

    for record in contradicted_records:
        for contradiction in record["contradictions"]:
            explainability = contradiction.get("explainability")
            assert explainability
            assert explainability["rule"] == contradiction["kind"]
            assert explainability["status"] == "OBSERVATIONAL_ONLY"
            assert explainability["impact"] == "route_confidence_degraded"
            assert explainability["operator_action"] == "TL review required before planner-safe use"


def test_contradiction_explainability_is_preview_only_and_non_planner_promoting():
    run_preview()
    data = load_registry()

    for record in data["records"]:
        for contradiction in record.get("contradictions") or []:
            explainability = contradiction["explainability"]
            assert explainability["status"] == "OBSERVATIONAL_ONLY"
            assert contradiction["planner_blocking"] is True
            assert record["evidence_pack"]["planner_allowed"] is False
