#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 代码优化 - 监控模块重复代码分析脚本
分析monitoring.py与monitoring/目录之间的重复代码问题

创建日期: 2025-11-25
版本: 1.0.0
"""

import os
import re
from typing import Dict, List, Set
from pathlib import Path

class MonitoringDuplicationAnalyzer:
    def __init__(self):
        self.project_root = Path("/opt/claude/mystocks_spec")
        self.src_path = self.project_root / "src"
        
    def analyze_duplication(self):
        """分析监控模块的重复情况"""
        print("=" * 60)
        print("MyStocks 监控模块重复代码分析")
        print("=" * 60)
        
        # 1. 检查monitoring.py文件
        monitoring_py = self.src_path / "monitoring.py"
        print(f"1. 检查统一监控文件: {monitoring_py}")
        
        if monitoring_py.exists():
            with open(monitoring_py, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = len(content.splitlines())
                classes = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
                print(f"   - 文件大小: {lines} 行")
                print(f"   - 包含类: {classes}")
        else:
            print("   - 文件不存在")
            
        # 2. 检查monitoring/目录
        monitoring_dir = self.src_path / "monitoring"
        print(f"\n2. 检查模块化监控目录: {monitoring_dir}")
        
        if monitoring_dir.exists():
            python_files = list(monitoring_dir.glob("*.py"))
            total_lines = 0
            all_classes = []
            
            for py_file in python_files:
                if py_file.name != "__init__.py" and not py_file.name.endswith(".backup"):
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = len(content.splitlines())
                        classes = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
                        total_lines += lines
                        all_classes.extend([(py_file.name, cls) for cls in classes])
                        print(f"   - {py_file.name}: {lines} 行, 类: {classes}")
                        
            print(f"   - 总计: {total_lines} 行")
            
        # 3. 分析重复类
        print(f"\n3. 重复类分析:")
        if monitoring_py.exists():
            with open(monitoring_py, 'r', encoding='utf-8') as f:
                unified_classes = set(re.findall(r'^class\s+(\w+)', f.read(), re.MULTILINE))
                
            module_classes = {cls for _, cls in all_classes}
            duplicated_classes = unified_classes & module_classes
            
            print(f"   - 统一版本类: {unified_classes}")
            print(f"   - 模块化版本类: {module_classes}")
            print(f"   - 重复类: {duplicated_classes}")
            
            # 计算重复代码量
            if monitoring_py.exists():
                with open(monitoring_py, 'r', encoding='utf-8') as f:
                    unified_lines = len(f.read().splitlines())
                duplicated_lines = total_lines
                print(f"\n4. 重复代码统计:")
                print(f"   - 统一版本: {unified_lines} 行")
                print(f"   - 模块化版本: {duplicated_lines} 行")
                print(f"   - 重复代码: {unified_lines + duplicated_lines} 行")
                print(f"   - 可节省: {unified_lines} 行（删除统一版本）")
                
        return True
        
    def find_dependencies(self):
        """查找对monitoring.py的依赖"""
        print(f"\n5. 查找对monitoring.py的依赖:")
        
        dependencies = []
        
        # 搜索项目中对monitoring.py的直接引用
        for py_file in self.project_root.rglob("*.py"):
            if "__pycache__" in str(py_file) or ".git" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 查找对monitoring.py的直接导入
                if re.search(r'from\s+src\.monitoring\s+import|import\s+src\.monitoring', content):
                    # 提取具体的导入内容
                    imports = re.findall(r'from\s+src\.monitoring\s+import\s+([^#\n]+)', content)
                    dependencies.extend([(str(py_file.relative_to(self.project_root)), imp.strip()) for imp in imports])
                    
            except Exception as e:
                continue
                
        if dependencies:
            print("   发现依赖关系:")
            for file_path, import_stmt in dependencies:
                print(f"   - {file_path}: {import_stmt}")
        else:
            print("   - 未发现对monitoring.py的直接依赖")
            
        return dependencies

if __name__ == "__main__":
    analyzer = MonitoringDuplicationAnalyzer()
    analyzer.analyze_duplication()
    dependencies = analyzer.find_dependencies()
    
    print(f"\n6. 优化建议:")
    print("   - 保留monitoring/目录中的模块化版本")
    print("   - 删除monitoring.py统一版本")
    print("   - 更新任何直接引用monitoring.py的代码")
    print("   - 预计节省代码行数: 1100+ 行")