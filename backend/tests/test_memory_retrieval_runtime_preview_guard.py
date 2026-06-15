from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_PREVIEW = ROOT / "backend" / "app" / "memory_retrieval" / "runtime_preview.py"
THIS_FILE = Path(__file__).resolve()

REQUIRED_API_TERMS = (
    "MemoryRetrievalRuntimeRequest",
    "MemoryRetrievalRuntimeResponse",
    "build_memory_retrieval_preview",
    "dry_run",
    "block_reason",
    "context_pack",
    "audit_reason",
)

REQUIRED_PREVIEW_ONLY_TERMS = (
    "request.dry_run is not True",
    "ok=False",
    "blocked=True",
    "audit_reason",
    "request.query.strip()",
    "request.intent.strip()",
    "request.caller.strip()",
    "request.memory_root",
    'item.source_path.startswith("memory/")',
    "item.authority.strip()",
    "item.confidence.strip()",
)

REQUIRED_PIPELINE_TERMS = (
    "collect_memory_evidence",
    "build_context_pack",
    "ContextPack",
    "Path",
    "dataclass",
)

FORBIDDEN_IMPORT_PREFIX_PARTS = (
    ("backend", "app", "api"),
    ("backend", "app", "api", "tl_chat"),
    ("backend", "app", "atlas_engine", "governed_retrieval"),
    ("backend", "app", "services", "sequence_planner"),
    ("backend", "app", "services", "planner_smf"),
    ("backend", "app", "services"),
    ("fast", "api"),
    ("sql", "alchemy"),
    ("psycopg",),
    ("re", "quests"),
    ("url", "lib"),
    ("sub", "process"),
    ("sock", "et"),
    ("open", "ai"),
    ("anthropic",),
    ("ollama",),
    ("lite", "llm"),
    ("sqlite", "3"),
)

FORBIDDEN_TEXT_MARKER_PARTS = (
    ("write", "_text"),
    ("open", "("),
    ("Path", ".", "open"),
    ("unlink",),
    ("rename",),
    ("replace",),
    ("mkdir",),
    ("rmdir",),
    ("remove",),
    ("shutil",),
    ("os", ".", "remove"),
    ("os", ".", "rename"),
    ("os", ".", "system"),
    ("sub", "process"),
    ("commit",),
    ("push",),
    ("insert",),
    ("update",),
    ("delete",),
    ("execute",),
    ("session",),
    ("database",),
    ("SMF",),
    ("smf",),
    ("apply",),
)

FORBIDDEN_ENDPOINT_MARKERS = (
    "@router",
    "@app",
    "APIRouter",
    "FastAPI",
)

FORBIDDEN_DOMAIN_OR_BRIDGE_MARKERS = (
    "tl_chat",
    "governed_retrieval",
    "sequence_planner",
    "planner_smf",
    "planner",
    "ProductionEvent",
    "Order",
    "Route",
    "Station",
)

FORBIDDEN_CALL_NAMES = (
    "open",
    "exec",
    "eval",
    "compile",
    "__import__",
)

FORBIDDEN_DYNAMIC_CALL_NAMES = (
    "getattr",
)

FORBIDDEN_ATTRIBUTE_CALL_PARTS = (
    ("os", "system"),
    ("sub" + "process", "run"),
    ("sub" + "process", "Popen"),
)

FORBIDDEN_CLASS_OR_NAME_PARTS = (
    ("Router",),
    ("APIRouter",),
    ("FastAPI",),
    ("Session",),
    ("Engine",),
    ("Client",),
    ("LLM",),
    ("Planner",),
    ("TLChat",),
    ("Apply",),
    ("Mutation",),
)

FORBIDDEN_TEST_SIDE_EFFECT_PARTS = (
    ("sub", "process"),
    ("re", "quests"),
    ("url", "lib"),
    ("sock", "et"),
    ("tmp", "_path"),
    ("Temporary", "Directory"),
    ("Named", "Temporary", "File"),
    ("os", ".", "system"),
    ("git", " "),
)


def _runtime_text() -> str:
    return RUNTIME_PREVIEW.read_text(encoding="utf-8")


def _runtime_tree() -> ast.AST:
    return ast.parse(_runtime_text(), filename=str(RUNTIME_PREVIEW))


def _assert_contains_all(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        assert marker in text, f"missing {label}: {marker}"


def _imported_names(tree: ast.AST) -> list[str]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.append(node.module)
                names.extend(f"{node.module}.{alias.name}" for alias in node.names)
    return names


def _call_name(node: ast.Call) -> str:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        parts = [func.attr]
        value = func.value
        while isinstance(value, ast.Attribute):
            parts.append(value.attr)
            value = value.value
        if isinstance(value, ast.Name):
            parts.append(value.id)
        return ".".join(reversed(parts))
    return ""


def test_runtime_preview_file_exists():
    assert RUNTIME_PREVIEW.is_file()


def test_runtime_preview_contains_expected_api_terms():
    _assert_contains_all(_runtime_text(), REQUIRED_API_TERMS, "runtime preview API term")


def test_runtime_preview_remains_preview_only():
    _assert_contains_all(_runtime_text(), REQUIRED_PREVIEW_ONLY_TERMS, "preview-only guard")


def test_runtime_preview_uses_only_authorized_pipeline_terms():
    _assert_contains_all(_runtime_text(), REQUIRED_PIPELINE_TERMS, "authorized pipeline term")


def test_runtime_preview_has_no_forbidden_import_prefixes_by_text():
    text = _runtime_text()
    for parts in FORBIDDEN_IMPORT_PREFIX_PARTS:
        prefix = ".".join(parts)
        assert f"import {prefix}" not in text
        assert f"from {prefix}" not in text


def test_runtime_preview_has_no_forbidden_import_prefixes_by_ast():
    for imported in _imported_names(_runtime_tree()):
        for parts in FORBIDDEN_IMPORT_PREFIX_PARTS:
            prefix = ".".join(parts)
            assert not imported.startswith(prefix), f"forbidden import: {imported}"


def test_runtime_preview_has_no_mutation_or_write_markers():
    text = _runtime_text()
    for parts in FORBIDDEN_TEXT_MARKER_PARTS:
        marker = "".join(parts)
        assert marker not in text, f"forbidden mutation/write marker: {marker}"


def test_runtime_preview_has_no_endpoint_decorators_or_fastapi_markers():
    text = _runtime_text()
    for marker in FORBIDDEN_ENDPOINT_MARKERS:
        assert marker not in text, f"forbidden endpoint marker: {marker}"


def test_runtime_preview_has_no_tl_chat_planner_or_domain_bridge_markers():
    text = _runtime_text()
    for marker in FORBIDDEN_DOMAIN_OR_BRIDGE_MARKERS:
        assert marker not in text, f"forbidden bridge/domain marker: {marker}"


def test_runtime_preview_has_no_forbidden_calls_by_ast():
    for node in ast.walk(_runtime_tree()):
        if not isinstance(node, ast.Call):
            continue
        call_name = _call_name(node)
        assert call_name not in FORBIDDEN_CALL_NAMES, f"forbidden call: {call_name}"
        assert call_name not in FORBIDDEN_DYNAMIC_CALL_NAMES, f"forbidden dynamic call: {call_name}"
        for owner, attr in FORBIDDEN_ATTRIBUTE_CALL_PARTS:
            assert call_name != f"{owner}.{attr}", f"forbidden call: {call_name}"


def test_runtime_preview_has_no_suspicious_classes_or_names():
    forbidden_names = {"".join(parts) for parts in FORBIDDEN_CLASS_OR_NAME_PARTS}
    for node in ast.walk(_runtime_tree()):
        if isinstance(node, ast.ClassDef):
            assert node.name not in forbidden_names, f"forbidden class: {node.name}"
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            assert node.name not in forbidden_names, f"forbidden function: {node.name}"
        elif isinstance(node, ast.Name):
            assert node.id not in forbidden_names, f"forbidden name: {node.id}"


def test_runtime_preview_guard_is_static_only():
    test_text = THIS_FILE.read_text(encoding="utf-8")
    for parts in FORBIDDEN_TEST_SIDE_EFFECT_PARTS:
        marker = "".join(parts)
        assert marker not in test_text, f"guard contains forbidden side-effect marker: {marker}"
