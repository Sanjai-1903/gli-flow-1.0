import json
from typing import Optional, Dict, Any


BHARATCODE_API_URL = "https://api.bharatcode.com/v1/green-lantern/submit"


class EmailWorkflow:
    """Optional workflow to submit unknown failures to Green Lantern Industries
    using the BharatCode API.

    Requires explicit user consent. No automatic uploads.
    """

    def __init__(self, api_key: Optional[str] = None, api_url: str = BHARATCODE_API_URL):
        self.api_key = api_key
        self.api_url = api_url

    def submit(
        self,
        failure_metadata: Dict[str, Any],
        ai_suggestions: Optional[Dict[str, Any]] = None,
        resolution_outcome: Optional[Dict[str, Any]] = None,
        consent_given: bool = False,
    ) -> Dict[str, Any]:
        """Submit an unknown failure to Green Lantern Industries.

        Args:
            failure_metadata: Tool, stage, error text, design metadata, metrics
            ai_suggestions: AI-generated possible causes and investigation steps
            resolution_outcome: If resolved, the fix description and outcome
            consent_given: User must explicitly consent

        Returns:
            Response dict with status and submission ID
        """
        if not consent_given:
            return {"status": "error", "message": "User consent required — no automatic uploads"}

        if not self.api_key:
            return {"status": "error", "message": "BharatCode API key not configured"}

        payload = {
            "failure_metadata": failure_metadata,
            "ai_suggestions": ai_suggestions or {},
            "resolution_outcome": resolution_outcome or {},
        }

        try:
            import urllib.request
            import urllib.error

            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                self.api_url,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                return {"status": "submitted", "response": body}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace") if e.fp else str(e)
            return {"status": "error", "message": f"HTTP {e.code}: {error_body}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def validate_consent(consent_input: str) -> bool:
        """Validate that user explicitly consented."""
        return consent_input.strip().lower() in ("yes", "y", "i consent", "confirm")
