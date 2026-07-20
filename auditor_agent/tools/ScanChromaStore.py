import json
import os
from typing import Optional

from agency_swarm.tools import BaseTool
from dotenv import load_dotenv
from pydantic import Field

from rlg_common import config as rlg_config
from rlg_common import stores, summary

load_dotenv()


class ScanChromaStore(BaseTool):
    """
    Scan a local (persistent) Chroma vector store and report what sensitive data
    it already remembers. Read-only: the store is never modified. Returns
    findings-METADATA only (counts, types, severities, risk level, record ids,
    masked samples) plus a Markdown risk report. Raw values are never returned.
    """

    path: str = Field(..., description="Filesystem path of the Chroma PersistentClient store.")
    collection: Optional[str] = Field(
        None, description="A specific collection to scan; omit to scan every collection."
    )
    locale: Optional[str] = Field(
        None,
        description="Optional country pack, e.g. 'au' for Australian identifiers. "
        "Defaults to the onboarding configuration.",
    )

    def run(self):
        if not os.path.isdir(self.path):
            return json.dumps({"event": "ragleakguard.agent.error", "error": f"store path not found: {self.path}"})
        locale = self.locale or rlg_config.get_default_locale()
        try:
            items = stores.iter_chroma_items(self.path, collection=self.collection)
            records = summary.scan_items(items, locale=locale)
        except ImportError:
            return json.dumps({
                "event": "ragleakguard.agent.error",
                "error": "chromadb is not installed in this deployment; install ragleakguard[chroma]",
            })
        result = summary.build_result("chroma", self.path, records, locale=locale)
        return summary.to_json(result)


if __name__ == "__main__":
    print(ScanChromaStore(path="./sample_store").run())
