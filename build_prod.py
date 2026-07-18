import os
from pathlib import Path
import zipfile

def create_deployment_package():
    src_dir = Path(__file__).resolve().parent
    zip_path = src_dir / "production_package.zip"
    
    print(f"Creating production package at {zip_path}...")
    
    exclude_patterns = [
        ".git",
        ".pytest_cache",
        "__pycache__",
        "build_prod.py",
        "production_package.zip",
        "public/bad_words.txt", 
        "mcp", 
        "node_modules",
        "venv",
        ".env",
    ]
    
    def should_exclude(rel_path_str, filename):
        if any(ex in rel_path_str for ex in exclude_patterns) or any(rel_path_str.startswith(ex) for ex in exclude_patterns):
            return True
            
        if filename.startswith("test_") and filename.endswith(".py") and "\\" not in rel_path_str and "/" not in rel_path_str:
            return True
            
        if filename.startswith("make_") and filename.endswith(".py"):
            return True
            
        if filename.endswith("_baseline.json"):
            return True
            
        return False

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(src_dir):
            # Prune excluded directories in-place so os.walk doesn't traverse them
            dirs[:] = [d for d in dirs if not any(d == ex or root.replace(str(src_dir), "").strip("\\/") == ex for ex in exclude_patterns)]
            
            for file in files:
                abs_path = Path(root) / file
                rel_path = abs_path.relative_to(src_dir)
                rel_path_str = rel_path.as_posix()
                
                if not should_exclude(rel_path_str, file):
                    zipf.write(abs_path, rel_path)
                    
    print("production_package.zip created successfully.")

if __name__ == "__main__":
    create_deployment_package()
