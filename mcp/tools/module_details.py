"""
Tool: get_module_details
MCP Name: get_module_details
Knowledge Source: knowledge/modules/{module_name}.md

Parameters:
    module_name (str): The module to look up. Must match one of the filenames
                       in knowledge/modules/ (without the .md extension).
                       Example: "downloader", "pii_engine", "risk_engine"

Returns: Full module specification including purpose, inputs, outputs,
         responsibilities, dependencies, and current implementation status.

Available module names:
    downloader, audio_validator, vad, speech_recognition, speaker_diarization,
    normalization, indian_number_intelligence, pii_engine, abuse_engine,
    threat_engine, scam_engine, risk_engine, reasoning_engine, alert_engine,
    analytics_engine, audit_log

IMPLEMENTATION STUB
-------------------
When implemented, this tool will:
1. Resolve knowledge/modules/{module_name}.md
2. Return UNKNOWN_MODULE error with available_modules list if not found
3. Parse sections: Purpose, Inputs, Outputs, Responsibilities, Dependencies, Status
4. Return structured dict matching schemas/module_details.schema.json
"""


AVAILABLE_MODULES = [
    "downloader", "audio_validator", "vad", "speech_recognition",
    "speaker_diarization", "normalization", "indian_number_intelligence",
    "pii_engine", "abuse_engine", "threat_engine", "scam_engine",
    "risk_engine", "reasoning_engine", "alert_engine", "analytics_engine",
    "audit_log"
]


def handle(module_name: str) -> dict:
    """
    Returns the full specification for the named system module.

    STUB — implement by reading knowledge/modules/{module_name}.md
    """
    raise NotImplementedError(
        f"Implement by reading knowledge/modules/{module_name}.md. "
        f"Available: {AVAILABLE_MODULES}"
    )
