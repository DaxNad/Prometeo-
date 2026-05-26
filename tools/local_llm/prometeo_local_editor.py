#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_PATHS = (
    ".env",
    "specs_finitura/",
    "data/local_smf/",
    "data/pattern_registry/",
    "logs/",
    "dumps/",
)

ALLOWED_HINTS = (
    "backend/app/",
    "backend/tests/",
    "docs/",
    "tools/local_llm/",
)


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, cwd=REPO_ROOT, text=True)


def fail(msg: str) -> None:
    print(f"[BLOCKED] {msg}", file=sys.stderr)
    raise SystemExit(2)


def assert_clean_main_safe() -> None:
    branch = run(["git", "branch", "--show-current"]).strip()
    if branch == "main":
        fail("Do not run local LLM editor on main. Create a dedicated branch first.")


def guard_prompt(prompt: str) -> None:
    lowered = prompt.lower()
    if any(token in lowered for token in ("commit", "push", "merge", ".env", "secret", "password", "token")):
        fail("Prompt requests forbidden operation or sensitive material.")


def call_ollama(prompt: str, model: str) -> str:
    payload = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1},
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))

    return str(data.get("response", "")).strip()


def build_controlled_prompt(user_goal: str) -> str:
    return f"""PROMETEO LOCAL LLM EDITOR — DRY RUN ONLY

You are a local editing assistant for PROMETEO.

Hard rules:
- Do not write files.
- Do not commit.
- Do not push.
- Do not open PRs.
- Do not touch .env, specs_finitura, data/local_smf, runtime registry data, logs, dumps, secrets.
- Propose only a safe plan and patch-style guidance.
- Respect PROMETEO Pattern Learning as primary objective.

Allowed areas:
{chr(10).join("- " + x for x in ALLOWED_HINTS)}

User goal:
{user_goal}

Return:
1. Scope
2. Files likely involved
3. Proposed patch summary
4. Risks
5. Tests to run
6. Explicit confirmation that this is dry-run only
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="PROMETEO local LLM editor dry-run tool.")
    parser.add_argument("goal", nargs="+", help="Editing goal for local LLM dry-run.")
    parser.add_argument("--model", default="mistral", help="Ollama model name. Default: mistral.")
    args = parser.parse_args()

    goal = " ".join(args.goal).strip()
    guard_prompt(goal)
    assert_clean_main_safe()

    prompt = build_controlled_prompt(goal)

    print("== PROMETEO LOCAL LLM EDITOR ==")
    print("mode: DRY-RUN ONLY")
    print(f"model: {args.model}")
    print()

    try:
        response = call_ollama(prompt, args.model)
    except Exception as exc:
        fail(f"Ollama call failed: {exc}")

    print(response)
    print()
    print("== NO FILES WRITTEN ==")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
