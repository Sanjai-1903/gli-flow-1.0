import dataclasses
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List


@dataclasses.dataclass
class KnowledgeContribution:
    new_signature_created: bool = False
    new_historical_intelligence: bool = False
    new_resolution_intelligence: bool = False
    atlas_id_assigned: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "new_signature_created": self.new_signature_created,
            "new_historical_intelligence": self.new_historical_intelligence,
            "new_resolution_intelligence": self.new_resolution_intelligence,
            "atlas_id_assigned": self.atlas_id_assigned,
        }


@dataclasses.dataclass
class EngineeringResponse:
    """Structured response from GLI engineers.

    Every resolution must be:
    - Reusable
    - Structured
    - Searchable

    This format maps directly to Failure Atlas concepts:
    - failure_type + signature → Signature Library
    - description + fix → Resolution Intelligence
    - occurrence tracking → Historical Intelligence
    """

    escalation_id: str
    response_version: str = "1.0"
    created_at: str = ""
    engineer_name: str = ""
    engineer_email: str = ""
    failure_type: str = ""
    signature: str = ""
    atlas_id: str = ""
    description: str = ""
    fix_description: str = ""
    verification_steps: Optional[List[str]] = None
    references: Optional[List[str]] = None
    knowledge_contribution: Optional[KnowledgeContribution] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if self.verification_steps is None:
            self.verification_steps = []
        if self.references is None:
            self.references = []
        if self.knowledge_contribution is None:
            self.knowledge_contribution = KnowledgeContribution()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "escalation_id": self.escalation_id,
            "response_version": self.response_version,
            "created_at": self.created_at,
            "engineer": {
                "name": self.engineer_name,
                "email": self.engineer_email,
            },
            "resolution": {
                "failure_type": self.failure_type,
                "signature": self.signature,
                "atlas_id": self.atlas_id,
                "description": self.description,
                "fix_description": self.fix_description,
                "verification_steps": self.verification_steps,
                "references": self.references,
            },
            "knowledge_contribution": self.knowledge_contribution.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EngineeringResponse":
        resolution = data.get("resolution", {})
        engineer = data.get("engineer", {})
        kc_data = data.get("knowledge_contribution", {})
        return cls(
            escalation_id=data.get("escalation_id", ""),
            response_version=data.get("response_version", "1.0"),
            created_at=data.get("created_at", ""),
            engineer_name=engineer.get("name", ""),
            engineer_email=engineer.get("email", ""),
            failure_type=resolution.get("failure_type", ""),
            signature=resolution.get("signature", ""),
            atlas_id=resolution.get("atlas_id", ""),
            description=resolution.get("description", ""),
            fix_description=resolution.get("fix_description", ""),
            verification_steps=resolution.get("verification_steps", []),
            references=resolution.get("references", []),
            knowledge_contribution=KnowledgeContribution(
                new_signature_created=kc_data.get("new_signature_created", False),
                new_historical_intelligence=kc_data.get("new_historical_intelligence", False),
                new_resolution_intelligence=kc_data.get("new_resolution_intelligence", False),
                atlas_id_assigned=kc_data.get("atlas_id_assigned", ""),
            ),
        )

    def to_signature_entry(self) -> Dict[str, Any]:
        """Convert response to a signature library entry candidate."""
        if not self.signature or not self.failure_type:
            return {}
        return {
            "atlas_id": self.atlas_id,
            "category": self.failure_type,
            "severity": "MEDIUM",
            "observed_signature": self.signature,
            "remediation": self.fix_description,
            "description": self.description,
            "confidence": 0.7,
            "public": True,
        }

    def to_knowledge_entry(self) -> Dict[str, Any]:
        """Convert response to a knowledge base entry candidate."""
        return {
            "failure_type": self.failure_type,
            "description": self.description,
            "common_causes": [self.description],
            "remediation_strategies": [
                {"technique": self.fix_description,
                 "description": self.fix_description}
            ],
            "verification_steps": self.verification_steps,
            "references": self.references or [],
            "confidence": "MEDIUM",
        }
