import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from app.services.intelligence.number_engine import NumberEngine
from app.services.intelligence.number_engine.models.input import TranscriptSegment
from tests.services.test_number_engine.benchmark.metrics import BenchmarkMetrics

BASE_DIR = Path(__file__).parent / "datasets"
REPORTS_DIR = Path(__file__).parent / "reports"

def load_dataset(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def run_benchmarks():
    engine = NumberEngine()
    
    overall_metrics = BenchmarkMetrics()
    category_metrics = {}
    language_metrics = {}
    entity_metrics = {}
    
    print("Starting Number Engine Benchmarks...\n")
    
    for category_dir in BASE_DIR.iterdir():
        if category_dir.is_dir():
            category_name = category_dir.name
            category_metrics[category_name] = BenchmarkMetrics()
            
            for file_path in category_dir.glob("*.jsonl"):
                for sample in load_dataset(file_path):
                    
                    segment = TranscriptSegment(
                        text=sample["text"],
                        start=0.0,
                        end=5.0,
                        speaker="SPEAKER_01",
                        confidence=0.9
                    )
                    
                    # Measure latency
                    start_time = time.perf_counter()
                    extracted = engine.extract_entities([segment.model_dump()])
                    end_time = time.perf_counter()
                    latency_ms = (end_time - start_time) * 1000
                    
                    # Update Overall and Category
                    overall_metrics.update(
                        expected_value=sample.get("expected_value"),
                        expected_entity=sample.get("expected_entity"),
                        expected_valid=sample.get("expected_valid"),
                        extracted_entities=extracted,
                        latency_ms=latency_ms
                    )
                    
                    category_metrics[category_name].update(
                        expected_value=sample.get("expected_value"),
                        expected_entity=sample.get("expected_entity"),
                        expected_valid=sample.get("expected_valid"),
                        extracted_entities=extracted,
                        latency_ms=latency_ms
                    )
                    
                    # Update Language Metrics
                    for lang in sample.get("language_tags", ["unknown"]):
                        if lang not in language_metrics:
                            language_metrics[lang] = BenchmarkMetrics()
                        language_metrics[lang].update(
                            expected_value=sample.get("expected_value"),
                            expected_entity=sample.get("expected_entity"),
                            expected_valid=sample.get("expected_valid"),
                            extracted_entities=extracted,
                            latency_ms=latency_ms
                        )
                        
                    # Update Entity Metrics
                    expected_entity = sample.get("expected_entity", "UNKNOWN")
                    if expected_entity not in entity_metrics:
                        entity_metrics[expected_entity] = BenchmarkMetrics()
                    entity_metrics[expected_entity].update(
                        expected_value=sample.get("expected_value"),
                        expected_entity=sample.get("expected_entity"),
                        expected_valid=sample.get("expected_valid"),
                        extracted_entities=extracted,
                        latency_ms=latency_ms
                    )
                    
    generate_reports(overall_metrics, category_metrics, language_metrics, entity_metrics)

def generate_reports(overall, categories, languages, entities):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_data = {
        "timestamp": timestamp,
        "overall": overall.calculate_stats(),
        "categories": {k: v.calculate_stats() for k, v in categories.items()},
        "languages": {k: v.calculate_stats() for k, v in languages.items()},
        "entities": {k: v.calculate_stats() for k, v in entities.items()}
    }
    
    # 1. Console Summary
    print_console_summary(report_data)
    
    # 2. JSON Report
    json_path = REPORTS_DIR / f"report_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=4)
        
    # 3. Markdown Report
    md_path = REPORTS_DIR / f"report_{timestamp}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Benchmark Report ({timestamp})\n\n")
        f.write("## Overall Metrics\n")
        for k, v in overall.report().items():
            f.write(f"- **{k}**: {v}\n")
        
        f.write("\n## By Category\n")
        for k, v in categories.items():
            f.write(f"### {k}\n")
            for mk, mv in v.report().items():
                f.write(f"- {mk}: {mv}\n")
                
        f.write("\n## By Language\n")
        for k, v in languages.items():
            f.write(f"### {k}\n")
            for mk, mv in v.report().items():
                f.write(f"- {mk}: {mv}\n")
                
        f.write("\n## By Entity Type\n")
        for k, v in entities.items():
            f.write(f"### {k}\n")
            for mk, mv in v.report().items():
                f.write(f"- {mk}: {mv}\n")
                
    # 4. HTML Report
    html_path = REPORTS_DIR / f"report_{timestamp}.html"
    with open(html_path, "w", encoding="utf-8") as f:
        html = f"""
        <html>
        <head>
            <title>Benchmark Report {timestamp}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 30px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                h2 {{ color: #333; border-bottom: 2px solid #333; padding-bottom: 5px; }}
            </style>
        </head>
        <body>
            <h1>Benchmark Report: {timestamp}</h1>
            
            <h2>Overall Metrics</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                {"".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in overall.report().items())}
            </table>
            
            <h2>By Language</h2>
            <table>
                <tr><th>Language</th><th>Total Samples</th><th>Extraction Accuracy</th><th>F1 Score</th></tr>
                {"".join(f"<tr><td>{lang}</td><td>{metrics.calculate_stats()['Total Samples']}</td><td>{metrics.report()['Extraction Accuracy (%)']}</td><td>{metrics.report()['F1 Score (%)']}</td></tr>" for lang, metrics in languages.items())}
            </table>
            
            <h2>By Category</h2>
            <table>
                <tr><th>Category</th><th>Total Samples</th><th>Extraction Accuracy</th><th>F1 Score</th></tr>
                {"".join(f"<tr><td>{cat}</td><td>{metrics.calculate_stats()['Total Samples']}</td><td>{metrics.report()['Extraction Accuracy (%)']}</td><td>{metrics.report()['F1 Score (%)']}</td></tr>" for cat, metrics in categories.items())}
            </table>
        </body>
        </html>
        """
        f.write(html)
        
    print(f"\nReports saved in: {REPORTS_DIR}")

def print_console_summary(report_data):
    print("=" * 50)
    print("OVERALL BENCHMARK RESULTS")
    print("=" * 50)
    for k, v in report_data["overall"].items():
        print(f"{k}: {v}")
    
    print("\n" + "=" * 50)
    print("LANGUAGE PERFORMANCE SUMMARY")
    print("=" * 50)
    for lang, stats in report_data["languages"].items():
        print(f"[{lang}] Accuracy: {stats['Extraction Accuracy (%)']}% | F1: {stats['F1 Score (%)']}%")
        
    print("\n" + "=" * 50)
    print("ENTITY PERFORMANCE SUMMARY")
    print("=" * 50)
    for ent, stats in report_data["entities"].items():
        print(f"[{ent}] Accuracy: {stats['Extraction Accuracy (%)']}% | F1: {stats['F1 Score (%)']}%")
        
if __name__ == "__main__":
    run_benchmarks()
