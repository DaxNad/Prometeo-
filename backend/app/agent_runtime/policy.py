from __future__ import annotations


class RuntimePolicy:
    def should_escalate(self, severity: str, inspection: dict) -> bool:
        if severity in {"high", "critical"}:
            return True

        if inspection.get("possible_anomaly", False):
            return True

        return False
