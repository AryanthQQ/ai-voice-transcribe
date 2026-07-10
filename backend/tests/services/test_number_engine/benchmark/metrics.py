import time

class BenchmarkMetrics:
    """
    Evaluation metrics for the Number Intelligence Engine.
    """
    
    def __init__(self):
        self.total_samples = 0
        self.true_positives = 0
        self.false_positives = 0
        self.false_negatives = 0
        self.exact_value_matches = 0
        self.validation_matches = 0
        self.entity_type_matches = 0
        self.total_latency_ms = 0.0

    def update(self, expected_value: str, expected_entity: str, expected_valid: bool, extracted_entities: list, latency_ms: float = 0.0):
        self.total_samples += 1
        self.total_latency_ms += latency_ms
        
        if not expected_value and not extracted_entities:
            # True negative scenario
            self.true_positives += 1
            return

        if expected_value and not extracted_entities:
            self.false_negatives += 1
            return

        if not expected_value and extracted_entities:
            self.false_positives += 1
            return

        # We have both expected and extracted
        # Take the best match or first match for simplicity
        best_match = extracted_entities[0]
        
        # Check extraction accuracy
        if best_match["normalized_value"] == expected_value:
            self.exact_value_matches += 1
            self.true_positives += 1
        else:
            self.false_positives += 1

        # Check entity type accuracy
        if best_match["entity_type"] == expected_entity:
            self.entity_type_matches += 1

        # Check validation accuracy
        is_valid = best_match.get("validation_result", {}).get("is_valid", False)
        if is_valid == expected_valid:
            self.validation_matches += 1

    def calculate_stats(self):
        accuracy = (self.true_positives / self.total_samples) if self.total_samples else 0
        precision = (self.true_positives / (self.true_positives + self.false_positives)) if (self.true_positives + self.false_positives) else 0
        recall = (self.true_positives / (self.true_positives + self.false_negatives)) if (self.true_positives + self.false_negatives) else 0
        
        f1_score = 0
        if precision + recall > 0:
            f1_score = 2 * (precision * recall) / (precision + recall)
            
        val_accuracy = (self.validation_matches / self.total_samples) if self.total_samples else 0
        ent_accuracy = (self.entity_type_matches / self.total_samples) if self.total_samples else 0
        avg_latency = (self.total_latency_ms / self.total_samples) if self.total_samples else 0
        
        return {
            "Total Samples": self.total_samples,
            "True Positives": self.true_positives,
            "False Positives": self.false_positives,
            "False Negatives": self.false_negatives,
            "Extraction Accuracy (%)": round(accuracy * 100, 2),
            "Precision (%)": round(precision * 100, 2),
            "Recall (%)": round(recall * 100, 2),
            "F1 Score (%)": round(f1_score * 100, 2),
            "Validation Accuracy (%)": round(val_accuracy * 100, 2),
            "Entity Type Accuracy (%)": round(ent_accuracy * 100, 2),
            "Average Latency (ms)": round(avg_latency, 2)
        }

    def report(self):
        stats = self.calculate_stats()
        return {
            k: f"{v}%" if "(%)" in k else str(v)
            for k, v in stats.items()
        }
