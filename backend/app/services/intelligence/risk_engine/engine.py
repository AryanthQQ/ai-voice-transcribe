import os
from .models import RiskInput, RiskResult
from .rule_engine import RuleEngine
from .decision_engine import DecisionEngine
from .policy_layer import PolicyLayer
from .action_engine import ActionEngine

class RiskDecisionEngine:
    """
    Orchestrates the 4-stage Risk Engine Pipeline:
    Rule Engine -> Decision Engine -> Policy Layer -> Action Engine
    """
    def __init__(self, rules_dir: str = None):
        if not rules_dir:
            rules_dir = os.path.join(os.path.dirname(__file__), "rules")
            
        rules_path = os.path.join(rules_dir, "rules.yaml")
        policies_path = os.path.join(rules_dir, "policies.yaml")
        
        self.rule_engine = RuleEngine(rules_path)
        self.decision_engine = DecisionEngine(self.rule_engine)
        self.policy_layer = PolicyLayer(policies_path)
        self.action_engine = ActionEngine()

    def process(self, input_data: RiskInput, tenant_id: str = "default") -> RiskResult:
        """
        Evaluate generalized engine inputs to produce a deterministic risk decision.
        """
        # Stage 1 & 2: Parse Rules & Evaluate Decisions
        decision_data = self.decision_engine.evaluate(input_data.engines)
        
        if decision_data:
            # Stage 3: Resolve Policy
            policy_name = decision_data.get("policy", "ALLOW")
            action = self.policy_layer.resolve_action(policy_name, tenant_id)
        else:
            action = "ALLOW"
            
        # Stage 4: Format Final Output
        return self.action_engine.format_result(decision_data, action)
