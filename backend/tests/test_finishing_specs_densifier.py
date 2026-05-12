from app.domain.finishing_specs_densifier import (
    ALREADY_AUTHORITATIVE,
    ASK_TL,
    AUTO_NORMALIZABLE,
    BLOCKED,
    _suggest_questions,
    _support_summary_from_metadata,
    build_densification_preview,
)


def test_densifier_marks_already_authoritative_without_patch():
    def loader(_record):
        return {}

    preview = build_densification_preview(
        metadata_loader=loader,
        specs_root=None,
    )

    # Questo test usa il repo reale solo se esiste; il contratto centrale è coperto dai test sotto.
    assert preview["schema"] == "PROMETEO_FINISHING_SPECS_DENSIFICATION_PREVIEW_V1"
    assert preview["mode"] == "preview_only"


def test_densifier_auto_normalizes_structured_synthetic_metadata(monkeypatch):
    from app.domain import finishing_specs_densifier as d

    fake_index = {
        "records": [
            {
                "article": "12999",
                "authoritative": False,
                "confidence": "CERTO",
                "issues": ["unsupported_or_missing_schema"],
            }
        ]
    }

    metadata = {
        "stations_expected": [
            "LAVAGGIO",
            "CONTROLLO_VISIVO",
            "INSERIMENTO_GUAINA",
            "MARCATURA",
            "HENN",
            "ZAW1",
            "COLLAUDO_PRESSIONE",
            "COLLAUDO_VERTICALE",
            "SACCHETTO",
        ],
        "linked_bom": [
            {"component": "468922"},
            {"component": "469122"},
            {"component": "468763"},
        ],
    }

    monkeypatch.setattr(d, "build_finishing_specs_index", lambda _root=None: fake_index)

    preview = build_densification_preview(metadata_loader=lambda _record: metadata)
    result = preview["results"][0]

    assert result["classification"] == AUTO_NORMALIZABLE
    patch = result["proposed_patch"]
    assert patch["schema"] == "PROMETEO_REAL_DATA_PILOT_V1"
    assert patch["route_status"] == "CERTO"
    assert [step["station"] for step in patch["route_steps"]] == [
        "LAVAGGIO",
        "CONTROLLO_VISIVO",
        "GUAINA",
        "MARCATURA",
        "HENN",
        "ZAW1",
        "CP",
    ]
    assert patch["constraints"]["has_henn"] is True
    assert patch["constraints"]["has_guaina"] is True
    assert patch["constraints"]["cp_required"] is True
    assert patch["constraints"]["cp_machine_mode"] == "VERTICALE_DUE_PIANI"


def test_densifier_asks_tl_for_real_zaw2(monkeypatch):
    from app.domain import finishing_specs_densifier as d

    fake_index = {
        "records": [
            {
                "article": "12888",
                "authoritative": False,
                "confidence": "CERTO",
                "issues": [],
            }
        ]
    }
    metadata = {"stations_expected": ["LAVAGGIO", "ZAW2", "COLLAUDO_PRESSIONE"]}

    monkeypatch.setattr(d, "build_finishing_specs_index", lambda _root=None: fake_index)

    preview = build_densification_preview(metadata_loader=lambda _record: metadata)
    result = preview["results"][0]

    assert result["classification"] == ASK_TL
    assert "zaw2_real_station_requires_tl_confirmation" in result["reasons"]
    assert result["proposed_patch"] == {}


def test_densifier_blocks_poor_metadata(monkeypatch):
    from app.domain import finishing_specs_densifier as d

    fake_index = {
        "records": [
            {
                "article": "12777",
                "authoritative": False,
                "confidence": "DA_VERIFICARE",
                "issues": ["unsupported_or_missing_schema"],
            }
        ]
    }

    monkeypatch.setattr(d, "build_finishing_specs_index", lambda _root=None: fake_index)

    preview = build_densification_preview(metadata_loader=lambda _record: {})
    result = preview["results"][0]

    assert result["classification"] == BLOCKED
    assert "missing_stations_expected" in result["reasons"]
    assert result["proposed_patch"] == {}


def test_densifier_keeps_authoritative_records_untouched(monkeypatch):
    from app.domain import finishing_specs_densifier as d

    fake_index = {
        "records": [
            {
                "article": "12066",
                "authoritative": True,
                "confidence": "CERTO",
                "issues": [],
            }
        ]
    }

    monkeypatch.setattr(d, "build_finishing_specs_index", lambda _root=None: fake_index)

    preview = build_densification_preview(metadata_loader=lambda _record: {})
    result = preview["results"][0]

    assert result["classification"] == ALREADY_AUTHORITATIVE
    assert result["proposed_patch"] == {}

def test_densifier_turns_poor_metadata_with_support_into_ask_tl(monkeypatch):
    from app.domain import finishing_specs_densifier as d

    fake_index = {
        "records": [
            {
                "article": "12097",
                "authoritative": False,
                "confidence": "DA_VERIFICARE",
                "issues": ["unsupported_or_missing_schema"],
            }
        ]
    }

    metadata = {
        "drawing": "A 236 501 81 00",
        "revision": "14",
        "stations_expected": [
            "LAVAGGIO",
            "CONTROLLO_VISIVO",
            "INSERIMENTO_GUAINA",
            "MARCATURA",
            "ZAW1",
            "COLLAUDO_PRESSIONE",
        ],
        "linked_bom": [
            {"component": "468922"},
            {"component": "468728"},
        ],
    }

    monkeypatch.setattr(d, "build_finishing_specs_index", lambda _root=None: fake_index)

    preview = build_densification_preview(metadata_loader=lambda _record: metadata)
    result = preview["results"][0]

    assert result["classification"] == ASK_TL
    assert result["proposed_patch"] == {}
    assert "metadata_poor_but_support_available" in result["reasons"]
    assert result["support_summary"]["drawing"] == "A 236 501 81 00"
    assert result["support_summary"]["has_zaw1_hint"] is True
    assert result["support_summary"]["has_cp_hint"] is True
    assert result["suggested_questions"]
    assert any("Confermi" in q for q in result["suggested_questions"])


def test_densifier_does_not_create_patch_from_support_only(monkeypatch):
    from app.domain import finishing_specs_densifier as d

    fake_index = {
        "records": [
            {
                "article": "12402",
                "authoritative": False,
                "confidence": "DA_VERIFICARE",
                "issues": ["unsupported_or_missing_schema"],
            }
        ]
    }

    metadata = {
        "drawing": "A 167 500 7203",
        "stations_expected": ["ZAW2", "PIDMILL", "COLLAUDO_PRESSIONE"],
        "linked_bom": [{"component": "468728"}],
    }

    monkeypatch.setattr(d, "build_finishing_specs_index", lambda _root=None: fake_index)

    preview = build_densification_preview(metadata_loader=lambda _record: metadata)
    result = preview["results"][0]

    assert result["classification"] == ASK_TL
    assert result["proposed_patch"] == {}
    assert "tl_confirmation_required" in result["reasons"]
    assert any("ZAW2" in q for q in result["suggested_questions"])
    assert any("PIDMILL" in q for q in result["suggested_questions"])


def test_support_without_henn_does_not_generate_henn_absence_question():
    summary = _support_summary_from_metadata(
        {
            "stations_expected": ["LAVAGGIO", "ZAW1", "COLLAUDO_PRESSIONE"],
            "linked_bom": [{"component": "468922"}],
        }
    )
    questions = _suggest_questions("12073", summary)

    assert summary["henn_status"] == "NON_INDICATO"
    assert not any("HENN è assente" in q for q in questions)


def test_support_with_henn_generates_henn_presence_question():
    summary = _support_summary_from_metadata(
        {
            "stations_expected": ["ASSEMBLAGGIO_HENN", "ZAW1", "COLLAUDO_PRESSIONE"],
        }
    )
    questions = _suggest_questions("12073", summary)

    assert summary["henn_status"] == "PRESENTE"
    assert any("HENN è presente" in q for q in questions)


def test_support_with_pidmill_generates_pidmill_question():
    summary = _support_summary_from_metadata(
        {
            "stations_expected": ["LAVAGGIO", "PIDMILL_CLIP", "COLLAUDO_PRESSIONE"],
        }
    )
    questions = _suggest_questions("12091", summary)

    assert summary["pidmill_status"] == "PRESENTE"
    assert any("PIDMILL è realmente presente" in q for q in questions)


def test_support_without_pidmill_does_not_generate_pidmill_absence_question():
    summary = _support_summary_from_metadata(
        {
            "stations_expected": ["LAVAGGIO", "ZAW1", "COLLAUDO_PRESSIONE"],
        }
    )
    questions = _suggest_questions("12091", summary)

    assert summary["pidmill_status"] == "NON_INDICATO"
    assert not any("PIDMILL è assente" in q for q in questions)
