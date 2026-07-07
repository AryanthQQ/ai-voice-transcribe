import os
import re
import sys

def get_imports():
    imports = set()
    import_regex = re.compile(r'^(?:from|import)\s+([a-zA-Z0-9_]+)')
    for root, _, files in os.walk('.'):
        if 'venv' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    for line in f:
                        match = import_regex.match(line.strip())
                        if match:
                            imports.add(match.group(1))
    return sorted(list(imports))

if __name__ == "__main__":
    found_imports = get_imports()
    print("Detected Top-Level Imports:")
    for imp in found_imports:
        print(f" - {imp}")
