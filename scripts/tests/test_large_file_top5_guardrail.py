import os
import sys
from pathlib import Path

# ArtDeco 3.1 Engineering Red Lines
LIMITS = {
    ".py": 800,
    ".ts": 500,
    ".vue": 500,
    ".js": 800,
    ".spec.ts": 1000,
    ".spec.js": 1000
}

# Explicitly tracked "Top 5" targets for governance
TOP_5_TARGETS = [
    "web/frontend/src/api/types/common.ts",
    "web/backend/app/api/data.py",
    "web/frontend/tests/api-automation.spec.js",
    "scripts/tests/web-usability-runner.js",
    "src/core/unified_manager.py"
]

def check_top5_compliance():
    violations = []
    print("🔍 [Guardrail] Monitoring Top 5 Target Compliance...")
    
    for rel_path in TOP_5_TARGETS:
        abs_path = Path(rel_path)
        if not abs_path.exists():
            print(f"  ⚪ {rel_path} not found (may have been renamed or moved)")
            continue
            
        ext = abs_path.suffix
        limit = LIMITS.get(ext, 800)
        
        # Special check for test files
        if rel_path.endswith(".spec.js") or rel_path.endswith(".spec.ts"):
            limit = 1000

        with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = sum(1 for _ in f)
            if lines > limit:
                violations.append(f"🚩 {rel_path}: {lines} lines (Limit: {limit})")
            else:
                print(f"  ✅ {rel_path}: {lines} lines (OK)")
                
    return violations

if __name__ == "__main__":
    v = check_top5_compliance()
    if v:
        print("\n❌ [Violation] Large files detected in Top 5 targets:")
        print("\n".join(v))
        sys.exit(1)
    print("\n✅ All Top 5 targets comply with governance standards.")
