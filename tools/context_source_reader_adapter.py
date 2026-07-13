from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ContextSourceReaderError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class ContextSourceReadResult:
    status: str
    source_id: str
    metadata: dict[str, Any]
    content: str | None = None


class ContextSourceReaderAdapter:
    """
    PROMETEO ContextSourceReaderAdapter read-only minimale.

    File-backed sources are resolved inside the repository. Logical registry
    sources are metadata-only, require no path, and never expose excerpts.
    """

    SOURCE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]+$")
    PATHLESS_SOURCE_KINDS = frozenset({"database_registry"})

    FORBIDDEN_PATH_PARTS = {
        ".env",
        "blocked",
        "node_modules",
        ".git",
    }

    def __init__(
        self,
        index_path: str | Path = "memory/context_source_index.json",
        repo_root: str | Path | None = None,
        max_chars: int = 2000,
    ) -> None:
        self.repo_root = Path(repo_root or Path.cwd()).resolve()
        self.index_path = self._resolve_inside_repo(Path(index_path))
        self.max_chars = max_chars
        self._index = self._load_index()
        self._sources = self._normalize_sources(self._index)

    def read_metadata(self, source_id: str) -> ContextSourceReadResult:
        source = self._get_source(source_id)
        if self._is_pathless_source(source):
            return ContextSourceReadResult(
                status="METADATA_OK",
                source_id=source_id,
                metadata=self._safe_pathless_metadata(source),
                content=None,
            )

        source_path = self._get_valid_source_path(source)
        return ContextSourceReadResult(
            status="METADATA_OK",
            source_id=source_id,
            metadata=self._safe_metadata(source, source_path),
            content=None,
        )

    def read_excerpt(self, source_id: str) -> ContextSourceReadResult:
        source = self._get_source(source_id)
        if self._is_pathless_source(source):
            raise ContextSourceReaderError(
                "SOURCE_EXCERPT_UNSUPPORTED",
                "Excerpt reading is not supported for logical registry sources.",
            )

        source_path = self._get_valid_source_path(source)
        if not source_path.exists() or not source_path.is_file():
            raise ContextSourceReaderError(
                "SOURCE_FILE_NOT_FOUND",
                "Source file not found or not readable.",
            )

        try:
            content = source_path.read_text(encoding="utf-8", errors="replace")
        except (PermissionError, OSError) as exc:
            raise ContextSourceReaderError(
                "SOURCE_FILE_NOT_FOUND",
                "Source file not found or not readable.",
            ) from exc

        limited = content[: self.max_chars]
        status = "CONTENT_LIMIT_APPLIED" if len(content) > self.max_chars else "READ_OK"

        return ContextSourceReadResult(
            status=status,
            source_id=source_id,
            metadata=self._safe_metadata(source, source_path),
            content=limited,
        )

    def _load_index(self) -> dict[str, Any]:
        if not self.index_path.exists():
            raise ContextSourceReaderError(
                "INDEX_NOT_FOUND",
                "Context Source Index not found.",
            )

        try:
            with self.index_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            raise ContextSourceReaderError(
                "INDEX_INVALID",
                "Context Source Index is invalid.",
            ) from exc
        except (PermissionError, OSError) as exc:
            raise ContextSourceReaderError(
                "INDEX_NOT_FOUND",
                "Context Source Index not found or not readable.",
            ) from exc

        if not isinstance(data, dict):
            raise ContextSourceReaderError(
                "INDEX_INVALID",
                "Context Source Index must be a JSON object.",
            )

        return data

    def _normalize_sources(self, index: dict[str, Any]) -> dict[str, dict[str, Any]]:
        raw_sources = (
            index.get("sources")
            or index.get("context_sources")
            or index.get("items")
            or {}
        )
        normalized: dict[str, dict[str, Any]] = {}

        if isinstance(raw_sources, dict):
            for source_id, source in raw_sources.items():
                if isinstance(source, dict):
                    normalized[str(source_id)] = dict(source, source_id=str(source_id))
        elif isinstance(raw_sources, list):
            for source in raw_sources:
                if not isinstance(source, dict):
                    continue
                source_id = source.get("source_id") or source.get("id") or source.get("name")
                if source_id:
                    normalized[str(source_id)] = source

        if not normalized:
            raise ContextSourceReaderError(
                "NO_SOURCES_DECLARED",
                "No context sources declared in index.",
            )

        return normalized

    def _get_source(self, source_id: str) -> dict[str, Any]:
        self._validate_source_id(source_id)
        source = self._sources.get(source_id)
        if not source:
            raise ContextSourceReaderError(
                "SOURCE_NOT_FOUND",
                "Source ID not found in Context Source Index.",
            )

        if source.get("access_mode", "read_only") != "read_only":
            raise ContextSourceReaderError(
                "SOURCE_NOT_ALLOWED",
                "Source is not declared as read_only.",
            )

        if source.get("runtime_enabled") is True:
            raise ContextSourceReaderError(
                "RUNTIME_SOURCE_BLOCKED",
                "Runtime-enabled sources are not allowed in this adapter.",
            )

        if self._is_pathless_source(source):
            raw_path = source.get("path") or source.get("relative_path")
            if isinstance(raw_path, str) and raw_path.strip():
                raise ContextSourceReaderError(
                    "NON_FILE_SOURCE_PATH_FORBIDDEN",
                    "Logical registry sources must not declare a filesystem path.",
                )

        return source

    def _validate_source_id(self, source_id: str) -> None:
        if not source_id or not isinstance(source_id, str):
            raise ContextSourceReaderError(
                "SOURCE_ID_INVALID",
                "Source ID must be a non-empty string.",
            )

        if "/" in source_id or "\\" in source_id or ".." in source_id:
            raise ContextSourceReaderError(
                "SOURCE_ID_INVALID",
                "Source ID must be logical and must not contain path fragments.",
            )

        if not self.SOURCE_ID_PATTERN.match(source_id):
            raise ContextSourceReaderError(
                "SOURCE_ID_INVALID",
                "Source ID contains forbidden characters.",
            )

    def _is_pathless_source(self, source: dict[str, Any]) -> bool:
        return source.get("kind") in self.PATHLESS_SOURCE_KINDS

    def _safe_pathless_metadata(self, source: dict[str, Any]) -> dict[str, Any]:
        return {
            "schema": "CONTEXT_SOURCE_READER_ADAPTER_READONLY_001",
            "source_type": source.get("source_type") or source.get("kind"),
            "kind": source.get("kind"),
            "access_mode": source.get("access_mode", "read_only"),
            "runtime_enabled": source.get("runtime_enabled", False),
            "relative_path": None,
            "locator_mode": "logical_registry",
            "structural_origin": source.get("structural_origin"),
            "exists": bool(source.get("exists")),
        }

    def _get_valid_source_path(self, source: dict[str, Any]) -> Path:
        raw_path = (
            source.get("path")
            or source.get("relative_path")
            or source.get("file_path")
            or source.get("source_path")
        )

        if not raw_path or not isinstance(raw_path, str):
            raise ContextSourceReaderError(
                "SOURCE_PATH_MISSING",
                "Source path missing in Context Source Index.",
            )

        source_path = self._resolve_inside_repo(Path(raw_path))
        self._block_forbidden_path(source_path)
        return source_path

    def _resolve_inside_repo(self, path: Path) -> Path:
        candidate = path if path.is_absolute() else self.repo_root / path
        resolved = candidate.resolve()

        try:
            resolved.relative_to(self.repo_root)
        except ValueError as exc:
            raise ContextSourceReaderError(
                "PATH_TRAVERSAL_BLOCKED",
                "Resolved path is outside repository root.",
            ) from exc

        return resolved

    def _block_forbidden_path(self, path: Path) -> None:
        relative_parts = {part.lower() for part in path.relative_to(self.repo_root).parts}
        if relative_parts & self.FORBIDDEN_PATH_PARTS:
            raise ContextSourceReaderError(
                "FORBIDDEN_PATH_BLOCKED",
                "Source path is explicitly forbidden.",
            )

    def _safe_metadata(self, source: dict[str, Any], source_path: Path) -> dict[str, Any]:
        relative_path = str(source_path.relative_to(self.repo_root))

        try:
            exists = source_path.exists()
        except (PermissionError, OSError) as exc:
            raise ContextSourceReaderError(
                "SOURCE_FILE_NOT_FOUND",
                "Source file not found or not readable.",
            ) from exc

        return {
            "schema": "CONTEXT_SOURCE_READER_ADAPTER_READONLY_001",
            "source_type": source.get("source_type"),
            "kind": source.get("kind"),
            "access_mode": source.get("access_mode", "read_only"),
            "runtime_enabled": source.get("runtime_enabled", False),
            "relative_path": relative_path,
            "locator_mode": "repository_path",
            "exists": exists,
        }
