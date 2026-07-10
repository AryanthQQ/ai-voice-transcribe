import json
from pathlib import Path

BASE_DIR = Path("backend/tests/services/test_number_engine/benchmark/datasets")

datasets = {
    "phone_numbers": [
        {"text": "my phone number is nine eight seven six five four three two one zero", "expected_entity": "PHONE_NUMBER", "expected_value": "9876543210", "expected_valid": True, "language_tags": ["en"]},
        {"text": "mera number hai nau aath saat chhe paanch chaar teen do ek shunya", "expected_entity": "PHONE_NUMBER", "expected_value": "9876543210", "expected_valid": True, "language_tags": ["hi"]},
        {"text": "maza number aahe nau aath saat saha paach chaar teen don ek shunya", "expected_entity": "PHONE_NUMBER", "expected_value": "9876543210", "expected_valid": True, "language_tags": ["mr"]},
        {"text": "maro number nav aath saat chha paanch chaar tran be ek shunya", "expected_entity": "PHONE_NUMBER", "expected_value": "9876543210", "expected_valid": True, "language_tags": ["gu"]}
    ],
    "otp": [
        {"text": "your otp is double four two one", "expected_entity": "OTP", "expected_value": "4421", "expected_valid": True, "language_tags": ["en"]},
        {"text": "one time password hai six seven eight nine zero", "expected_entity": "OTP", "expected_value": "67890", "expected_valid": True, "language_tags": ["hi", "en"]}
    ],
    "aadhaar": [
        {"text": "mera aadhaar number hai one two three four five six seven eight nine zero one two", "expected_entity": "AADHAAR", "expected_value": "123456789012", "expected_valid": True, "language_tags": ["hi", "en"]}
    ],
    "pan": [
        {"text": "mera pan card number hai a b c d e one two three four f", "expected_entity": "PAN", "expected_value": None, "expected_valid": False, "language_tags": ["hi", "en"]}
    ],
    "bank_account": [
        {"text": "account number hai one two three four five six seven eight nine", "expected_entity": "BANK_ACCOUNT", "expected_value": "123456789", "expected_valid": True, "language_tags": ["hi", "en"]}
    ],
    "upi": [
        {"text": "mera gpay number hai nine eight seven six five four three two one zero", "expected_entity": "UPI_ID", "expected_value": "9876543210", "expected_valid": True, "language_tags": ["hi", "en"]}
    ],
    "invalid": [
        {"text": "my number is one two three four five six seven eight nine zero", "expected_entity": "PHONE_NUMBER", "expected_value": "1234567890", "expected_valid": False, "language_tags": ["en"]}
    ],
    "partial": [
        {"text": "my number is nine eight seven", "expected_entity": "PHONE_NUMBER", "expected_value": "987", "expected_valid": False, "language_tags": ["en"]}
    ],
    "mixed_language": [
        {"text": "phone nine aath saat chha double two char panch six zero", "expected_entity": "PHONE_NUMBER", "expected_value": "9876224560", "expected_valid": True, "language_tags": ["en", "hi", "gu", "mr"]}
    ]
}

def generate_datasets():
    for category, samples in datasets.items():
        file_path = BASE_DIR / category / "sample.jsonl"
        with open(file_path, "w", encoding="utf-8") as f:
            for sample in samples:
                f.write(json.dumps(sample) + "\n")
        print(f"Generated {file_path}")

if __name__ == "__main__":
    generate_datasets()
