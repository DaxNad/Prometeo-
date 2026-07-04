from __future__ import annotations

import argparse
import ast
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


DEFAULT_TARGET = Path("backend/app/api/tl_chat.py")
TARGET_FUNCTION = "_build_contract_response"


@dataclass(frozen=True)
class ReturnInventoryItem:
    line: int
    expression_type: str
    target: str
    direct_tl_chat_response: bool
    resolver_reference_in_expression: bool
    source_excerpt: str


def _call_name(node: ast.AST | None) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def _contains_name(node: ast.AST, name: str) -> bool:
    return any(isinstance(child, ast.Name) and child.id == name for child in ast.walk(node))


def _source_excerpt(lines: list[str], node: ast.AST) -> str:
    start = max(getattr(node, "lineno", 1) - 1, 0)
    end = min(getattr(node, "end_lineno", getattr(node, "lineno", 1)), len(lines))
    return " ".join(line.strip() for line in lines[start:end] if line.strip())


def _classify_return(node: ast.Return, lines: list[str]) -> ReturnInventoryItem:
    value = node.value
    expression_type = type(value).__name__ if value is not None else "None"
    target = ""
    direct_tl_chat_response = False

    if isinstance(value, ast.Call):
        target = _call_name(value.func)
        direct_tl_chat_response = target == "TLChatResponse"
    elif isinstance(value, ast.Name):
        target = value.id
    elif value is None:
        target = "None"

    return ReturnInventoryItem(
        line=node.lineno,
        expression_type=expression_type,
        target=target,
        direct_tl_chat_response=direct_tl_chat_response,
        resolver_reference_in_expression=(
            _contains_name(value, "resolve_tl_chat_context") if value is not None else False
        ),
        source_excerpt=_source_excerpt(lines, node),
    )


def build_inventory(path: Path) -> dict[str, Any]:
    source = path.read_text(encoding="utf-8")
    lines = source.splitlines()
    tree = ast.parse(source, filename=str(path))

    function = next(
        (
            node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == TARGET_FUNCTION
        ),
        None,
    )
    if function is None:
        raise ValueError(f"function_not_found:{TARGET_FUNCTION}")

    returns = [
        _classify_return(node, lines)
        for node in ast.walk(function)
        if isinstance(node, ast.Return)
    ]
    returns.sort(key=lambda item: item.line)

    direct = [item for item in returns if item.direct_tl_chat_response]
    helper = [
        item
        for item in returns
        if item.target and not item.direct_tl_chat_response and item.target != "None"
    ]

    return {
        "schema": "TL_CHAT_SOURCE_NORMALIZATION_AUDIT_V1",
        "mode": "READ_ONLY_NON_BLOCKING",
        "target_file": str(path),
        "target_function": TARGET_FUNCTION,
        "summary": {
            "return_count": len(returns),
            "direct_tl_chat_response_count": len(direct),
            "helper_or_variable_return_count": len(helper),
        },
        "returns": [asdict(item) for item in returns],
        "notes": [
            "This is an implementation inventory, not a correctness test.",
            "Direct TLChatResponse construction does not by itself prove a runtime defect.",
            "Resolver use inside called helper functions is intentionally not inferred.",
            "The command exits with status 0 when the audit completes successfully.",
        ],
    }


def render_text(inventory: dict[str, Any]) -> str:
    summary = inventory["summary"]
    output = [
        "TL Chat source normalization audit",
        f"Target: {inventory['target_file']}::{inventory['target_function']}",
        "Mode: READ_ONLY_NON_BLOCKING",
        "",
        f"Returns: {summary['return_count']}",
        f"Direct TLChatResponse: {summary['direct_tl_chat_response_count']}",
        f"Helper/variable returns: {summary['helper_or_variable_return_count']}",
        "",
    ]

    for item in inventory["returns"]:
        classification = "DIRECT_TL_CHAT_RESPONSE" if item["direct_tl_chat_response"] else "DELEGATED_OR_VARIABLE"
        output.append(
            f"L{item['line']}: {classification} target={item['target'] or '-'}"
        )
        output.append(f"  {item['source_excerpt']}")

    output.extend(["", "Notes:"])
    output.extend(f"- {note}" for note in inventory["notes"])
    return "\n".join(output)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only, non-blocking inventory of return branches in "
            "_build_contract_response()."
        )
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_TARGET,
        help=f"Path to tl_chat.py (default: {DEFAULT_TARGET})",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    args = parser.parse_args()

    inventory = build_inventory(args.path)
    if args.format == "json":
        print(json.dumps(inventory, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_text(inventory))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
