import os

def is_generated(filepath):
    """Check if a file is likely generated or a library."""
    if "node_modules" in filepath: return True
    if "dist" in filepath: return True
    if "build" in filepath: return True
    if "generated" in filepath: return True
    if "site-packages" in filepath: return True
    if filepath.endswith(".d.ts"): return True
    if filepath.endswith(".min.js"): return True
    if filepath.endswith("package-lock.json"): return True
    if filepath.endswith("yarn.lock"): return True
    if ".git" in filepath: return True
    if "coverage" in filepath: return True
    if "htmlcov" in filepath: return True
    if "__pycache__" in filepath: return True
    return False

def is_target_ext(filepath):
    """Check if file is a target extension."""
    return filepath.endswith(".py") or filepath.endswith(".vue")

def count_lines(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0

def scan_files(root_dir):
    large_files = []
    for root, dirs, files in os.walk(root_dir):
        # Exclude common ignore dirs in-place to save traversal
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', 'dist', 'build', 'coverage', 'htmlcov']]
        
        for file in files:
            filepath = os.path.join(root, file)
            if is_generated(filepath):
                continue
            if not is_target_ext(filepath):
                continue
            
            # Additional exclusion for tests and docs directories if they appear in path
            if "/tests/" in filepath or "/docs/" in filepath:
                continue
                
            lines = count_lines(filepath)
            if lines > 1000:
                large_files.append((lines, filepath))
    
    return large_files

if __name__ == "__main__":
    results = scan_files(".")
    results.sort(key=lambda x: x[0], reverse=True)
    
    print(f"{'Lines':<10} {'File Path'}")
    print("-" * 80)
    for lines, path in results:
        print(f"{lines:<10} {path}")
