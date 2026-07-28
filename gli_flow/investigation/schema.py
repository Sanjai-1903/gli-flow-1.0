"""JSON schema validation for LLM investigation output.

Validates that the LLM response matches the expected schema.
Never crashes the pipeline on validation failure.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


REQUIRED_TOP_LEVEL = {
    "investigation_status",
    "summary",
    "facts",
    "possible_causes",
    "recommended_next_steps",
    "missing_information",
    "disclaimer",
}

VALID_STATUSES = {"EXPERIMENTAL", "FAILED"}
VALID_CONFIDENCE = {"LOW", "MEDIUM", "HIGH"}

MAX_FACTS = 20
MAX_CAUSES = 10
MAX_STEPS = 10
MAX_MISSING = 10


@dataclass
class ValidationResult:
    valid: bool
    payload: Optional[dict] = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class InvestigationSchema:

    @staticmethod
    def _extract_json(raw: str) -> tuple[Optional[str], Optional[str]]:
        """Extract JSON from the raw string, handling markdown fences and leading/trailing text."""
        text = raw.strip()

        stripped = text.strip()
        if stripped.startswith("```"):
            lines = stripped.splitlines()
            if len(lines) >= 2:
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                stripped = "\n".join(lines).strip()

        first_brace = stripped.find("{")
        last_brace = stripped.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            return stripped[first_brace : last_brace + 1], None

        return None, "No JSON object found in response"

    @staticmethod
    def validate(raw: str) -> ValidationResult:
        errors = []
        warnings = []

        if not raw or not raw.strip():
            return ValidationResult(valid=False, errors=["Empty response from provider"])

        extracted, err = InvestigationSchema._extract_json(raw)
        if extracted is None:
            return ValidationResult(valid=False, errors=[err or "Could not extract JSON from response"])
        try:
            payload = json.loads(extracted)
        except json.JSONDecodeError as e:
            return ValidationResult(valid=False, errors=[f"Invalid JSON: {e}"])

        if not isinstance(payload, dict):
            return ValidationResult(valid=False, errors=["Response is not a JSON object"])

        missing = REQUIRED_TOP_LEVEL - set(payload.keys())
        if missing:
            errors.append(f"Missing required fields: {', '.join(sorted(missing))}")

        status = payload.get("investigation_status", "")
        if status not in VALID_STATUSES:
            warnings.append(f"Unexpected investigation_status: {status}")

        if not isinstance(payload.get("summary", ""), str):
            errors.append("summary must be a string")

        facts = payload.get("facts", [])
        if not isinstance(facts, list):
            errors.append("facts must be an array")
        elif len(facts) > MAX_FACTS:
            warnings.append(f"facts has {len(facts)} entries (max {MAX_FACTS})")

        for i, fact in enumerate(facts[:MAX_FACTS]):
            if not isinstance(fact, dict):
                errors.append(f"facts[{i}] is not an object")
                continue
            if "observation" not in fact:
                errors.append(f"facts[{i}] missing 'observation'")

        causes = payload.get("possible_causes", [])
        if not isinstance(causes, list):
            errors.append("possible_causes must be an array")
        elif len(causes) > MAX_CAUSES:
            warnings.append(f"possible_causes has {len(causes)} entries (max {MAX_CAUSES})")

        for i, cause in enumerate(causes[:MAX_CAUSES]):
            if not isinstance(cause, dict):
                errors.append(f"possible_causes[{i}] is not an object")
                continue
            if "cause" not in cause:
                errors.append(f"possible_causes[{i}] missing 'cause'")
            confidence = cause.get("confidence", "")
            if confidence not in VALID_CONFIDENCE and confidence:
                warnings.append(f"possible_causes[{i}] unexpected confidence: {confidence}")

        steps = payload.get("recommended_next_steps", [])
        if not isinstance(steps, list):
            errors.append("recommended_next_steps must be an array")

        missing_info = payload.get("missing_information", [])
        if not isinstance(missing_info, list):
            errors.append("missing_information must be an array")

        if not isinstance(payload.get("disclaimer", ""), str):
            errors.append("disclaimer must be a string")

        result = ValidationResult(
            valid=len(errors) == 0,
            payload=payload if len(errors) == 0 else None,
            errors=errors,
            warnings=warnings,
        )

        return result

    @staticmethod
    def build_failed(reason: str) -> dict:
        return {
            "investigation_status": "FAILED",
            "summary": f"Investigation failed: {reason}",
            "facts": [],
            "possible_causes": [],
            "recommended_next_steps": ["Run gli-flow diagnose for deterministic analysis"],
            "missing_information": ["Investigation provider response was invalid"],
            "disclaimer": "AI-generated investigation. Not verified. Does not override signoff results.",
            "validation_error": reason,
            "generated_at": datetime.now().isoformat(),
        }
