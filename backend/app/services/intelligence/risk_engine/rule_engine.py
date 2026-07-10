import yaml
import os
from typing import Dict, Any, List, Optional

class RuleEngine:
    """
    Parses and evaluates declarative YAML rules securely without using eval().
    """
    def __init__(self, rules_path: str):
        if not os.path.exists(rules_path):
            self.rules = []
        else:
            with open(rules_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                self.rules = data.get("rules", [])
                
        # Sort rules by priority descending
        self.rules.sort(key=lambda x: x.get("priority", 0), reverse=True)

    def evaluate_condition(self, condition: Dict[str, Any], engines_data: Dict[str, List[Dict[str, Any]]]) -> Optional[Dict[str, Any]]:
        """
        Evaluates a single condition against the provided engines data.
        Returns the matched item (evidence) if True, else None.
        """
        engine_name = condition.get("engine")
        field = condition.get("field")
        expected_value = condition.get("value")
        expected_in = condition.get("in")
        
        if not engine_name or engine_name not in engines_data:
            return None
            
        items = engines_data[engine_name]
        for item in items:
            # Note: For strict schemas like Pydantic models, they might be passed as dicts or objects.
            # Assuming they are converted to dicts before passing here.
            item_val = item.get(field)
            if expected_value is not None and item_val == expected_value:
                return item
            if expected_in is not None and item_val in expected_in:
                return item
        return None

    def evaluate_rule(self, rule: Dict[str, Any], engines_data: Dict[str, List[Dict[str, Any]]]) -> tuple[bool, List[Dict[str, Any]], List[str]]:
        """
        Evaluates an entire rule block (handling 'all').
        Returns (is_match, evidence_items, matched_conditions)
        """
        evidence = []
        matched_conditions = []
        
        if "all" in rule:
            for cond in rule["all"]:
                match = self.evaluate_condition(cond, engines_data)
                if not match:
                    return False, [], []
                evidence.append({"engine": cond.get("engine"), "matched_data": match})
                
                # Format a readable condition string
                cond_str = f"{cond.get('engine')}.{cond.get('field')} "
                if "value" in cond:
                    cond_str += f"== '{cond.get('value')}'"
                elif "in" in cond:
                    cond_str += f"in {cond.get('in')}"
                matched_conditions.append(cond_str)
                
        return True, evidence, matched_conditions
