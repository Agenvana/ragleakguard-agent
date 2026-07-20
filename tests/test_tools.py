"""Tool behavior: verdicts, ingest gating, store resolution, risk aggregation."""
import json
import os

from conftest import PLANTED

from rlg_common import config as rlg_config
from rlg_common import openai_store, summary


def test_resolve_vector_store_id_priority(tmp_path, monkeypatch):
    agent_dir = str(tmp_path)
    # nothing configured -> None
    monkeypatch.delenv("RLG_VECTOR_STORE_ID", raising=False)
    assert openai_store.resolve_vector_store_id(agent_dir) is None
    # cache file
    (tmp_path / ".vector_store_id").write_text("vs_cached", encoding="utf-8")
    assert openai_store.resolve_vector_store_id(agent_dir) == "vs_cached"
    # renamed files folder beats cache (agency-swarm convention files_vs_<id>)
    os.makedirs(tmp_path / "files_vs_vs_abc123")
    assert openai_store.resolve_vector_store_id(agent_dir) == "vs_abc123"
    # env beats folder
    monkeypatch.setenv("RLG_VECTOR_STORE_ID", "vs_env")
    assert openai_store.resolve_vector_store_id(agent_dir) == "vs_env"
    # explicit beats everything
    assert openai_store.resolve_vector_store_id(agent_dir, explicit="vs_explicit") == "vs_explicit"


def test_risk_levels_aggregate():
    high = summary.build_result(
        "files", "/x",
        {"a": {"findings": 2, "types": {"AU_TFN": 1, "EMAIL_ADDRESS": 1}, "samples": []},
         "b": {"findings": 0, "types": {}, "samples": []}},
    )
    assert high["risk_level"] in ("HIGH", "ELEVATED")
    empty = summary.build_result("files", "/x", {"a": {"findings": 0, "types": {}, "samples": []}})
    assert empty["risk_level"] == "LOW"
    assert "report_markdown" in high


def test_default_locale_env_override(monkeypatch):
    monkeypatch.setenv("RLG_LOCALE", "au")
    assert rlg_config.get_default_locale() == "au"
    monkeypatch.delenv("RLG_LOCALE")
    assert rlg_config.get_default_locale() in (None, "au")  # None unless onboarding config sets one


def test_planted_fixture_sanity(use_fake_detect):
    findings = use_fake_detect(" ".join(PLANTED.values()))
    assert len(findings) == len(PLANTED)
