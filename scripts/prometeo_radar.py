#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import pandas as pd
except Exception:  # pragma: no cover
    pd = None


ROOT = Path(__file__).resolve().parents[1]
SMF_BASE = ROOT / "data" / "local_smf"
SMF_MASTER = SMF_BASE / "SuperMegaFile_Master.xlsx"
LIFECYCLE_REGISTRY = SMF_BASE / "article_lifecycle_registry.json"
MASTER_DOC = ROOT / "docs" / "PROMETEO_MASTER.md"
REAL_INGEST = ROOT / "backend" / "app" / "api" / "real_ingest.py"
TL_CHAT = ROOT / "backend" / "app" / "api" / "tl_chat.py"


def _run(cmd: list[str], *, timeout: int = 8) -> tuple[int, str]:
    try:
        res = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except Exception as exc:
        return 1, str(exc)

    out = (res.stdout or "").strip()
    err = (res.stderr or "").strip()
    return res.returncode, out or err


def _git_info() -> dict[str, Any]:
    _, branch = _run(["git", "branch", "--show-current"])
    _, commit = _run(["git", "log", "--oneline", "-1"])
    _, status = _run(["git", "status", "--short"])

    return {
        "branch": branch or "UNKNOWN",
        "last_commit": commit or "UNKNOWN",
        "working_tree": "clean" if not status else "dirty",
        "changed_files": status.splitlines() if status else [],
    }


def _ollama_info() -> dict[str, Any]:
    code, version = _run(["ollama", "--version"], timeout=5)
    if code != 0:
        return {
            "available": False,
            "version": None,
            "models": [],
            "error": version,
        }

    code, tags_raw = _run(
        [
            "curl",
            "--max-time",
            "5",
            "-s",
            "http://127.0.0.1:11434/api/tags",
        ],
        timeout=8,
    )

    models: list[str] = []
    if code == 0 and tags_raw:
        try:
            parsed = json.loads(tags_raw)
            models = [
                str(item.get("name"))
                for item in parsed.get("models", [])
                if item.get("name")
            ]
        except Exception:
            models = []

    return {
        "available": True,
        "version": version,
        "models": models,
        "server_running": bool(models),
    }


def _sheet_count(sheet: str) -> int | None:
    if pd is None or not SMF_MASTER.exists():
        return None

    try:
        df = pd.read_excel(SMF_MASTER, sheet_name=sheet)
    except Exception:
        return None

    return int(len(df))


def _smf_info() -> dict[str, Any]:
    info: dict[str, Any] = {
        "base_path": str(SMF_BASE),
        "master_path": str(SMF_MASTER),
        "master_exists": SMF_MASTER.exists(),
        "sheets": [],
        "counts": {},
        "bom_articles_not_in_codici": None,
    }

    if pd is None:
        info["error"] = "pandas not available"
        return info

    if not SMF_MASTER.exists():
        return info

    try:
        xls = pd.ExcelFile(SMF_MASTER)
    except Exception as exc:
        info["error"] = f"workbook not readable: {exc}"
        return info

    info["sheets"] = list(xls.sheet_names)

    for sheet in ("Codici", "BOM_Specs", "BOM_Components", "BOM_Operations", "BOM_Controls"):
        info["counts"][sheet] = _sheet_count(sheet)

    try:
        codici = pd.read_excel(SMF_MASTER, sheet_name="Codici").fillna("")
        specs = pd.read_excel(SMF_MASTER, sheet_name="BOM_Specs").fillna("")

        codici_set = set()
        if "Codice" in codici.columns:
            codici_set = {
                str(v).strip().upper()
                for v in codici["Codice"].tolist()
                if str(v).strip()
            }

        bom_set = set()
        if "articolo" in specs.columns:
            bom_set = {
                str(v).strip().upper()
                for v in specs["articolo"].tolist()
                if str(v).strip()
            }

        missing = sorted(bom_set - codici_set)
        info["bom_articles_not_in_codici"] = len(missing)
        info["bom_articles_not_in_codici_sample"] = missing[:12]
    except Exception:
        pass

    return info



def _lifecycle_info() -> dict[str, Any]:
    info: dict[str, Any] = {
        "path": str(LIFECYCLE_REGISTRY),
        "exists": LIFECYCLE_REGISTRY.exists(),
        "total": 0,
        "by_status": {},
        "sample": [],
    }

    if not LIFECYCLE_REGISTRY.exists():
        return info

    try:
        data = json.loads(LIFECYCLE_REGISTRY.read_text(encoding="utf-8"))
    except Exception as exc:
        info["error"] = str(exc)
        return info

    if not isinstance(data, dict):
        info["error"] = "registry not object"
        return info

    info["total"] = len(data)

    by_status: dict[str, int] = {}
    sample: list[str] = []

    for code, payload in sorted(data.items()):
        status = "SCONOSCIUTO"
        if isinstance(payload, dict):
            status = str(payload.get("status") or "SCONOSCIUTO").strip().upper()

        by_status[status] = by_status.get(status, 0) + 1

        if len(sample) < 12:
            sample.append(str(code))

    info["by_status"] = by_status
    info["sample"] = sample
    return info


def _real_ingest_info() -> dict[str, Any]:
    text = REAL_INGEST.read_text(encoding="utf-8") if REAL_INGEST.exists() else ""

    return {
        "file_exists": REAL_INGEST.exists(),
        "preview_endpoint": '"/real/ingest-order"' in text or '"/real/ingest-order",' in text,
        "article_profile_endpoint": '"/real/article-profile/{article}"' in text,
        "uses_smf_reader": "SMFReader" in text,
        "uses_article_profile_builder": "build_article_pilot_profile_from_reader" in text,
        "mentions_smf_adapter_bootstrap": "SMFAdapter(" in text,
    }



def _tl_chat_info() -> dict[str, Any]:
    text = TL_CHAT.read_text(encoding="utf-8") if TL_CHAT.exists() else ""

    return {
        "file_exists": TL_CHAT.exists(),
        "endpoint_present": 'router.post("/chat"' in text or '@router.post("/chat"' in text,
        "reads_lifecycle_registry": "LIFECYCLE_REGISTRY" in text and "_load_lifecycle_registry" in text,
        "read_only_contract": (
            "no SMF write" in text
            and "no DB write" in text
            and "no planner mutation" in text
            and "no executor" in text
        ),
        "technical_details_hidden": "technical_details_hidden" in text,
    }


def _docs_info() -> dict[str, Any]:
    text = MASTER_DOC.read_text(encoding="utf-8") if MASTER_DOC.exists() else ""
    return {
        "master_doc_exists": MASTER_DOC.exists(),
        "real_ingest_contract_documented": "Real ingest preview contract" in text,
        "radar_documented": "PROMETEO RADAR" in text,
    }


def _print_section(title: str) -> None:
    print()
    print(f"## {title}")


def main() -> int:
    git = _git_info()
    smf = _smf_info()
    real_ingest = _real_ingest_info()
    lifecycle = _lifecycle_info()
    tl_chat = _tl_chat_info()
    docs = _docs_info()
    ollama = _ollama_info()

    print("# PROMETEO RADAR")
    print()
    print("Vista locale read-only del progetto. Nessuna scrittura. Nessuna API esterna.")

    _print_section("Git")
    print(f"- branch: {git['branch']}")
    print(f"- ultimo commit: {git['last_commit']}")
    print(f"- working tree: {git['working_tree']}")
    if git["changed_files"]:
        print("- file modificati:")
        for item in git["changed_files"]:
            print(f"  - {item}")

    _print_section("SMF")
    print(f"- base path: {smf['base_path']}")
    print(f"- master: {'presente' if smf['master_exists'] else 'mancante'}")
    print(f"- fogli: {len(smf.get('sheets') or [])}")
    for sheet, count in (smf.get("counts") or {}).items():
        print(f"- {sheet}: {count if count is not None else 'N/D'}")
    if smf.get("bom_articles_not_in_codici") is not None:
        print(f"- articoli BOM_Specs non in Codici: {smf['bom_articles_not_in_codici']}")
        sample = smf.get("bom_articles_not_in_codici_sample") or []
        if sample:
            print(f"- sample: {', '.join(sample)}")

    _print_section("Lifecycle registry")
    print(f"- registry: {'presente' if lifecycle['exists'] else 'mancante'}")
    print(f"- voci: {lifecycle['total']}")
    for status, count in sorted((lifecycle.get("by_status") or {}).items()):
        print(f"- {status}: {count}")
    sample = lifecycle.get("sample") or []
    if sample:
        print(f"- sample: {', '.join(sample)}")

    _print_section("Real ingest")
    print(f"- file endpoint: {'presente' if real_ingest['file_exists'] else 'mancante'}")
    print(f"- /real/ingest-order: {'presente' if real_ingest['preview_endpoint'] else 'mancante'}")
    print(f"- /real/article-profile/{{article}}: {'presente' if real_ingest['article_profile_endpoint'] else 'mancante'}")
    print(f"- SMFReader: {'sì' if real_ingest['uses_smf_reader'] else 'no'}")
    print(f"- ArticlePilotProfile builder: {'sì' if real_ingest['uses_article_profile_builder'] else 'no'}")
    print(f"- SMFAdapter diretto nel path: {'ATTENZIONE' if real_ingest['mentions_smf_adapter_bootstrap'] else 'no'}")

    _print_section("TL Chat")
    print(f"- file endpoint: {'presente' if tl_chat['file_exists'] else 'mancante'}")
    print(f"- /tl/chat: {'presente' if tl_chat['endpoint_present'] else 'mancante'}")
    print(f"- lifecycle registry: {'collegato' if tl_chat['reads_lifecycle_registry'] else 'non collegato'}")
    print(f"- modalità read-only: {'sì' if tl_chat['read_only_contract'] else 'da verificare'}")
    print(f"- rumore tecnico nascosto: {'sì' if tl_chat['technical_details_hidden'] else 'da verificare'}")

    _print_section("Documentazione")
    print(f"- PROMETEO_MASTER.md: {'presente' if docs['master_doc_exists'] else 'mancante'}")
    print(f"- real_ingest contract: {'documentato' if docs['real_ingest_contract_documented'] else 'mancante'}")
    print(f"- PROMETEO RADAR: {'documentato' if docs['radar_documented'] else 'non ancora documentato'}")

    _print_section("AI locale")
    print(f"- Ollama CLI: {'presente' if ollama['available'] else 'mancante'}")
    if ollama.get("version"):
        print(f"- versione: {ollama['version']}")
    print(f"- server locale: {'attivo' if ollama.get('server_running') else 'non attivo'}")
    models = ollama.get("models") or []
    print(f"- modelli: {', '.join(models) if models else 'N/D'}")

    _print_section("Rischi visibili")
    risks: list[str] = []
    if git["working_tree"] != "clean":
        risks.append("working tree non pulito")
    if smf.get("bom_articles_not_in_codici", 0):
        risks.append("Codici non allineato a BOM_Specs")
    if lifecycle.get("by_status", {}).get("DA_VERIFICARE", 0):
        risks.append("lifecycle registry contiene articoli DA_VERIFICARE")
    if not docs["real_ingest_contract_documented"]:
        risks.append("contratto real_ingest non documentato")
    if real_ingest["mentions_smf_adapter_bootstrap"]:
        risks.append("possibile uso SMFAdapter nel path real_ingest")
    if not tl_chat["endpoint_present"]:
        risks.append("TL Chat endpoint non rilevato")
    if tl_chat["endpoint_present"] and not tl_chat["reads_lifecycle_registry"]:
        risks.append("TL Chat non collegata al lifecycle registry")
    if not ollama.get("server_running"):
        risks.append("Ollama server non attivo")

    if risks:
        for risk in risks:
            print(f"- {risk}")
    else:
        print("- nessun rischio immediato rilevato")

    _print_section("Prossimo blocco consigliato")
    if smf.get("bom_articles_not_in_codici", 0):
        print("- densificazione Codici / articoli BOM inferiti")
    else:
        print("- gate TL conferma preview → staging")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
