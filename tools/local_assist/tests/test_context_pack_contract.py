#!/usr/bin/env python3
import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "context_pack.py"
spec = importlib.util.spec_from_file_location("context_pack", MODULE_PATH)
context_pack = importlib.util.module_from_spec(spec)
spec.loader.exec_module(context_pack)


def test_sanitize_text_redacts_forbidden_markers():
    text = "ok\nLOCAL_ASSIST_SECRET_MARKER\nLOCAL_ASSIST_SPEC_MARKER\nstill ok"
    sanitized = context_pack.sanitize_text(text)
    assert "ok" in sanitized
    assert "LOCAL_ASSIST_SECRET_MARKER" not in sanitized
    assert "LOCAL_ASSIST_SPEC_MARKER" not in sanitized
    assert sanitized.count("[REDACTED_BY_LOCAL_ASSIST]") == 2


def test_context_pack_shape_without_diff_stats():
    pack = context_pack.build_context_pack(include_diff_stats=False)
    assert pack["capability"] == "LOCAL_ASSIST_BRIDGE_002"
    assert pack["mode"] == "safe_context_pack"
    assert pack["repo_root_label"] == "PROMETEO_REPO"
    assert "git_status" in pack["commands"]
    assert "git_branch" in pack["commands"]
    assert "git_diff_stat" not in pack["commands"]
    assert "git_diff_cached_stat" not in pack["commands"]


def test_safe_commands_allowlist_is_limited():
    assert set(context_pack.SAFE_COMMANDS) == {
        "git_status",
        "git_branch",
        "git_diff_stat",
        "git_diff_cached_stat",
    }
