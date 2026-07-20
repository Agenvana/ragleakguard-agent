from agency_swarm.tools import BaseTool
from pydantic import Field
import os
from dotenv import load_dotenv
from typing import Literal, Optional

load_dotenv()


class OnboardingTool(BaseTool):
    """
    Customizes the AI Data Security Auditor before deployment: agent naming,
    model, detection locale and business context. No field here ever asks for,
    or stores, actual sensitive data values.
    """

    agent_name: str = Field(
        "AI Data Security Auditor",
        description="Name of the auditor agent visible to your users.",
    )

    model: Literal["gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.6-sol"] = Field(
        "gpt-5.6-luna",
        description="OpenAI model the agents run on (verified against the July 2026 catalog). "
        "The scanner itself runs locally and costs no tokens; the model only orchestrates "
        "tools and explains results, so the economical gpt-5.6-luna is a strong default. "
        "Pick terra or sol for more nuanced remediation guidance.",
    )

    locale: Literal["default", "au"] = Field(
        "default",
        description="Detection locale pack. 'au' adds Australian identifiers (TFN, ABN, "
        "ACN, Medicare, AU phone formats) on top of the global/US defaults.",
        json_schema_extra={
            "ui:title": "Detection Locale",
        },
    )

    business_overview: Optional[str] = Field(
        None,
        description="Brief overview of your business and what your AI agents do. "
        "Helps the auditor tailor its guidance.",
        json_schema_extra={
            "ui:widget": "textarea",
            "ui:placeholder": "We run voice agents for dental clinics; call transcripts "
            "land in a Chroma store before summarisation.",
        },
    )

    data_context: Optional[str] = Field(
        None,
        description="What kinds of data your stack touches (categories only; never paste "
        "real records here).",
        json_schema_extra={
            "ui:widget": "textarea",
            "ui:placeholder": "Patient contact details, appointment notes, AU phone numbers.",
        },
    )

    def run(self):
        """
        Saves the configuration as a Python file with a config object.
        """
        import json

        tool_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(tool_dir, "onboarding_config.py")

        config = self.model_dump()

        json_str = json.dumps(config, indent=4, ensure_ascii=False)
        json_str = json_str.replace(": null", ": None").replace(": true", ": True").replace(": false", ": False")
        python_code = f"# Auto-generated onboarding configuration\n\nconfig = {json_str}\n"

        try:
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(python_code)
            return f"Configuration saved at: {config_path}"
        except Exception as e:
            return f"Error writing config file: {str(e)}"


if __name__ == "__main__":
    tool = OnboardingTool()
    print(tool.run())
