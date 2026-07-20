import json
import os
from typing import Optional

from agency_swarm.tools import BaseTool
from dotenv import load_dotenv
from pydantic import Field

from rlg_common import config as rlg_config
from rlg_common import files as rlg_files
from rlg_common import summary

load_dotenv()


class ScanFiles(BaseTool):
    """
    Scan a local file or folder of documents for exposed sensitive data (PII and
    identity/financial/health identifiers) BEFORE the documents are ingested into
    a RAG store or knowledge base. Returns findings-METADATA only: counts, types,
    severities, risk level, file names and fully-masked samples. The detected
    values themselves are never returned.
    """

    path: str = Field(..., description="Path to a file or folder to scan.")
    locale: Optional[str] = Field(
        None,
        description="Optional country pack, e.g. 'au' adds Australian identifiers "
        "(TFN, ABN, ACN, Medicare, AU phone formats). Defaults to the onboarding configuration.",
    )
    max_files: int = Field(500, description="Safety cap on files walked in folder mode.")

    def run(self):
        if not os.path.exists(self.path):
            return json.dumps({"event": "ragleakguard.agent.error", "error": f"path not found: {self.path}"})
        locale = self.locale or rlg_config.get_default_locale()
        base = self.path if os.path.isdir(self.path) else os.path.dirname(self.path) or "."
        records = {}
        for fp in rlg_files.iter_text_files(self.path, max_files=self.max_files):
            key = os.path.relpath(fp, base)
            records[key] = summary.scan_text(rlg_files.read_text(fp), locale=locale)
        result = summary.build_result("files", self.path, records, locale=locale)
        return summary.to_json(result)


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "note.txt")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("Contact John Smith at john.smith@example.com or +1 415 555 0100.")
        print(ScanFiles(path=d).run())
