class BenchmarkMetrics:
    def __init__(self):
        self.true_positives = 0
        self.false_positives = 0
        self.false_negatives = 0
        self.total_latency_ms = 0.0
        self.latency_samples = 0

    def add_true_positive(self, category: str, lang: str, expected: str):
        self.true_positives += 1

    def add_false_positive(self, category: str, lang: str, detected: str):
        self.false_positives += 1

    def add_false_negative(self, category: str, lang: str, expected: str):
        self.false_negatives += 1

    def add_latency(self, ms: float):
        self.total_latency_ms += ms
        self.latency_samples += 1

    def precision(self) -> float:
        if self.true_positives + self.false_positives == 0:
            return 0.0
        return (self.true_positives / (self.true_positives + self.false_positives)) * 100

    def recall(self) -> float:
        if self.true_positives + self.false_negatives == 0:
            return 0.0
        return (self.true_positives / (self.true_positives + self.false_negatives)) * 100

    def f1_score(self) -> float:
        p = self.precision()
        r = self.recall()
        if p + r == 0:
            return 0.0
        return 2 * (p * r) / (p + r)

    def average_latency(self) -> float:
        if self.latency_samples == 0:
            return 0.0
        return self.total_latency_ms / self.latency_samples
