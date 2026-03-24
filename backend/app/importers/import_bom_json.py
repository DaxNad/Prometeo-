from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy import text

from app.db.session import engine


BOM_DIR = Path("/mnt/data")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _as_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    s = str(value).strip().lower()
    if s in {"true", "1", "si", "sì", "yes"}:
        return True
    if s in {"false", "0", "no"}:
        return False
    return None


def _pick(data: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in data and data[key] not in (None, "", [], {}):
            return data[key]
    return None


def _detect_family(data: dict[str, Any]) -> str:
    src = json.dumps(data, ensure_ascii=False).upper()

    has_henn = "469122" in src or "469124" in src or "HENN" in src
    has_pidmill = "PIDMILL" in src or "BAT0" in src
    zaw_count = src.count("CRM")
    has_double_zaw = zaw_count >= 2 or "DOPPIO_INNESTO" in src
    has_double_guaina = "GUAINA_DOPPIA" in src or "LUNGHEZZE_MM" in src
    has_taglio = "TAGLIO_SAGOMA" in src

    if has_henn and has_pidmill and has_double_zaw:
        return "HENN_ZAW2_PIDMILL"
    if has_henn and has_pidmill:
        return "HENN_ZAW_PIDMILL"
    if has_henn and has_double_zaw:
        return "HENN_ZAW2"
    if has_henn and "CRM" in src:
        return "HENN_ZAW"
    if has_pidmill and has_double_zaw:
        return "PIDMILL_ZAW2"
    if has_pidmill and has_double_guaina:
        return "PIDMILL_GUAINA_DOPPIA"
    if has_pidmill:
        return "PIDMILL_DIRETTO"
    if has_taglio:
        return "ZAW_TAGLIO_SAGOMA"
    if has_double_zaw and has_double_guaina:
        return "ZAW2_GUAINA_DOPPIA"
    if has_double_zaw:
        return "DOPPIO_INNESTO_ZAW"
    if has_double_guaina:
        return "ZAW_GUAINA_DOPPIA"
    if "CRM" in src:
        return "ZAW_BASE"
    if has_henn:
        return "HENN_BASE"
    return "BASE"


def _extract_specs(data: dict[str, Any], source_file: str) -> dict[str, Any]:
    doc = data.get("documento", {}) or {}
    cluster = data.get("cluster", {}) or {}
    cp = data.get("cp", {}) or {}

    return {
        "articolo": str(_pick(data, "articolo") or "").strip(),
        "codice_articolo": _pick(data, "codice_articolo", "codice_completo", "codice_sap", "codice"),
        "disegno": _pick(data, "disegno", "disegni"),
        "rev": _pick(data, "rev"),
        "documento_tipo": _pick(doc, "tipo"),
        "data_sba": _pick(doc, "data_sba"),
        "qta_lotto": _pick(doc, "qta_lotto", "quantita_lotto"),
        "qta_imballo": _pick(doc, "qta_imballo", "quantita_imballo"),
        "codice_imballo": _pick(doc, "imballo_codice", "codice_imballo"),
        "cluster_name": _pick(cluster, "cluster_name"),
        "famiglia_processo": _detect_family(data),
        "cp_required": _as_bool(_pick(cp, "cp_required")),
        "cp_note": _pick(cp, "cp_note"),
        "source_file": source_file,
        "raw_json": json.dumps(data, ensure_ascii=False),
    }


def _iter_components(data: dict[str, Any], articolo: str):
    # struttura PROMETEO_BOM
    payload = data.get("PROMETEO_BOM", data)
    component_keys = ["componenti", "componenti_base"]
    for key in component_keys:
        for item in payload.get(key, []) or []:
            yield {
                "articolo": articolo,
                "parent_articolo": articolo,
                "codice_componente": item.get("codice"),
                "tipo": item.get("tipo"),
                "ruolo": item.get("ruolo"),
                "quantita": item.get("quantita"),
                "lunghezza_mm": item.get("lunghezza_mm"),
                "postazione": item.get("postazione"),
                "tooling": item.get("tooling"),
                "note": item.get("note"),
                "extra": json.dumps(item, ensure_ascii=False),
            }

    # strutture legacy/materiali
    materiali = payload.get("materiali", {}) or {}
    for key, item in materiali.items():
        if isinstance(item, dict):
            codice = _pick(item, "codice", "materiale_riferimento")
            quantita = _pick(item, "quantita")
            lunghezza = _pick(item, "lunghezza_mm", "lunghezza")
            tooling = _pick(item, "tooling", "attrezzatura", "tooling_pidmill")
            yield {
                "articolo": articolo,
                "parent_articolo": articolo,
                "codice_componente": codice,
                "tipo": key,
                "ruolo": None,
                "quantita": quantita,
                "lunghezza_mm": None if isinstance(lunghezza, str) else lunghezza,
                "postazione": _pick(item, "postazione"),
                "tooling": tooling if isinstance(tooling, str) else None,
                "note": _pick(item, "note", "descrizione", "istruzioni"),
                "extra": json.dumps(item, ensure_ascii=False),
            }
        elif isinstance(item, list):
            yield {
                "articolo": articolo,
                "parent_articolo": articolo,
                "codice_componente": None,
                "tipo": key,
                "ruolo": None,
                "quantita": None,
                "lunghezza_mm": None,
                "postazione": None,
                "tooling": None,
                "note": None,
                "extra": json.dumps(item, ensure_ascii=False),
            }
        elif isinstance(item, str):
            yield {
                "articolo": articolo,
                "parent_articolo": articolo,
                "codice_componente": item,
                "tipo": key,
                "ruolo": None,
                "quantita": None,
                "lunghezza_mm": None,
                "postazione": None,
                "tooling": None,
                "note": None,
                "extra": json.dumps({"value": item}, ensure_ascii=False),
            }


def _iter_operations(data: dict[str, Any], articolo: str):
    payload = data.get("PROMETEO_BOM", data)
    seq = payload.get("sequenza") or payload.get("operazioni_chiave") or []
    for idx, item in enumerate(seq, start=1):
        if isinstance(item, str):
            yield {
                "articolo": articolo,
                "seq_no": idx,
                "fase": item,
                "famiglia_operazione": None,
                "materiale_riferimento": None,
                "tooling": None,
                "macchina": None,
                "solo_per": None,
                "note": None,
                "extra": json.dumps({"fase": item}, ensure_ascii=False),
            }
        else:
            yield {
                "articolo": articolo,
                "seq_no": idx,
                "fase": _pick(item, "fase"),
                "famiglia_operazione": _pick(item, "famiglia_operazione", "famiglia"),
                "materiale_riferimento": _pick(item, "materiale_riferimento", "materiale", "codice", "componenti"),
                "tooling": _pick(item, "tooling", "strumento"),
                "macchina": _pick(item, "macchina"),
                "solo_per": _pick(item, "solo_per"),
                "note": _pick(item, "dettagli", "vincolo", "file"),
                "extra": json.dumps(item, ensure_ascii=False),
            }


def _iter_markings(data: dict[str, Any], articolo: str):
    payload = data.get("PROMETEO_BOM", data)
    markings = payload.get("marcature", [])
    if isinstance(markings, dict):
        markings = [markings]
    for idx, item in enumerate(markings, start=1):
        yield {
            "articolo": articolo,
            "seq_no": idx,
            "tipo": _pick(item, "tipo", "classe"),
            "valore": _pick(item, "valore", "contenuto", "testo", "specifica"),
            "posizione": _pick(item, "posizione"),
            "dettaglio": _pick(item, "dettaglio", "descrizione", "note"),
            "codice_riferimento": _pick(item, "codice_riferimento", "codice_rif", "codice_marcatura"),
            "note": _pick(item, "note"),
            "extra": json.dumps(item, ensure_ascii=False),
        }


def _iter_controls(data: dict[str, Any], articolo: str):
    payload = data.get("PROMETEO_BOM", data)
    controls = payload.get("controlli", []) or payload.get("collaudi", [])
    if isinstance(controls, dict):
        controls = [controls]
    for idx, item in enumerate(controls, start=1):
        if isinstance(item, str):
            yield {
                "articolo": articolo,
                "seq_no": idx,
                "fase": None,
                "tipo": item,
                "obbligatorio": None,
                "campionamento": None,
                "vincolo": None,
                "note": None,
                "extra": json.dumps({"value": item}, ensure_ascii=False),
            }
        else:
            yield {
                "articolo": articolo,
                "seq_no": idx,
                "fase": _pick(item, "fase"),
                "tipo": _pick(item, "tipo"),
                "obbligatorio": _as_bool(_pick(item, "obbligatorio")),
                "campionamento": _pick(item, "campionamento", "regola"),
                "vincolo": _pick(item, "vincolo", "oggettivazione"),
                "note": _pick(item, "note"),
                "extra": json.dumps(item, ensure_ascii=False),
            }


def import_bom_file(path: Path) -> dict[str, Any]:
    data = _read_json(path)
    payload = data.get("PROMETEO_BOM", data)
    articolo = str(_pick(payload, "articolo") or "").strip()
    if not articolo:
        raise ValueError(f"articolo mancante in {path.name}")

    spec = _extract_specs(payload, path.name)

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM bom_components WHERE articolo = :articolo"), {"articolo": articolo})
        conn.execute(text("DELETE FROM bom_operations WHERE articolo = :articolo"), {"articolo": articolo})
        conn.execute(text("DELETE FROM bom_markings WHERE articolo = :articolo"), {"articolo": articolo})
        conn.execute(text("DELETE FROM bom_controls WHERE articolo = :articolo"), {"articolo": articolo})
        conn.execute(text("DELETE FROM bom_variants WHERE articolo = :articolo"), {"articolo": articolo})
        conn.execute(text("DELETE FROM bom_specs WHERE articolo = :articolo"), {"articolo": articolo})

        conn.execute(text("""
            INSERT INTO bom_specs (
                articolo, codice_articolo, disegno, rev, documento_tipo, data_sba,
                qta_lotto, qta_imballo, codice_imballo, cluster_name,
                famiglia_processo, cp_required, cp_note, source_file, raw_json
            ) VALUES (
                :articolo, :codice_articolo, :disegno, :rev, :documento_tipo, :data_sba,
                :qta_lotto, :qta_imballo, :codice_imballo, :cluster_name,
                :famiglia_processo, :cp_required, :cp_note, :source_file, CAST(:raw_json AS JSONB)
            )
        """), spec)

        components = list(_iter_components(payload, articolo))
        for row in components:
            conn.execute(text("""
                INSERT INTO bom_components (
                    articolo, parent_articolo, codice_componente, tipo, ruolo, quantita,
                    lunghezza_mm, postazione, tooling, note, extra
                ) VALUES (
                    :articolo, :parent_articolo, :codice_componente, :tipo, :ruolo, :quantita,
                    :lunghezza_mm, :postazione, :tooling, :note, CAST(:extra AS JSONB)
                )
            """), row)

        operations = list(_iter_operations(payload, articolo))
        for row in operations:
            conn.execute(text("""
                INSERT INTO bom_operations (
                    articolo, seq_no, fase, famiglia_operazione, materiale_riferimento,
                    tooling, macchina, solo_per, note, extra
                ) VALUES (
                    :articolo, :seq_no, :fase, :famiglia_operazione, :materiale_riferimento,
                    :tooling, :macchina, :solo_per, :note, CAST(:extra AS JSONB)
                )
            """), row)

        markings = list(_iter_markings(payload, articolo))
        for row in markings:
            conn.execute(text("""
                INSERT INTO bom_markings (
                    articolo, seq_no, tipo, valore, posizione, dettaglio,
                    codice_riferimento, note, extra
                ) VALUES (
                    :articolo, :seq_no, :tipo, :valore, :posizione, :dettaglio,
                    :codice_riferimento, :note, CAST(:extra AS JSONB)
                )
            """), row)

        controls = list(_iter_controls(payload, articolo))
        for row in controls:
            conn.execute(text("""
                INSERT INTO bom_controls (
                    articolo, seq_no, fase, tipo, obbligatorio, campionamento,
                    vincolo, note, extra
                ) VALUES (
                    :articolo, :seq_no, :fase, :tipo, :obbligatorio, :campionamento,
                    :vincolo, :note, CAST(:extra AS JSONB)
                )
            """), row)

    return {
        "articolo": articolo,
        "famiglia_processo": spec["famiglia_processo"],
        "components": len(components),
        "operations": len(operations),
        "markings": len(markings),
        "controls": len(controls),
        "source_file": path.name,
    }


def import_bom_dir(directory: Path) -> list[dict[str, Any]]:
    results = []
    for path in sorted(directory.glob("*.json")):
        if path.name.endswith(" 2.json"):
            continue
        results.append(import_bom_file(path))
    return results


if __name__ == "__main__":
    results = import_bom_dir(BOM_DIR)
    print(json.dumps(results, ensure_ascii=False, indent=2))
