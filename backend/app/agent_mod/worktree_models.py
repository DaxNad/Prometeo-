from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class WorktreeEntry:
    path: str
    git_status: str
    category: str
    reason: str


@dataclass
class DeployRisk:
    code: str
    severity: str
    message: str


@dataclass
class HygieneReport:
    status: str
    repo_root: str
    branch: str
    core_changes: list[WorktreeEntry] = field(default_factory=list)
    runtime_artifacts: list[WorktreeEntry] = field(default_factory=list)
    junk_files: list[WorktreeEntry] = field(default_factory=list)
    deploy_risks: list[DeployRisk] = field(default_factory=list)
    recommended_git_add: list[str] = field(default_factory=list)
    recommended_exclude: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "repo_root": self.repo_root,
            "branch": self.branch,
            "core_changes": [asdict(x) for x in self.core_changes],
            "runtime_artifacts": [asdict(x) for x in self.runtime_artifacts],
            "junk_files": [asdict(x) for x in self.junk_files],
            "deploy_risks": [asdict(x) for x in self.deploy_risks],
            "recommended_git_add": self.recommended_git_add,
            "recommended_exclude": self.recommended_exclude,
            "notes": self.notes,
        }
