from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Any


class DataClass(StrEnum):
    PUBLIC_CODE = "PUBLIC_CODE"
    PROJECT_INTERNAL = "PROJECT_INTERNAL"
    OPERATIONAL_REAL = "OPERATIONAL_REAL"
    INDUSTRIAL_SENSITIVE = "INDUSTRIAL_SENSITIVE"
    PERSONAL = "PERSONAL"
    SECRET = "SECRET"


class RiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


_LOCAL_USER_PATH_PATTERN = re.compile(
    r"(?i)(?:^|\s)(?:/" "Users" r"/|/home/|[A-Z]:\\)[^\s'\"<>]+"
)
_EMAIL_PATTERN = re.compile(
    r"[A-Za-z0-9._%+-]+" "@" r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)
_SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|secret|token|password|passwd|private[_-]?key)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"(?i)(postgresql|postgres|mysql|mongodb)://(?!localhost/|127\.0\.0\.1/)[^\s'\"<>]+"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{20,}"),
    re.compile(r"(?i)DATABASE_URL\s*="),
)
_REAL_ARTICLE_PATTERN = re.compile(r"\b\d{5}[A-Z]{0,3}\b")
_REAL_COMPONENT_PATTERN = re.compile(r"\b\d{6}\b")

_INDUSTRIAL_TOKENS = (
    "specs_finitura",
    "specifica",
    "specifiche",
    "bom",
    "smf",
    "data/local_smf",
    "BOM_Specs",
)
_OPERATIONAL_TOKENS = (
    "route",
    "stazione",
    "station",
    "zaw",
    "pidmill",
    "henn",
    "forno",
    "ultrasuoni",
    "wintec",
    "ordine cliente",
)
_REAL_ASSET_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".pdf",
    ".xlsx",
    ".xls",
    ".xlsm",
    ".csv",
}
_SENSITIVE_ROOTS = (
    "specs_finitura",
    "data/local_smf",
)


@dataclass(frozen=True)
class DataBoundaryClassification:
    allowed_external: bool
    risk_level: RiskLevel
    detected_classes: tuple[DataClass, ...] = field(default_factory=tuple)
    reasons: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["risk_level"] = self.risk_level.value
        data["detected_classes"] = [item.value for item in self.detected_classes]
        data["reasons"] = list(self.reasons)
        return data


def classify_data_boundary(
    text: str | None = None,
    *,
    file_path: str | None = None,
    scope_declared: bool = False,
) -> dict[str, Any]:
    content = str(text or "")
    path = str(file_path or "")
    detected: set[DataClass] = set()
    reasons: list[str] = []

    _classify_text(content, detected, reasons)
    if path:
        _classify_path(path, detected, reasons)

    if not detected:
        detected.add(DataClass.PUBLIC_CODE)

    if not scope_declared:
        reasons.append("scope_not_declared")

    allowed_external = (
        detected.issubset({DataClass.PUBLIC_CODE, DataClass.PROJECT_INTERNAL})
        and "secret_detected" not in reasons
        and "real_asset_detected" not in reasons
        and scope_declared
    )
    risk_level = _risk_level(detected, reasons)

    return DataBoundaryClassification(
        allowed_external=allowed_external,
        risk_level=risk_level,
        detected_classes=tuple(sorted(detected, key=lambda item: item.value)),
        reasons=tuple(_dedupe(reasons)),
    ).to_dict()


def _classify_text(content: str, detected: set[DataClass], reasons: list[str]) -> None:
    lowered = content.lower()

    if _LOCAL_USER_PATH_PATTERN.search(content):
        detected.add(DataClass.PERSONAL)
        reasons.append("local_path_detected")

    if _EMAIL_PATTERN.search(content):
        detected.add(DataClass.PERSONAL)
        reasons.append("email_detected")

    if any(pattern.search(content) for pattern in _SECRET_PATTERNS):
        detected.add(DataClass.SECRET)
        reasons.append("secret_detected")

    if any(token.lower() in lowered for token in _INDUSTRIAL_TOKENS):
        detected.add(DataClass.INDUSTRIAL_SENSITIVE)
        reasons.append("industrial_reference_detected")

    if any(token in lowered for token in _OPERATIONAL_TOKENS):
        detected.add(DataClass.OPERATIONAL_REAL)
        reasons.append("operational_reference_detected")

    if _REAL_ARTICLE_PATTERN.search(content):
        detected.add(DataClass.OPERATIONAL_REAL)
        reasons.append("article_code_detected")

    if _REAL_COMPONENT_PATTERN.search(content):
        detected.add(DataClass.OPERATIONAL_REAL)
        reasons.append("component_code_detected")

    if _looks_project_internal(lowered, detected):
        detected.add(DataClass.PROJECT_INTERNAL)


def _classify_path(path: str, detected: set[DataClass], reasons: list[str]) -> None:
    normalized = path.replace("\\", "/")
    lowered = normalized.lower()
    suffix = PurePosixPath(normalized).suffix.lower()

    if _LOCAL_USER_PATH_PATTERN.search(" " + normalized):
        detected.add(DataClass.PERSONAL)
        reasons.append("local_path_detected")

    if any(lowered.startswith(root + "/") or f"/{root}/" in lowered for root in _SENSITIVE_ROOTS):
        detected.add(DataClass.INDUSTRIAL_SENSITIVE)
        reasons.append("sensitive_root_detected")

    if suffix in _REAL_ASSET_SUFFIXES:
        detected.add(DataClass.INDUSTRIAL_SENSITIVE)
        reasons.append("real_asset_detected")

    if ".env" in PurePosixPath(normalized).name.lower():
        detected.add(DataClass.SECRET)
        reasons.append("secret_detected")


def _looks_project_internal(lowered: str, detected: set[DataClass]) -> bool:
    return (
        "prometeo" in lowered
        and not detected.intersection(
            {
                DataClass.OPERATIONAL_REAL,
                DataClass.INDUSTRIAL_SENSITIVE,
                DataClass.PERSONAL,
                DataClass.SECRET,
            }
        )
    )


def _risk_level(detected: set[DataClass], reasons: list[str]) -> RiskLevel:
    if DataClass.SECRET in detected:
        return RiskLevel.CRITICAL
    if detected.intersection({DataClass.INDUSTRIAL_SENSITIVE, DataClass.PERSONAL}):
        return RiskLevel.HIGH
    if DataClass.OPERATIONAL_REAL in detected or "scope_not_declared" in reasons:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            output.append(item)
    return output
