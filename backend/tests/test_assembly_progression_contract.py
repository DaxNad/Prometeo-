from app.domain.assembly_progression import (
    normalize_assembly_progression,
    summarize_assembly_progression,
)


def test_assembly_progression_12056_contract_does_not_promote_confidence():
    profile = {
        "article": "12056",
        "confidence": "INFERITO",
        "assembly_progression": [
            {
                "state": "STATE_0",
                "description": "12056 standalone da specifica finitura",
                "stations": ["ZAW1"],
                "confidence": "INFERITO",
                "source": "SPEC_FINISHING_PLUS_TL",
            },
            {
                "state": "STATE_1",
                "description": "12056 viene unito/assemblato con 12057 tramite 468773",
                "stations": ["ZAW2"],
                "related_articles": ["12057"],
                "components": ["468773"],
                "confidence": "TL_DA_DOCUMENTARE",
                "source": "TL_KNOWLEDGE",
            },
            {
                "state": "STATE_2",
                "description": "Dopo ZAW2 viene aggiunto 12058 e il flusso arriva a PIDMILL",
                "stations": ["PIDMILL"],
                "related_articles": ["12058"],
                "confidence": "TL_DA_DOCUMENTARE",
                "source": "TL_KNOWLEDGE",
            },
        ],
    }

    progression = normalize_assembly_progression(profile)

    assert len(progression) == 3
    assert progression[0]["stations"] == ["ZAW1"]
    assert progression[1]["stations"] == ["ZAW2"]
    assert progression[1]["related_articles"] == ["12057"]
    assert progression[1]["components"] == ["468773"]
    assert progression[2]["stations"] == ["PIDMILL"]
    assert progression[2]["related_articles"] == ["12058"]
    assert progression[1]["confidence"] == "TL_DA_DOCUMENTARE"


def test_assembly_progression_summary_is_compact_and_operational():
    profile = {
        "assembly_progression": [
            {
                "state": "STATE_1",
                "stations": ["ZAW2"],
                "related_articles": ["12057"],
                "components": ["468773"],
                "confidence": "TL_DA_DOCUMENTARE",
            }
        ]
    }

    lines = summarize_assembly_progression(profile)

    assert lines == [
        "STATE_1: stazioni ZAW2, con 12057, componenti 468773 (TL_DA_DOCUMENTARE)"
    ]
