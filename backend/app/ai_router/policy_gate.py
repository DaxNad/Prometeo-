from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.security.prompt_sanitizer import sanitize_prompt


EXTERNAL_AI_ADAPTERS = {"openai", "claude", "mimo_cloud", "codex"}
AI_INVOCATION_AUDIT_LOG = Path("data/local_reports/ai_invocation_audit.jsonl")


class AIRouterPolicyBlocked(RuntimeError):
    def __init__(self, decision: dict[str, Any]):
        self.decision = decision
        reason = decision.get("reason") or "external_ai_policy_blocked"
        super().__init__(str(reason))


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
    verifier_present: bool = False,
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
        if scope_value == "C_GUARDED" and not verifier_present:
            reasons.append("verifier_required")

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


def prepare_external_ai_invocation(
    *,
    target_adapter: str,
    scope: str,
    raw_prompt: str | None,
    raw_files_attached: bool = False,
    screenshots_attached: bool = False,
    log_path: Path | None = None,
) -> dict[str, Any]:
    """
    Single read-only boundary for cloud AI invocations.

    Contract:
    - classifier and sanitizer always run before provider IO
    - policy decision is audited without raw prompt storage
    - returned prompt is sanitized output only
    """
    sanitization = sanitize_prompt(raw_prompt, scope_declared=bool(scope))
    sanitized_prompt = str(sanitization.get("sanitized_prompt") or "")
    decision = evaluate_ai_router_policy(
        target_adapter=target_adapter,
        scope=scope,
        sanitized_prompt=sanitized_prompt,
        data_boundary_check=sanitization.get("boundary_check") or {},
        sanitized=True,
        raw_files_attached=raw_files_attached,
        screenshots_attached=screenshots_attached,
    )
    audit_record = append_ai_invocation_audit(decision, log_path=log_path)

    return {
        "allowed": bool(decision.get("allowed")),
        "blocked": bool(decision.get("blocked")),
        "sanitized_prompt": sanitized_prompt,
        "sanitization": sanitization,
        "decision": decision,
        "audit": audit_record,
    }


def enforce_external_ai_boundary(
    *,
    target_adapter: str,
    scope: str,
    raw_prompt: str | None,
    raw_files_attached: bool = False,
    screenshots_attached: bool = False,
    log_path: Path | None = None,
) -> dict[str, Any]:
    invocation = prepare_external_ai_invocation(
        target_adapter=target_adapter,
        scope=scope,
        raw_prompt=raw_prompt,
        raw_files_attached=raw_files_attached,
        screenshots_attached=screenshots_attached,
        log_path=log_path,
    )

    if invocation["blocked"]:
        raise AIRouterPolicyBlocked(invocation["decision"])

    return invocation
