from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class RiskInput(BaseModel):
    """
    A generalized schema containing outputs from any upstream intelligence engine.
    Example: 
    {
        "NumberEngine": [...],
        "ContactIntentEngine": [...]
    }
    """
    engines: Dict[str, List[Dict[str, Any]]]

class RiskEvidence(BaseModel):
    """
    Explainable evidence explaining the source engines and confidence of the trigger.
    """
    engine: str
    confidence: float
    matched_data: Dict[str, Any]

class RiskResult(BaseModel):
    """
    The final decision output from the Risk Engine.
    """
    decision_rule: Optional[str] = None
    matched_conditions: List[str] = []
    evidence: List[RiskEvidence] = []
    risk_level: str = "NONE"
    recommended_action: str = "ALLOW"
    reason: str = "No risk patterns detected."
    risk_score: Optional[int] = 0
