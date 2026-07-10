from typing import Dict, Any, List, Optional
from .rule_engine import RuleEngine

class DecisionEngine:
    """
    Evaluates inputs against all parsed rules, returning the highest priority match.
    """
    def __init__(self, rule_engine: RuleEngine):
        self.rule_engine = rule_engine

    def evaluate(self, engines_data: Dict[str, List[Dict[str, Any]]]) -> Optional[Dict[str, Any]]:
        """
        Scans all rules in priority order. Returns the first matching rule payload.
        """
        for rule in self.rule_engine.rules:
            is_match, evidence, matched_conditions = self.rule_engine.evaluate_rule(rule, engines_data)
            if is_match:
                return {
                    "rule_name": rule.get("name"),
                    "risk_level": rule.get("risk_level", "NONE"),
                    "policy": rule.get("policy", "ALLOW"),
                    "reason": rule.get("reason", ""),
                    "evidence": evidence,
                    "matched_conditions": matched_conditions
                }
        return None
