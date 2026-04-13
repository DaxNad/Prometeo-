from app.ingest.ocr_parser import parse_ocr_order_rows
from app.ingest.ocr_ingest import normalize_extracted_order
from app.api_smf import ParseExtractedOrderRequest, _build_parse_only_result
from tests.test_smf_ingest import _build_test_workbook
from app.smf.smf_adapter import SMFAdapter


def test_parse_ocr_order_rows_from_text_block():
    result = parse_ocr_order_rows(
        """
        ID ordine: TL-2026-001
        Cliente: Officine Rossi
        Codice: ABC123
        Q.tà: 12
        Data richiesta cliente: 2026-04-20
        Priorità: urgente
        Note: consegna parziale
        """
    )

    parsed = result["parsed_order"]
    assert parsed["order_id"] == "TL-2026-001"
    assert parsed["cliente"] == "Officine Rossi"
    assert parsed["codice"] == "ABC123"
    assert parsed["qta"] == "12"
    assert parsed["due_date"] == "2026-04-20"
    assert parsed["priority"] == "ALTA"
    assert parsed["note"] == "consegna parziale"


def test_parse_ocr_order_rows_from_row_list_with_extra_text():
    result = parse_ocr_order_rows(
        [
            "ORDINE = TL-2026-002",
            "CUSTOMER - Meccanica Bianchi",
            "ARTICOLO: ZX-900",
            "QTA 5",
            "CONSEGNA 22/04/2026",
            "PRIO media",
            "testo spurio OCR da verificare",
        ]
    )

    parsed = result["parsed_order"]
    assert parsed["order_id"] == "TL-2026-002"
    assert parsed["cliente"] == "Meccanica Bianchi"
    assert parsed["codice"] == "ZX-900"
    assert parsed["qta"] == "5"
    assert parsed["due_date"] == "22/04/2026"
    assert parsed["priority"] == "MEDIA"
    assert "OCR_EXTRA=" in parsed["note"]


def test_parse_then_normalize_bridge_without_write():
    parsed = parse_ocr_order_rows(
        """
        ID ordine: TL-2026-003
        Cliente: Officine Verdi
        Codice: CDE456
        QTA 8
        Consegna 23/04/2026
        Prio alta
        """
    )

    normalized = normalize_extracted_order(parsed)
    payload = normalized["normalized"]
    assert payload["order_id"] == "TL-2026-003"
    assert payload["cliente"] == "Officine Verdi"
    assert payload["codice"] == "CDE456"
    assert payload["qta"] == 8
    assert payload["priority"] == "ALTA"
    assert normalized["has_meaningful_payload"] is True


def test_parse_detects_postazione_when_present():
    parsed = parse_ocr_order_rows(
        """
        ID ordine: TL-2026-004
        Cliente: Officine Blu
        Codice: FGH789
        QTA 3
        Postazione: LINEA1
        """
    )

    parsed_order = parsed["parsed_order"]
    assert parsed_order["order_id"] == "TL-2026-004"
    assert parsed_order["postazione"] == "LINEA1"


def test_parse_only_result_accepts_structured_payload_and_dedup_key(tmp_path):
    smf_dir = tmp_path / "smf_parse"
    smf_dir.mkdir()
    workbook_path = smf_dir / "SuperMegaFile_Master.xlsx"
    _build_test_workbook(workbook_path)
    adapter = SMFAdapter(base_path=smf_dir)

    payload = ParseExtractedOrderRequest(
        order_id="TL-STRUCT-001",
        code="COD-NEW",
        quantity=4,
        station="LINEA1",
        customer_due_date="2026-04-24",
        customer="Cliente Strutturato",
        note="note structured",
        source_type="ocr_structured",
    )

    result = _build_parse_only_result(payload, smf_adapter=adapter)
    assert result["parsed_order"]["order_id"] == "TL-STRUCT-001"
    assert result["parsed_order"]["codice"] == "COD-NEW"
    assert result["parsed_order"]["qta"] == "4"
    assert result["parsed_order"]["postazione"] == "LINEA1"
    assert result["normalized"]["order_id"] == "TL-STRUCT-001"
    assert result["normalized"]["codice"] == "COD-NEW"
    assert result["normalized"]["qta"] == 4
    assert result["has_meaningful_payload"] is True
    assert result["code_validation"]["status"] == "found"
    assert result["station_validation"]["status"] == "found"
