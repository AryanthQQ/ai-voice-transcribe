import os
import json
from datetime import datetime
from backend.app.services.intelligence.pipeline.orchestrator import IntelligencePipeline
from backend.app.services.intelligence.pipeline.models import PipelineInput

def run_benchmarks():
    print("Starting Intelligence Pipeline End-to-End Benchmarks...\n")
    pipeline = IntelligencePipeline()
    
    datasets_dir = os.path.join(os.path.dirname(__file__), "datasets")
    if not os.path.exists(datasets_dir):
        print(f"Datasets directory not found at {datasets_dir}")
        return

    total_samples = 0
    correct_actions = 0
    total_latency_ms = 0.0
    
    for filename in os.listdir(datasets_dir):
        if not filename.endswith(".json"):
            continue
            
        filepath = os.path.join(datasets_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
            
        for sample in dataset.get("samples", []):
            total_samples += 1
            
            text = sample.get("text", "")
            lang = sample.get("language", "en")
            tenant = sample.get("tenant_id", "default")
            expected_action = sample.get("expected_action")
            
            input_data = PipelineInput(
                text=text,
                start=0.0,
                end=5.0,
                speaker="SPEAKER_00",
                detected_language=lang,
                tenant_id=tenant
            )
            
            result = pipeline.process(input_data)
            total_latency_ms += result.metrics.total_latency_ms
            
            if result.risk_assessment.get("recommended_action", "ALLOW") == expected_action:
                correct_actions += 1
            else:
                print(f"Failed Sample: '{text}'. Expected {expected_action}, got {result.risk_assessment.get('recommended_action')}")

    action_accuracy = (correct_actions / total_samples) * 100 if total_samples else 0
    avg_latency = total_latency_ms / total_samples if total_samples else 0

    print("="*50)
    print("OVERALL BENCHMARK RESULTS")
    print("="*50)
    print(f"Total Samples: {total_samples}")
    print(f"E2E Action Accuracy (%): {action_accuracy:.2f}")
    print(f"Average Total Latency (ms): {avg_latency:.2f}")
    
    # Generate Markdown report
    report_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    
    with open(report_path, 'w') as f:
        f.write("# Intelligence Pipeline End-to-End Benchmark\n")
        f.write(f"- **Total Samples:** {total_samples}\n")
        f.write(f"- **Action Accuracy:** {action_accuracy:.2f}%\n")
        f.write(f"- **Average Latency:** {avg_latency:.2f}ms\n")
        
    print(f"\nReport saved to: {report_path}")

if __name__ == "__main__":
    run_benchmarks()
