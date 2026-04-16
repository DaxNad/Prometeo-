import importlib
import json
from pathlib import Path

import app.domain.article_process_matrix as apm


def test_article_matrix_path_env_fallback_and_missing_file_are_safe(monkeypatch, tmp_path):
    env_base = tmp_path / "env_base"
    env_matrix = env_base / "finiture" / "article_route_matrix.json"
    env_matrix.parent.mkdir(parents=True, exist_ok=True)
    env_matrix.write_text(
        json.dumps(
            {
                "profiles": {
                    "ART-ENV": {
                        "route": ["CUT", "PAINT"],
                        "signals": {"priority_boost": 1},
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("SMF_BASE_PATH", str(env_base))
    m = importlib.reload(apm)

    assert m.get_article_profile("ART-ENV") is not None
    assert m.get_article_route("ART-ENV") == ["CUT", "PAINT"]
    assert m.get_article_signals("ART-ENV") == {"priority_boost": 1}

    monkeypatch.delenv("SMF_BASE_PATH", raising=False)
    fallback_home = tmp_path / "fake_home"
    fallback_base = fallback_home / "Documents" / "local_smf"
    fallback_matrix = fallback_base / "finiture" / "article_route_matrix.json"
    fallback_matrix.parent.mkdir(parents=True, exist_ok=True)
    fallback_matrix.write_text(
        json.dumps(
            {
                "profiles": {
                    "ART-FALLBACK": {
                        "route": ["WELD"],
                        "signals": {"hazmat": False},
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(Path, "home", staticmethod(lambda: fallback_home))
    m = importlib.reload(apm)

    assert m.get_article_route("ART-FALLBACK") == ["WELD"]
    assert m.get_article_signals("ART-FALLBACK") == {"hazmat": False}

    fallback_matrix.unlink()
    m = importlib.reload(apm)

    assert m.get_article_profile("ART-FALLBACK") is None
    assert m.get_article_route("ART-FALLBACK") == []
    assert m.get_article_signals("ART-FALLBACK") == {}

