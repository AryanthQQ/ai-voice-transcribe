import yaml
import os
from typing import Dict, Any, Callable, List

class EngineRegistry:
    """
    Manages the registration and lifecycle of downstream intelligence engines.
    """
    def __init__(self, config_path: str = None):
        self.engines = {} # Mapping of engine name -> {"instance": obj, "adapter": fn}
        
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), "config", "pipeline.yaml")
            
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            self.pipeline_config = data.get("pipeline", {})

    def register(self, name: str, engine_instance: Any, adapter_fn: Callable):
        """
        Registers an engine and the adapter function required to map PipelineContext to the engine's input.
        """
        self.engines[name] = {
            "instance": engine_instance,
            "adapter": adapter_fn
        }

    def get_execution_plan(self) -> List[Dict[str, Any]]:
        """
        Reads pipeline.yaml and returns the ordered list of enabled engines to execute.
        """
        configured_engines = self.pipeline_config.get("engines", [])
        
        # Filter enabled and sort by priority descending
        enabled = [e for e in configured_engines if e.get("enabled", True)]
        enabled.sort(key=lambda x: x.get("priority", 0), reverse=True)
        
        execution_plan = []
        for config in enabled:
            name = config.get("name")
            if name in self.engines:
                execution_plan.append({
                    "name": name,
                    "instance": self.engines[name]["instance"],
                    "adapter": self.engines[name]["adapter"]
                })
        return execution_plan
