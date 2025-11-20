#!/usr/bin/env python3
"""
调试API扫描过程
Debug API Scanning Process
"""

import os
import ast
from pathlib import Path

def debug_api_scan():
    """调试API扫描过程"""
    api_dir = Path("/opt/claude/mystocks_spec/web/backend/app/api")
    
    print(f"🔍 检查API目录: {api_dir}")
    print(f"目录是否存在: {api_dir.exists()}")
    
    if not api_dir.exists():
        print("❌ API目录不存在")
        return
    
    # 查找所有Python文件
    py_files = []
    py_files.extend(api_dir.glob("*.py"))
    
    v1_dir = api_dir / "v1"
    if v1_dir.exists():
        py_files.extend(v1_dir.glob("*.py"))
    
    print(f"📁 发现 {len(py_files)} 个Python文件")
    
    for file_path in py_files:
        print(f"\n📄 分析文件: {file_path}")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 解析AST
            tree = ast.parse(content)
            
            functions_found = 0
            router_functions = 0
            
            # 首先查找 router 定义
            has_router = False
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "router":
                            has_router = True
                            break
            
            if has_router:
                print(f"  ✅ 发现 router 定义")
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions_found += 1
                    
                    # 显示函数名
                    func_name = node.name
                    
                    # 检查装饰器
                    decorator_found = False
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call):
                            decorator_found = True
                            # 打印所有装饰器
                            if isinstance(decorator.func, ast.Attribute):
                                attr_name = decorator.func.attr
                                if isinstance(decorator.func.value, ast.Name):
                                    value_name = decorator.func.value.id
                                    print(f"  🔧 函数 {func_name}: @{value_name}.{attr_name}()")
                                    
                                    # 检查是否是路由函数
                                    if attr_name in ["get", "post", "put", "delete", "patch"] and value_name == "router":
                                        router_functions += 1
                                        print(f"    ✅ 发现API路由函数: {node.name}")
                                        
                                        # 尝试提取路径
                                        if decorator.args:
                                            path = decorator.args[0]
                                            if isinstance(path, ast.Constant):
                                                print(f"    📍 路径: {path.value}")
                            
                            elif isinstance(decorator.func, ast.Name):
                                name = decorator.func.id
                                print(f"  🔧 函数 {func_name}: @{name}")
                    
                    if not decorator_found:
                        print(f"  📝 函数 {func_name}: 无装饰器")
            
            print(f"  📊 总结: {functions_found} 个函数, {router_functions} 个API路由函数")
            
        except Exception as e:
            print(f"  ❌ 解析失败: {e}")

if __name__ == "__main__":
    debug_api_scan()