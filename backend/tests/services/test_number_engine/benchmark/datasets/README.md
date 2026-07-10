# Number Intelligence Engine Datasets

This directory contains benchmark datasets used for evaluating the accuracy, precision, and recall of the `NumberEngine`.

## Directory Structure
The datasets are organized by category to test different aspects of the engine:

- `phone_numbers`: Valid Indian mobile/landline numbers.
- `otp`: Short numerical strings with context clues (e.g. "my OTP is").
- `aadhaar`: 12-digit patterns.
- `pan`: Alphanumeric patterns (future scope for the engine).
- `bank_account`: Variable length numerical patterns.
- `upi`: Numerical strings linked to UPI IDs or phone numbers used for UPI.
- `invalid`: Valid sequences of number words that violate Indian phone validation rules (e.g., 10 digits starting with 1).
- `partial`: Snippets of spoken numbers that are interrupted or incomplete.
- `mixed_language`: Sentences that heavily code-switch between languages (e.g., English and Hindi) mid-number.

## File Format
Datasets are stored in JSON Lines (`.jsonl`) format. This allows for streaming reads and easy append operations for future scaling.

### Schema Requirements
Each line in a `.jsonl` file must conform to the following schema:
```json
{
  "text": "The raw transcript text containing the spoken number.",
  "expected_entity": "The expected entity type (e.g., 'PHONE_NUMBER', 'OTP', 'AADHAAR'). Use null if none expected.",
  "expected_value": "The normalized absolute numeric string (e.g., '9876543210'). Use null if none expected.",
  "expected_valid": true, // Boolean indicating if the number should pass validation.
  "language_tags": ["en", "hi"] // Array of expected predominant languages or code-switches.
}
```

### Adding New Datasets
When adding support for new languages (e.g., Bengali, Tamil), simply create new `.jsonl` files in the appropriate category directories and append new lines conforming to the schema. The benchmark runner will automatically discover and evaluate them.
