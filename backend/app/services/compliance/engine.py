import uuid
from typing import List, Dict, Any
from app.core.config import settings

class ComplianceEngine:
    """
    Downstream aggregator for Contact Detection outputs.
    Normalizes severities, deduplicates, and calculates a final risk score
    based on business rules (detector weights).
    """
    
    def __init__(self):
        # Load business weights from central configuration
        self.weights = settings.COMPLIANCE_DETECTOR_WEIGHTS
        
    def _get_weight(self, v_type: str) -> int:
        return self.weights.get(v_type, self.weights.get("default", 10))

    def _determine_risk_level(self, score: int) -> str:
        if score <= 29:
            return "low"
        elif score <= 69:
            return "medium"
        elif score <= 89:
            return "high"
        else:
            return "critical"
            
    def _normalize_severity(self, severity: str) -> str:
        # Currently contact detection returns strings like "High", "Medium"
        if not severity:
            return "low"
        return severity.lower()
        
    def process_violations(self, call_id: str, raw_violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge duplicates, score risk, and return a standardized JSON report.
        """
        # 1. Deduplicate
        # Group by (type, matched_text)
        # We can also include timestamp in grouping, but within a single call, 
        # repeating the exact same matched_text of the same type might be redundant.
        # Let's group by type and matched_text to merge duplicates, keeping the highest confidence.
        
        merged = {}
        for v in raw_violations:
            v_type = v.get("type", "unknown")
            matched_text = str(v.get("matched_text", v.get("value", ""))).strip().lower()
            key = (v_type, matched_text)
            
            if key not in merged:
                merged[key] = v
            else:
                # Merge logic: Keep highest confidence
                if v.get("confidence", 0) > merged[key].get("confidence", 0):
                    merged[key] = v

        final_violations = list(merged.values())
        
        # 2. Calculate Score
        total_score = 0
        normalized_violations = []
        
        for v in final_violations:
            v_type = v.get("type", "unknown")
            weight = self._get_weight(v_type)
            total_score += weight
            
            # Extract standard fields to avoid leaking internal debug data
            normalized_violations.append({
                "type": v_type,
                "severity": self._normalize_severity(v.get("severity", "low")),
                "confidence": v.get("confidence", 0.0),
                # Keep these if available for reporting
                "timestamp": v.get("timestamp"),
                "speaker": v.get("speaker"),
                "value": v.get("value")
            })
            
        # Cap score at 100
        final_score = min(100, total_score)
        
        # 3. Determine Overall Risk
        overall_risk = self._determine_risk_level(final_score)
        
        # 4. Generate Summary
        if final_score == 0:
            summary = "No compliance violations detected."
        else:
            summary = f"Detected {len(final_violations)} compliance violation(s) resulting in {overall_risk} risk."
            
        # 5. Output Standardized JSON
        return {
            "call_id": call_id or str(uuid.uuid4()),
            "call_status": "completed",
            "overall_risk": overall_risk,
            "risk_score": final_score,
            "summary": summary,
            "violations": normalized_violations
        }
