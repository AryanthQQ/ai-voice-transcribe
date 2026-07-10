import yaml
import os
from typing import Dict, Any

class PolicyLayer:
    """
    Decouples decision policies from actions. Applies tenant-specific overrides.
    """
    def __init__(self, policies_path: str):
        if not os.path.exists(policies_path):
            self.policies = {}
        else:
            with open(policies_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                self.policies = data.get("policies", {})

    def resolve_action(self, policy_name: str, tenant_id: str = "default") -> str:
        """
        Resolves a policy name to a concrete action based on the tenant config.
        """
        policy = self.policies.get(policy_name)
        if not policy:
            return "ALLOW" # Default fallback
            
        overrides = policy.get("tenant_overrides", {})
        if tenant_id in overrides:
            return overrides[tenant_id]
            
        return policy.get("default_action", "ALLOW")
