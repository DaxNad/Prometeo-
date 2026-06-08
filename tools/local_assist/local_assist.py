#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = REPO_ROOT / "tools" / "local_assist" / "policy.json"
SYSTEM_PROMPT_PATH = REPO_ROOT / "tools" / "local_assist" / "prompts" / "system.txt"


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_policy() -> dict:
    return json.loads(load_text(POLICY_PATH))


def build_prompt(task: str, terminal_text: str) -> str:
    policy = load_policy()
    system_prompt = load_text(SYSTEM_PROMPT_PATH)

    return (
        f"{system_prompt}\n\n"
        f"POLICY_JSON:\n{json.dumps(policy, ensure_ascii=False, indent=2)}\n\n"
        f"TASK:\n{task}\n\n"
        f"TERMINAL_OUTPUT:\n{terminal_text}\n\n"
        "Restituisci solo JSON valido con chiavi: "
        "verdict, risk, summary, suggested_next_command, requires_human_confirmation."
    )


def deterministic_fallback(task: str, terminal_text: str) -> dict | None:
    lowered = terminal_text.lower()

    if "all checks were successful" in lowered and "0 failing" in lowered:
        return {
            "verdict": "PASS",
            "risk": "LOW",
            "summary": "Tutti i check risultano verdi.",
            "suggested_next_command": None,
            "requires_human_confirmation": True,
        }

    if "data leak guard" in lowered and ("failing" in lowered or "not successful" in lowered or "violation" in lowered):
        return {
            "verdict": "FAIL",
            "risk": "HIGH",
            "summary": "Data Leak Guard risulta fallito. Leggere il log fallito prima di qualunque patch.",
            "suggested_next_command": "gh run view <RUN_ID> --log-failed",
            "requires_human_confirmation": True,
        }

    if "privacy guard" in lowered and ("failing" in lowered or "not successful" in lowered or "violation" in lowered):
        return {
            "verdict": "FAIL",
            "risk": "HIGH",
            "summary": "Privacy Guard risulta fallito. Leggere il log fallito prima di qualunque patch.",
            "suggested_next_command": "gh run view <RUN_ID> --log-failed",
            "requires_human_confirmation": True,
        }

    return None


def call_ollama(model: str, prompt: str) -> str:
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt,
        text=True,
        capture_output=True,
        check=False,
        timeout=60,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ollama failed")

    return result.stdout.strip()


FORBIDDEN_COMMAND_PATTERNS = (
    "git push origin main",
    "git push",
    "git merge",
    "gh pr merge",
    "rm -rf",
    "cat .env",
    "printenv",
    "open ~/.ssh",
)


def command_is_forbidden(command: object) -> bool:
    if command is None:
        return False
    if not isinstance(command, str):
        return True
    normalized = command.strip().lower()
    return any(pattern in normalized for pattern in FORBIDDEN_COMMAND_PATTERNS)


def extract_json_object(raw: str) -> str:
    stripped = raw.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end > start:
        return stripped[start : end + 1]

    return stripped


def validate_output(raw: str) -> dict:
    candidate = extract_json_object(raw)
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError as exc:
        return {
            "verdict": "DA_VERIFICARE",
            "risk": "HIGH",
            "summary": f"Ollama non ha restituito JSON valido: {exc}",
            "suggested_next_command": None,
            "requires_human_confirmation": True,
        }

    required = {
        "verdict",
        "risk",
        "summary",
        "suggested_next_command",
        "requires_human_confirmation",
    }

    missing = sorted(required - set(data))
    if missing:
        return {
            "verdict": "DA_VERIFICARE",
            "risk": "HIGH",
            "summary": f"Output incompleto. Campi mancanti: {missing}",
            "suggested_next_command": None,
            "requires_human_confirmation": True,
        }

    if data["verdict"] not in {"PASS", "FAIL", "DA_VERIFICARE"}:
        data["verdict"] = "DA_VERIFICARE"
        data["risk"] = "HIGH"
        data["requires_human_confirmation"] = True

    if data["risk"] not in {"LOW", "MEDIUM", "HIGH"}:
        data["risk"] = "HIGH"
        data["requires_human_confirmation"] = True

    if command_is_forbidden(data.get("suggested_next_command")):
        data["verdict"] = "DA_VERIFICARE"
        data["risk"] = "HIGH"
        data["summary"] = "Comando suggerito bloccato dalla policy locale."
        data["suggested_next_command"] = None

    data["requires_human_confirmation"] = True
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="PROMETEO local assist bridge proposal-only CLI")
    parser.add_argument("--task", required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--input-file", required=True)
    args = parser.parse_args()

    policy = load_policy()
    model = args.model or policy["default_model"]
    terminal_text = load_text(Path(args.input_file))

    fallback = deterministic_fallback(args.task, terminal_text)
    if fallback is not None:
        print(json.dumps(fallback, ensure_ascii=False, indent=2))
        return 0

    prompt = build_prompt(args.task, terminal_text)
    try:
        raw = call_ollama(model, prompt)
        validated = validate_output(raw)
    except Exception as exc:
        validated = {
            "verdict": "DA_VERIFICARE",
            "risk": "HIGH",
            "summary": f"Ollama non disponibile o errore runtime: {exc}",
            "suggested_next_command": None,
            "requires_human_confirmation": True,
        }

    print(json.dumps(validated, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
