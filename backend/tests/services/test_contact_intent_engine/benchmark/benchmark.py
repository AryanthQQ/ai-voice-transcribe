import os
import json
from datetime import datetime
from metrics import BenchmarkMetrics
from backend.app.services.intelligence.contact_intent_engine.engine import ContactIntentEngine
from backend.app.services.intelligence.contact_intent_engine.models import IntentInput

def run_benchmarks():
    print("Starting Contact Intent Engine Benchmarks...\n")
    engine = ContactIntentEngine()
    metrics = BenchmarkMetrics()
    
    datasets_dir = os.path.join(os.path.dirname(__file__), "datasets")
    if not os.path.exists(datasets_dir):
        print(f"Datasets directory not found at {datasets_dir}")
        return

    for filename in os.listdir(datasets_dir):
        if not filename.endswith(".json"):
            continue
            
        filepath = os.path.join(datasets_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
            
        category = dataset.get("category", "unknown")
        
        for sample in dataset.get("samples", []):
            text = sample.get("text", "")
            expected_intents = sample.get("expected_intents", [])
            lang = sample.get("language", "en")
            
            input_data = IntentInput(
                text=text,
                start=0.0,
                end=2.0,
                speaker="SPEAKER_00",
                confidence=0.9,
                detected_language=lang
            )
            
            # Run engine and measure latency
            start_time = datetime.now()
            results = engine.process(input_data)
            latency = (datetime.now() - start_time).total_seconds() * 1000
            
            # Simple evaluation: Did we extract all expected intents?
            detected_channels = [r.channel for r in results]
            expected_channels = [e["channel"] for e in expected_intents]
            
            # Handle true positive tracking
            for expected in expected_channels:
                if expected in detected_channels:
                    metrics.add_true_positive(category, lang, expected)
                else:
                    metrics.add_false_negative(category, lang, expected)
                    
            # Handle false positive tracking
            for detected in detected_channels:
                if detected not in expected_channels:
                    metrics.add_false_positive(category, lang, detected)
                    
            # For exact matches without expecting any, if we found nothing, it's a true negative (which is correct).
            # But the metric class tracks precision/recall based on TP/FP/FN.
            
            metrics.add_latency(latency)

    print("="*50)
    print("OVERALL BENCHMARK RESULTS")
    print("="*50)
    print(f"Total True Positives: {metrics.true_positives}")
    print(f"Total False Positives: {metrics.false_positives}")
    print(f"Total False Negatives: {metrics.false_negatives}")
    
    precision = metrics.precision()
    recall = metrics.recall()
    f1 = metrics.f1_score()
    
    print(f"Precision (%): {precision:.2f}")
    print(f"Recall (%): {recall:.2f}")
    print(f"F1 Score (%): {f1:.2f}")
    print(f"Average Latency (ms): {metrics.average_latency():.2f}")
    
    # Let's generate a simple Markdown report
    report_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    
    with open(report_path, 'w') as f:
        f.write("# Contact Intent Engine Benchmark\n")
        f.write(f"- **Precision:** {precision:.2f}%\n")
        f.write(f"- **Recall:** {recall:.2f}%\n")
        f.write(f"- **F1 Score:** {f1:.2f}%\n")
        f.write(f"- **Latency:** {metrics.average_latency():.2f}ms\n")
        
    print(f"\nReport saved to: {report_path}")

if __name__ == "__main__":
    run_benchmarks()
