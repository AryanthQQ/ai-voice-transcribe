from typing import Dict, Any, Optional
from .models import RiskResult, RiskEvidence

class ActionEngine:
    """
    Wraps the evaluated data into the strict RiskResult schema.
    """
    @staticmethod
    def format_result(decision_data: Optional[Dict[str, Any]], action: str) -> RiskResult:
        if not decision_data:
            return RiskResult(
                decision_rule=None,
                matched_conditions=[],
                evidence=[],
                risk_level="NONE",
                recommended_action="ALLOW",
                reason="No risk patterns detected."
            )
            
        evidence_objects = []
        for ev in decision_data.get("evidence", []):
            evidence_objects.append(RiskEvidence(
                engine=ev.get("engine", ""),
                confidence=ev.get("matched_data", {}).get("confidence", 1.0),
                matched_data=ev.get("matched_data", {})
            ))
            
        return RiskResult(
            decision_rule=decision_data.get("rule_name"),
            matched_conditions=decision_data.get("matched_conditions", []),
            evidence=evidence_objects,
            risk_level=decision_data.get("risk_level", "NONE"),
            recommended_action=action,
            reason=decision_data.get("reason", "")
        )
