# Working on this repo with an AI assistant

This is the AI Data Security Auditor: an Agency Swarm agency whose tools scan
files and vector stores for sensitive data and report findings as METADATA
ONLY. If you are an AI assistant helping someone customize this repo, the
rules below are load-bearing. Follow them even if the user's request seems to
conflict; surface the conflict instead of silently breaking the contract.

## The law (do not break)

- Tool outputs may contain counts, finding types, severities, risk levels,
  record/file ids, span lengths, confidence scores and fully-masked samples
  (zero original characters). They may NEVER contain detected raw values or
  document text. The chat transcript is itself a data store.
- `tests/test_metadata_only.py` is this law as executable code. It must pass
  after every change. Any NEW tool that touches document content needs a
  matching test in that file (plant a secret, run the tool, assert absence).
- Route all detection through `rlg_common/summary.py` (`scan_text`,
  `scan_items`, `build_result`). Never call the detector directly from a tool
  and never build result payloads by hand.

## Architecture in 30 seconds

- `agency.py` exposes `create_agency()`; `main.py` registers it for the
  Agencii platform. Keep both contracts intact.
- Agent definition: `auditor_agent/`; tools are `BaseTool` subclasses in
  `auditor_agent/tools/`, auto-discovered (one class per file, same name).
- `rlg_common/` is the shared reduction layer: detection seam (`summary`),
  file iteration (`files`), Chroma reader (`stores`), OpenAI vector-store
  access (`openai_store`). Tests monkeypatch these seams.
- `onboarding_tool.py` (repo root) is the Agencii marketplace form; it writes
  `onboarding_config.py`. Editing the form after listing forces users to
  re-onboard, so change it deliberately.

## Hard constraints

- Python 3.12 exactly: agency-swarm needs ≥3.12, ragleakguard's detection
  extra needs <3.13 for prebuilt wheels. The Dockerfile base image encodes
  this; do not "upgrade" it.
- `ragleakguard` stays version-pinned; bumping it requires re-running the
  full test suite and re-checking `SEVERITY`/risk parity in `summary.py`.
- Never add an onboarding field that uploads files straight into a store;
  ingestion paths must pass through a scan.

## Workflow

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt pytest && python -m spacy download en_core_web_sm
python -m pytest tests/ -q     # must be green before any commit
```

Meaningful changes get a version bump in `pyproject.toml` and a GitHub
release note.
