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


def call_ollama(prompt: str, model: str, timeout: int) -> str:
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

    with urllib.request.urlopen(req, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))

    return str(data.get("response", "")).strip()



def _safe_read(path: Path, max_chars: int = 6000) -> str:
    try:
        if not path.exists() or not path.is_file():
            return ""
        rel = str(path.relative_to(REPO_ROOT))
        if any(rel.startswith(x) for x in FORBIDDEN_PATHS):
            return ""
        return path.read_text(encoding="utf-8", errors="replace")[:max_chars]
    except Exception:
        return ""


def _repo_candidate_files() -> list[Path]:
    roots = [
        REPO_ROOT / "backend" / "app",
        REPO_ROOT / "backend" / "tests",
        REPO_ROOT / "docs",
        REPO_ROOT / "tools",
    ]
    suffixes = {".py", ".md", ".json", ".txt"}

    files: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in suffixes:
                continue
            rel = str(path.relative_to(REPO_ROOT))
            if any(rel.startswith(x) for x in FORBIDDEN_PATHS):
                continue
            if "__pycache__" in rel or ".pytest_cache" in rel:
                continue
            files.append(path)
    return files


def _goal_terms(user_goal: str) -> set[str]:
    raw = user_goal.lower().replace("/", " ").replace("-", " ").replace("_", " ")
    return {x for x in raw.split() if len(x) >= 3}


def _score_file(path: Path, terms: set[str]) -> int:
    rel = str(path.relative_to(REPO_ROOT)).lower()
    content = _safe_read(path, max_chars=2000).lower()
    score = 0

    for term in terms:
        if term in rel:
            score += 8
        if term in content:
            score += 2

    if "test" in terms and "backend/tests" in rel:
        score += 5
    if "api" in terms and "backend/app/api" in rel:
        score += 5
    if "service" in terms and "backend/app/services" in rel:
        score += 5
    if "pattern" in terms and "pattern" in rel:
        score += 8
    if "local" in terms and "tools/local_llm" in rel:
        score += 8

    return score


def select_repo_context(user_goal: str, limit: int = 4) -> tuple[str, list[str]]:
    terms = _goal_terms(user_goal)
    scored: list[tuple[int, Path]] = []

    for path in _repo_candidate_files():
        score = _score_file(path, terms)
        if score > 0:
            scored.append((score, path))

    scored.sort(key=lambda item: (-item[0], str(item[1])))

    sections: list[str] = []
    selected_files: list[str] = []

    for score, path in scored[:limit]:
        rel = str(path.relative_to(REPO_ROOT))
        content = _safe_read(path)
        if content:
            selected_files.append(rel)
            sections.append(f"--- FILE: {rel} | score={score} ---\n{content}")

    if not sections:
        return "No specific repository context selected.", []

    return "\n\n".join(sections), selected_files


def collect_repo_context(user_goal: str) -> str:
    context, _files = select_repo_context(user_goal)
    return context



def suggest_pytest_command(selected_files: list[str]) -> str:
    test_files = [
        file for file in selected_files
        if file.startswith("backend/tests/") and file.endswith(".py")
    ]

    if test_files:
        return "python3 -m pytest " + " ".join(test_files) + " -q"

    if any(file.startswith("backend/app/api/") for file in selected_files):
        return "python3 -m pytest backend/tests/test_tl_chat_contract.py backend/tests/test_pattern_learning_registry.py -q"

    if any(file.startswith("tools/local_llm/") for file in selected_files):
        return "python3 tools/local_llm/prometeo_local_editor.py --help"

    return "python3 -m pytest backend/tests/test_tl_chat_contract.py -q"

def build_controlled_prompt(user_goal: str) -> str:
    repo_context, selected_files = select_repo_context(user_goal)
    allowed_files = "\n".join("- " + file for file in selected_files) or "- none"
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

PROMETEO technical context:

- Stack: Python + FastAPI.
- Backend source: backend/app/
- Tests: pytest under backend/tests/
- API routers: backend/app/api/
- Services: backend/app/services/
- Domain logic: backend/app/domain/
- NEVER propose PHP.
- NEVER propose Laravel.
- NEVER propose controllers.php patterns.
- NEVER propose PHPUnit or backend/tests/Unit/.
- Use PROMETEO repository conventions only.

Allowed areas:
{chr(10).join("- " + x for x in ALLOWED_HINTS)}

Auto-detected allowed files for this goal:
{allowed_files}

Repository context:
{repo_context}

User goal:
{user_goal}

Return:
1. Scope
2. Auto-detected allowed files
3. Proposed patch summary
4. Proposed unified diff preview
5. Risk summary
6. Suggested pytest command
7. Human confirmation checklist
8. Explicit confirmation that this is dry-run only

Unified diff rules:
- Return patch as preview text only.
- Do not claim files were written.
- Use repository-relative paths.
- Do not include .env, specs_finitura, data/local_smf, logs or dumps.
- Prefer minimal diffs.
- Only propose edits for auto-detected allowed files.
- If the needed file is not listed, say that human scope update is required.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="PROMETEO local LLM editor dry-run tool.")
    parser.add_argument("goal", nargs="+", help="Editing goal for local LLM dry-run.")
    parser.add_argument("--model", default="mistral", help="Ollama model name. Default: mistral.")
    parser.add_argument("--timeout", type=int, default=120, help="Ollama timeout seconds. Default: 120.")
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Skip Ollama and print deterministic local scope/test guidance only.",
    )
    args = parser.parse_args()

    goal = " ".join(args.goal).strip()
    guard_prompt(goal)
    assert_clean_main_safe()

    _context, selected_files = select_repo_context(goal)
    pytest_command = suggest_pytest_command(selected_files)
    prompt = build_controlled_prompt(goal)

    print("== PROMETEO LOCAL LLM EDITOR ==")
    print("mode: DRY-RUN ONLY")
    print(f"model: {args.model}")
    print(f"timeout: {args.timeout}s")
    print("selected files:")
    if selected_files:
        for file in selected_files:
            print(f"- {file}")
    else:
        print("- none")
    print()

    if args.no_llm:
        print("== DETERMINISTIC LOCAL SCOPE ==")
        print("goal:")
        print(goal)
        print()
        print("allowed files:")
        if selected_files:
            for file in selected_files:
                print(f"- {file}")
        else:
            print("- none")
        print()
        print("risk summary:")
        print("- no LLM call")
        print("- no files written")
        print("- no commit/push/merge")
        print("- human review required before any patch")
    else:
        try:
            response = call_ollama(prompt, args.model, args.timeout)
        except Exception as exc:
            fail(f"Ollama call failed: {exc}")

        print(response)

    print()
    print("== AUTHORITATIVE TEST COMMAND ==")
    print(pytest_command)
    print("== PATCH PREVIEW ONLY ==")
    print("== NO FILES WRITTEN ==")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
