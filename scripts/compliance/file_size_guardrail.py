import os
import sys

# 定义工程红线 (ArtDeco 3.1)
# Python > 800行, TS/Vue > 500行, 测试文件 > 1000行
LIMITS = {
    ".py": 800,
    ".ts": 500,
    ".vue": 500,
    ".spec.ts": 1000,
    ".spec.js": 1000
}

def check_files():
    violations = []
    
    for root, _, files in os.walk("."):
        # 排除无关目录
        if any(x in root for x in ["node_modules", ".git", "archived", ".venv", "__pycache__"]):
            continue
            
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext not in LIMITS:
                continue
                
            path = os.path.join(root, file)
            # 针对测试文件调整后缀判断
            if file.endswith(".spec.ts"): ext = ".spec.ts"
            elif file.endswith(".spec.js"): ext = ".spec.js"
            
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = sum(1 for _ in f)
                    if lines > LIMITS[ext]:
                        violations.append(f"🚩 {path}: {lines} lines (Limit: {LIMITS[ext]})")
            except Exception:
                continue
                
    return violations

if __name__ == "__main__":
    v = check_files()
    if v:
        print("\n".join(v))
        print(f"\n❌ Total {len(v)} violations found.")
        sys.exit(1)
    print("✅ All files comply with ArtDeco size limits.")
