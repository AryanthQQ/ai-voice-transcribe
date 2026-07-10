import os
import json
from datetime import datetime
from backend.app.services.intelligence.risk_engine.engine import RiskDecisionEngine
from backend.app.services.intelligence.risk_engine.models import RiskInput

def run_benchmarks():
    print("Starting Risk Engine Benchmarks...\n")
    engine = RiskDecisionEngine()
    
    datasets_dir = os.path.join(os.path.dirname(__file__), "datasets")
    if not os.path.exists(datasets_dir):
        print(f"Datasets directory not found at {datasets_dir}")
        return

    total_samples = 0
    correct_actions = 0
    correct_rules = 0
    total_latency_ms = 0.0

    for filename in os.listdir(datasets_dir):
        if not filename.endswith(".json"):
            continue
            
        filepath = os.path.join(datasets_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
            
        for sample in dataset.get("samples", []):
            total_samples += 1
            
            engines_data = sample.get("engines", {})
            tenant = sample.get("tenant", "default")
            expected_action = sample.get("expected_action")
            expected_rule = sample.get("expected_rule")
            
            input_data = RiskInput(engines=engines_data)
            
            # Run engine and measure latency
            start_time = datetime.now()
            result = engine.process(input_data, tenant_id=tenant)
            latency = (datetime.now() - start_time).total_seconds() * 1000
            total_latency_ms += latency
            
            if result.recommended_action == expected_action:
                correct_actions += 1
            if result.decision_rule == expected_rule:
                correct_rules += 1

    action_accuracy = (correct_actions / total_samples) * 100 if total_samples else 0
    rule_accuracy = (correct_rules / total_samples) * 100 if total_samples else 0
    avg_latency = total_latency_ms / total_samples if total_samples else 0

    print("="*50)
    print("OVERALL BENCHMARK RESULTS")
    print("="*50)
    print(f"Total Samples: {total_samples}")
    print(f"Action Accuracy (%): {action_accuracy:.2f}")
    print(f"Rule Accuracy (%): {rule_accuracy:.2f}")
    print(f"Average Latency (ms): {avg_latency:.2f}")
    
    # Generate Markdown report
    report_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    
    with open(report_path, 'w') as f:
        f.write("# Risk Engine Benchmark\n")
        f.write(f"- **Total Samples:** {total_samples}\n")
        f.write(f"- **Action Accuracy:** {action_accuracy:.2f}%\n")
        f.write(f"- **Rule Accuracy:** {rule_accuracy:.2f}%\n")
        f.write(f"- **Latency:** {avg_latency:.2f}ms\n")
        
    print(f"\nReport saved to: {report_path}")

if __name__ == "__main__":
    run_benchmarks()
