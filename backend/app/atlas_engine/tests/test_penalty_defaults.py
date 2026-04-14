from backend.app.atlas_engine.config.penalty_defaults import (
    PARAMETERS,
    CURRENT_DEFAULTS,
    PROPOSED_DEFAULTS,
    SAFE_RANGES,
)


def test_penalty_defaults_proposal_structure():
    # Keys exist and align across dicts
    assert set(PARAMETERS) <= set(CURRENT_DEFAULTS)
    assert set(PARAMETERS) <= set(PROPOSED_DEFAULTS)
    assert set(PARAMETERS) <= set(SAFE_RANGES)

    # Proposed within safe ranges and current also within ranges
    for k in PARAMETERS:
        lo, hi = SAFE_RANGES[k]
        cv = CURRENT_DEFAULTS[k]
        pv = PROPOSED_DEFAULTS[k]
        assert lo <= cv <= hi
        assert lo <= pv <= hi

