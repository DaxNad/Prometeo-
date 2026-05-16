from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


EXTERNAL_AI_ADAPTERS = {"openai", "claude", "mimo_cloud", "codex"}
AI_INVOCATION_AUDIT_LOG = Path("data/local_reports/ai_invocation_audit.jsonl")


@dataclass(frozen=True)
class AIRouterPolicyDecision:
    allowed: bool
    blocked: bool
    adapter: str
    scope: str
    sanitized: bool
    raw_prompt_stored: bool
    risk_level: str
    reason: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_ai_router_policy(
    *,
    target_adapter: str,
    scope: str,
    sanitized_prompt: str | None,
    data_boundary_check: dict[str, Any],
    sanitized: bool,
    raw_files_attached: bool = False,
    screenshots_attached: bool = False,
) -> dict[str, Any]:
    adapter = str(target_adapter or "").strip().lower()
    scope_value = str(scope or "").strip()
    reasons: list[str] = []

    if adapter in EXTERNAL_AI_ADAPTERS:
        if not sanitized:
            reasons.append("sanitized_prompt_required")
        if not sanitized_prompt:
            reasons.append("sanitized_prompt_missing")
        if not scope_value:
            reasons.append("scope_required")
        if not data_boundary_check.get("allowed_external", False):
            reasons.append("data_boundary_not_allowed")
        if raw_files_attached:
            reasons.append("raw_files_forbidden")
        if screenshots_attached:
            reasons.append("screenshots_forbidden")

    allowed = not reasons
    return AIRouterPolicyDecision(
        allowed=allowed,
        blocked=not allowed,
        adapter=adapter,
        scope=scope_value,
        sanitized=sanitized,
        raw_prompt_stored=False,
        risk_level=str(data_boundary_check.get("risk_level", "UNKNOWN")),
        reason=";".join(reasons) if reasons else None,
    ).to_dict()


def append_ai_invocation_audit(
    decision: dict[str, Any],
    *,
    log_path: Path | None = None,
) -> dict[str, Any]:
    path = log_path or AI_INVOCATION_AUDIT_LOG
    record = {
        "timestamp": datetime.now(UTC).isoformat(),
        "adapter": decision.get("adapter"),
        "scope": decision.get("scope"),
        "raw_prompt_stored": False,
        "sanitized": bool(decision.get("sanitized")),
        "risk_level": decision.get("risk_level"),
        "blocked": bool(decision.get("blocked")),
        "reason": decision.get("reason"),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return record
