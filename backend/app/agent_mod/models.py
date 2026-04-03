from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CheckResult:
    name: str
    passed: bool
    details: str = ""
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class GateResult:
    gate: str
    passed: bool
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def summary(self) -> str:
        return f"{self.gate}: {'PASS' if self.passed else 'FAIL'}"


@dataclass
class RunContext:
    root_dir: str
    backend_dir: str
    files: list[str] = field(default_factory=list)
    skip_runtime: bool = False
    snapshot: bool = False
    categories: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class SnapshotInfo:
    timestamp: str
    branch: str
    commit: str
    files: list[str]
    gates: list[dict[str, Any]]
