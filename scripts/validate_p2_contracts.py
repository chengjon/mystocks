#!/usr/bin/env python3
"""验证P2 API契约"""

import yaml
from pathlib import Path

def validate_contracts():
    """验证契约文件"""
    p2_dir = Path("/opt/claude/mystocks_phase7_backend/contracts/p2")
    
    issues = []
    total = 0
    
    for yaml_file in p2_dir.rglob("*.yaml"):
        if yaml_file.name == "index.yaml":
            continue
            
        total += 1
        with open(yaml_file, "r", encoding="utf-8") as f:
            try:
                contract = yaml.safe_load(f)
                
                # 验证必需字段
                required_fields = ["api_id", "priority", "module", "path", "method", "description"]
                for field in required_fields:
                    if field not in contract:
                        issues.append(f"{yaml_file.name}: 缺少字段 {field}")
                
                # 验证priority
                if contract.get("priority") != "P2":
                    issues.append(f"{yaml_file.name}: priority应为P2")
                
                # 验证method
                if contract.get("method") not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    issues.append(f"{yaml_file.name}: 无效的method {contract.get('method')}")
                    
            except Exception as e:
                issues.append(f"{yaml_file.name}: 解析错误 - {str(e)}")
    
    print(f"✅ 契约验证完成")
    print(f"   总计: {total}个契约")
    print(f"   问题: {len(issues)}个")
    
    if issues:
        print("\n问题列表:")
        for issue in issues[:10]:  # 只显示前10个
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... 还有{len(issues)-10}个问题")
    else:
        print("   所有契约验证通过! ✅")
    
    return len(issues) == 0

if __name__ == "__main__":
    validate_contracts()
