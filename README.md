# RAGLeakGuard Agent — the agent that audits agents

A ready-to-deploy [Agency Swarm](https://agency-swarm.ai/) agency: the
**AI Data Security Auditor** scans documents before ingestion, and Chroma /
OpenAI vector stores on demand, reporting what your agents already remember.
Powered by **[RAGLeakGuard](https://github.com/Agenvana/RAGLeakGuard)**, the
open-source scanner for AI pipelines and vector stores.

> ⭐ If this agent is useful to you, the engine behind it lives at
> **[github.com/Agenvana/RAGLeakGuard](https://github.com/Agenvana/RAGLeakGuard)**.
> Stars, issues and locale-pack requests all land there.
> Want a Q&A (RAG) agent with this scan built into ingestion? That's the
> sister repo:
> **[ragleakguard-safe-qna-agent](https://github.com/Agenvana/ragleakguard-safe-qna-agent)**.

Runs on the [Agencii](https://agencii.ai/) platform or any Docker host.

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

Detection engine: [RAGLeakGuard](https://github.com/Agenvana/RAGLeakGuard)
(Microsoft Presidio + custom recognisers + post-processing judgment). Global +
US entities are on by default; `locale='au'` adds Australian identifiers
(TFN, ABN, ACN, Medicare, AU phone formats) with checksum validation.

## Use the auditor inside YOUR agency

The deployable agencies above are thin wrappers; the reusable unit is the
agent. To add security auditing to an existing Agency Swarm project (no RAG
required), copy `auditor_agent/` and `rlg_common/` into your repo, add
`ragleakguard[detect,chroma]==0.1.0` to your requirements, and wire the agent
into your chart:

```python
from auditor_agent import auditor_agent

agency = Agency(
    my_orchestrator, auditor_agent,
    communication_flows=[(my_orchestrator, auditor_agent)],
)
```

Your orchestrator can now delegate questions like "what sensitive data is in
our store?" to the auditor. The tools are also plain `BaseTool` classes: copy
`auditor_agent/tools/` into any agent's `tools_folder` (keep `rlg_common/`
importable) and that agent gains `ScanFiles` / `ScanChromaStore` /
`ScanOpenAIVectorStore` directly.

## Quick start (local)

Requires **Python 3.12** (agency-swarm needs ≥3.12; ragleakguard's detection
extra needs <3.13 for prebuilt wheels).

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.template .env   # add your OPENAI_API_KEY

# terminal demo:
python agency.py

# tools also run standalone, e.g.:
python -m auditor_agent.tools.ScanFiles
```

Run the tests:

```bash
python -m pytest tests/ -q
```

## Deploy on Agencii

1. Sign up at [agencii.ai](https://agencii.ai/signup?referral=a0d8a28b-56c3-47a4-9ebf-7faa8c2b0caf)
   (referral link) and install the
   [Agencii GitHub App](https://github.com/apps/agencii) with access to this repo.
2. Add `OPENAI_API_KEY` in the Agencii dashboard environment settings.
3. Push to `main`. The agency deploys as `ai-data-security-auditor` from `main.py`.

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
main.py                    # platform entry
auditor_agent/             # auditor agent + tools
rlg_common/                # shared reduction layer: findings -> metadata
onboarding_tool.py         # Agencii marketplace onboarding form
tests/                     # incl. the metadata-only enforcing tests
```

## Need more than a scan?

These agents diagnose. For a formal, human-led assessment of your AI data
security (scoping, data-flow mapping, remediation program, compliance
mapping), start here: **[the intake form](https://tally.so/r/obaG5V)**.
The same goes for managed deployment: if you want this auditor running inside
your own cloud rather than on Agencii, that's an engagement, not a README
section. Deploying this agent for your own clients? The onboarding form lets
you point the contact at your own security team instead, or switch it off.

## Credits

Built by [Agenvana](https://github.com/Agenvana) on
**[RAGLeakGuard](https://github.com/Agenvana/RAGLeakGuard)** ("Scan your AI's
vector database for exposed sensitive data") and
[Agency Swarm](https://github.com/VRSEN/agency-swarm) /
the [agency-starter-template](https://github.com/agency-ai-solutions/agency-starter-template).

License: Apache-2.0. Detection is best-effort; absence of findings is not
proof of safety.
