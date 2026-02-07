import ast
import os

def analyze_imports(filepath):
    print(f"Analyzing imports for: {filepath}")
    print("-" * 40)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=filepath)
        
        imports = []
        from_imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ""
                for alias in node.names:
                    from_imports.append(f"from {module} import {alias.name}")
                    
        print("Imports:")
        for i in sorted(imports):
            print(f"  {i}")
            
        print("\nFrom Imports:")
        for i in sorted(from_imports):
            print(f"  {i}")
            
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")

if __name__ == "__main__":
    analyze_imports("web/backend/app/api/risk_management.py")
    print("\n" + "="*60 + "\n")
    analyze_imports("web/backend/app/services/data_adapter.py")