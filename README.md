# RAGLeakGuard Agent — the agent that audits agents

Two ready-to-deploy [Agency Swarm](https://agency-swarm.ai/) agencies that keep
sensitive data out of AI memory, powered by
**[RAGLeakGuard](https://github.com/Agenvana/RAGLeakGuard)**, the open-source
scanner for AI pipelines and vector stores.

> ⭐ If these agents are useful to you, the engine behind them lives at
> **[github.com/Agenvana/RAGLeakGuard](https://github.com/Agenvana/RAGLeakGuard)**.
> Stars, issues and locale-pack requests all land there.

| Agency | What it does | Entry point |
|---|---|---|
| **AI Data Security Auditor** | Scans documents before ingestion, and Chroma / OpenAI vector stores on demand. Reports what your agents already remember. | `agency.py` |
| **Safe RAG Agent** | A RAG agent that checks what it is about to remember: documents pass a sensitive-data scan before they can enter the knowledge base, and the knowledge base can be audited on demand. | `safe_rag_agency.py` |

Both run on the [Agencii](https://agencii.ai/) platform or any Docker host.

---

## The metadata-only principle

Every tool in this repo returns **findings-metadata only**: counts, finding
types, severities, risk levels, record and file ids, span lengths, confidence
scores and fully-masked samples (zero original characters). Raw detected
values and document text are never returned. A chat transcript is itself a
data store; an auditor that pastes findings into it would be the leak.

This is not a convention, it is a test:
[`tests/test_metadata_only.py`](tests/test_metadata_only.py) plants known
secrets, runs every tool end to end, and fails if any secret (or any document
prose) appears in the output. It mirrors
`test_state_and_payload_never_contain_raw_values` in the RAGLeakGuard repo.

## Tools

**AI Data Security Auditor** (`auditor_agent/`)

- `ScanFiles(path, locale?)` — scan a file or folder before it gets ingested anywhere.
- `ScanChromaStore(path, collection?, locale?)` — scan a local persistent Chroma store. Read-only.
- `ScanOpenAIVectorStore(vector_store_id, locale?)` — scan an OpenAI vector store's parsed chunks. Read-only.

**Safe RAG Agent** (`safe_rag_agent/`)

- `ScanDocument(path, locale?)` — verdict for one document: `SAFE_TO_INGEST` or `REVIEW_REQUIRED`.
- `SafeIngestDocument(path, force?, locale?)` — scan, then ingest only if clean.
  Findings refuse ingestion unless the user explicitly accepts the risk (`force=true`).
- `ScanKnowledgeBase(vector_store_id?, locale?)` — audit what the knowledge base remembers.

Detection engine: [RAGLeakGuard](https://github.com/Agenvana/RAGLeakGuard)
(Microsoft Presidio + custom recognisers + post-processing judgment). Global +
US entities are on by default; `locale='au'` adds Australian identifiers
(TFN, ABN, ACN, Medicare, AU phone formats) with checksum validation.

## Quick start (local)

Requires **Python 3.12** (agency-swarm needs ≥3.12; ragleakguard's detection
extra needs <3.13 for prebuilt wheels).

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.template .env   # add your OPENAI_API_KEY

# terminal demo, auditor agency:
python agency.py
# terminal demo, safe RAG agency:
python safe_rag_agency.py

# tools also run standalone, e.g.:
python -m auditor_agent.tools.ScanFiles
```

Run the tests:

```bash
python -m pytest tests/ -q
```

## Deploy on Agencii

1. Sign in at [agencii.ai](https://agencii.ai/) and install the
   [Agencii GitHub App](https://github.com/apps/agencii) with access to this repo.
2. Add `OPENAI_API_KEY` in the Agencii dashboard environment settings.
3. Push to `main`. Both agencies deploy from `main.py`
   (`ai-data-security-auditor` and `safe-rag-agent`).

With your own OpenAI API key configured, Agencii does not deduct platform
credits for AI tokens; your running cost is your OpenAI token spend.

## Marketplace onboarding

`onboarding_tool.py` defines the customization form shown when someone
installs the auditor from the Agencii marketplace: agent name, model,
detection locale and business context. `onboarding_config.py` is the
committed default configuration. No onboarding field asks for real sensitive
data, ever.

## Repo layout

```
agency.py                  # AI Data Security Auditor agency (entry)
safe_rag_agency.py         # Safe RAG agency (entry)
main.py                    # platform entry: serves both agencies
auditor_agent/             # auditor agent + tools
safe_rag_agent/            # safe RAG agent + tools (+ files/ knowledge folder)
rlg_common/                # shared reduction layer: findings -> metadata
onboarding_tool.py         # Agencii marketplace onboarding form
tests/                     # incl. the metadata-only enforcing tests
```

## Credits

Built by [Agenvana](https://github.com/Agenvana) on
**[RAGLeakGuard](https://github.com/Agenvana/RAGLeakGuard)** ("Scan your AI's
vector database for exposed sensitive data") and
[Agency Swarm](https://github.com/VRSEN/agency-swarm) /
the [agency-starter-template](https://github.com/agency-ai-solutions/agency-starter-template).

License: Apache-2.0. Detection is best-effort; absence of findings is not
proof of safety.
