from agency_swarm import Agent

from rlg_common.config import get_config

_cfg = get_config()

auditor_agent = Agent(
    name=_cfg["agent_name"],
    description=(
        "Audits AI agent stacks for sensitive-data exposure: scans documents "
        "before ingestion and vector stores (Chroma, OpenAI) on demand. "
        "Reports findings as metadata only, never raw values."
    ),
    instructions="./instructions.md",
    tools_folder="./tools",
    model=_cfg["model"],
)
