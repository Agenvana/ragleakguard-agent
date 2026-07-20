import json
from typing import Optional

from agency_swarm.tools import BaseTool
from dotenv import load_dotenv
from pydantic import Field

from rlg_common import config as rlg_config
from rlg_common import openai_store, summary

load_dotenv()


class ScanOpenAIVectorStore(BaseTool):
    """
    Scan an OpenAI vector store (the kind platform-hosted RAG agents use for file
    search) and report what sensitive data its parsed chunks remember. Read-only.
    Returns findings-METADATA only (counts, types, severities, risk level, chunk
    ids, masked samples) plus a Markdown risk report. Raw values are never
    returned. Requires the OpenAI API key of the account that owns the store.
    """

    vector_store_id: str = Field(..., description="The vector store id, e.g. 'vs_abc123'.")
    locale: Optional[str] = Field(
        None,
        description="Optional country pack, e.g. 'au' for Australian identifiers. "
        "Defaults to the onboarding configuration.",
    )

    def run(self):
        locale = self.locale or rlg_config.get_default_locale()
        try:
            items = openai_store.iter_vector_store_chunks(self.vector_store_id)
            records = summary.scan_items(items, locale=locale)
        except Exception as e:  # API/auth errors carry no document content
            return json.dumps({"event": "ragleakguard.agent.error", "error": f"{type(e).__name__}: {e}"})
        result = summary.build_result("openai_vector_store", self.vector_store_id, records, locale=locale)
        return summary.to_json(result)


if __name__ == "__main__":
    import sys

    vs = sys.argv[1] if len(sys.argv) > 1 else "vs_missing"
    print(ScanOpenAIVectorStore(vector_store_id=vs).run())
