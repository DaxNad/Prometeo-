from __future__ import annotations

from typing import Any

import requests


class SMFBOMAdapter:
    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        self.base_url = base_url.rstrip("/")

    def family_by_drawing(self, drawing: str) -> dict[str, Any]:
        url = f"{self.base_url}/smf/bom/family-summary/by-drawing"

        try:
            response = requests.get(
                url,
                params={"disegno": drawing},
                timeout=5,
            )
        except Exception as exc:
            return {
                "ok": False,
                "drawing": drawing,
                "error": f"request_failed: {exc}",
            }

        if response.status_code != 200:
            return {
                "ok": False,
                "drawing": drawing,
                "error": f"http_{response.status_code}",
            }

        try:
            payload = response.json()
        except Exception as exc:
            return {
                "ok": False,
                "drawing": drawing,
                "error": f"invalid_json: {exc}",
            }

        return self._tl_projection(payload)

    def _tl_projection(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not payload.get("ok"):
            return payload

        return {
            "ok": True,
            "drawing": payload.get("drawing"),
            "normalized_drawing": payload.get("normalized_drawing"),
            "articoli": payload.get("articoli_famiglia", []),
            "count_articoli": payload.get("count_articoli", 0),
            "componenti": payload.get("componenti_coinvolti", []),
            "count_componenti": payload.get("count_componenti", 0),
            "fasi": payload.get("fasi_coinvolte", []),
            "postazioni_coinvolte": payload.get("postazioni_stimate", []),
            "criticita": payload.get("criticita_tl", []),
            "rotazione": payload.get("rotazione"),
            "tassativo": payload.get("tassativo", False),
            "peso_turno": payload.get("peso_turno", {}),
            "tipo_famiglia": payload.get("tipo_famiglia"),
            "fonte": "SMF_BOM",
        }
