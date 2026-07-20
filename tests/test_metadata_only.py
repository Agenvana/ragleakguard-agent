"""The metadata-only principle as executable law, for every agent tool.

Mirrors test_state_and_payload_never_contain_raw_values in the RAGLeakGuard
repo (tests/test_monitor.py): plant known secrets, run the real tool code end
to end, then assert the serialized output contains finding TYPES but none of
the planted values and no document text. Any change to a tool's output shape
must keep every test in this file passing.
"""
import json

import pytest

from conftest import PLANTED, assert_metadata_only

from rlg_common import openai_store, stores, summary
from auditor_agent.tools.ScanFiles import ScanFiles
from auditor_agent.tools.ScanChromaStore import ScanChromaStore
from auditor_agent.tools.ScanOpenAIVectorStore import ScanOpenAIVectorStore


def test_scan_files_output_never_contains_raw_values(use_fake_detect, docs_folder):
    out = ScanFiles(path=docs_folder).run()
    assert_metadata_only(out)
    assert "EMAIL_ADDRESS" in out and "AU_TFN" in out  # types are the only content we ship
    assert "patient_note.txt" in out  # record ids/file names are allowed metadata
    parsed = json.loads(out)
    assert parsed["totals"]["records_with_findings"] == 1
    assert parsed["totals"]["findings"] == 4


def test_scan_chroma_store_output_never_contains_raw_values(use_fake_detect, monkeypatch, tmp_path):
    def fake_items(path, collection=None):
        yield {"id": "rec-1", "text": f"note for {PLANTED['PERSON']}: {PLANTED['EMAIL_ADDRESS']}",
               "metadata": {}, "collection": "clinic_notes"}
        yield {"id": "rec-2", "text": "totally clean content", "metadata": {}, "collection": "clinic_notes"}

    monkeypatch.setattr(stores, "iter_chroma_items", fake_items)
    out = ScanChromaStore(path=str(tmp_path)).run()
    assert_metadata_only(out)
    assert "PERSON" in out and "EMAIL_ADDRESS" in out
    assert "clinic_notes:rec-1" in out
    assert "totally clean content" not in out


def test_scan_openai_vector_store_output_never_contains_raw_values(
    use_fake_detect, monkeypatch, fake_store_chunks
):
    monkeypatch.setattr(openai_store, "iter_vector_store_chunks", lambda vs_id: iter(fake_store_chunks))
    out = ScanOpenAIVectorStore(vector_store_id="vs_test123").run()
    assert_metadata_only(out)
    assert "EMAIL_ADDRESS" in out and "PHONE_NUMBER" in out
    assert "notes.txt#chunk0" in out
    assert "shipping takes" not in out  # clean chunk text must not leak either


def test_masked_samples_contain_zero_original_characters(use_fake_detect):
    rec = summary.scan_text(f"reach {PLANTED['PERSON']} at {PLANTED['EMAIL_ADDRESS']}")
    for sample in rec["samples"]:
        assert set(sample["masked"]) <= {summary.MASK_CHAR}
        assert sample["length"] > 0


def _real_detector_ready():
    try:
        from ragleakguard.detect import detect
        return bool(detect("Contact sam.reader@example.com today"))
    except Exception:
        return False


@pytest.mark.skipif(not _real_detector_ready(), reason="presidio/spaCy model not installed")
def test_real_detector_end_to_end_never_leaks_raw_values(tmp_path):
    """Belt and braces: the same guarantee with the REAL detection stack."""
    secret_email = "sam.reader@example.com"
    secret_phone = "+1 415 555 0142"
    p = tmp_path / "leads.txt"
    p.write_text(f"Lead: Sam Reader, {secret_email}, {secret_phone}, meeting 2026-07-21.", encoding="utf-8")

    out = ScanFiles(path=str(p)).run()
    assert secret_email not in out
    assert secret_phone not in out
    assert "EMAIL_ADDRESS" in out
    parsed = json.loads(out)
    assert parsed["totals"]["findings"] >= 2
