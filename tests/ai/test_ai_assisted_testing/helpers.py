#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks AI辅助测试工具
提供智能测试用例生成、优化和故障诊断
集成AST分析和项目上下文感知
"""

import ast
import asyncio
import hashlib
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import pytest

class TestPriority(Enum):
    """测试优先级"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestCategory(Enum):
    """测试类别"""

    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPATIBILITY = "compatibility"


@dataclass
class TestCase:
    """增强的测试用例数据结构"""

    name: str
    description: str
    code: str
    method_name: str
    coverage: List[str]
    complexity_score: float
    priority: TestPriority
    category: TestCategory
    dependencies: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    execution_time_estimate: float = 0.0
    flakiness_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    """增强的代码分析结果"""

    method_name: str
    complexity: int
    length: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    coupling_score: float
    cohesion_score: float
    test_coverage: List[str]
    dependencies: List[str]
    risk_level: str  # low, medium, high
    security_issues: List[str]
    performance_issues: List[str]
    maintainability_score: float


class ProjectContextAnalyzer:
    """项目上下文分析器"""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.context_cache = {}

    def get_project_structure(self) -> Dict[str, Any]:
        """获取项目结构"""
        if "structure" in self.context_cache:
            return self.context_cache["structure"]

        structure = {
            "modules": [],
            "config_files": [],
            "test_files": [],
            "api_endpoints": [],
            "business_entities": [],
        }

        # 扫描项目目录
        for root, dirs, files in os.walk(self.project_root):
            root_path = Path(root)

            # 排除特定目录
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["__pycache__", "node_modules"]]

            # 分析模块
            if "__init__.py" in files:
                module_path = root_path.relative_to(self.project_root)
                structure["modules"].append(str(module_path))

            # 收集配置文件
            for file in files:
                if file.endswith((".yaml", ".yml", ".json", ".toml", ".ini")):
                    structure["config_files"].append(str(root_path / file))

            # 收集测试文件
            if "test_" in file or file.endswith("_test.py"):
                structure["test_files"].append(str(root_path / file))

        self.context_cache["structure"] = structure
        return structure

    def detect_patterns(self, source_code: str) -> Dict[str, Any]:
        """检测代码模式"""
        patterns = {
            "data_models": [],
            "api_handlers": [],
            "business_logic": [],
            "utility_functions": [],
            "external_calls": [],
        }

        tree = ast.parse(source_code)

        for node in ast.walk(tree):
            # 检测数据模型（Pydantic类）
            if isinstance(node, ast.ClassDef) and any(
                isinstance(base, ast.Attribute) and base.attr == "BaseModel"
                for base in node.bases
                if isinstance(base, ast.Attribute)
            ):
                patterns["data_models"].append(node.name)

            # 检测API处理器
            elif isinstance(node, ast.FunctionDef) and (
                "api" in node.name.lower() or "endpoint" in node.name.lower() or "route" in node.name.lower()
            ):
                patterns["api_handlers"].append(node.name)

            # 检测业务逻辑
            elif isinstance(node, ast.FunctionDef) and any(
                keyword in node.name.lower()
                for keyword in [
                    "calculate",
                    "get",
                    "set",
                    "update",
                    "process",
                    "analyze",
                ]
            ):
                patterns["business_logic"].append(node.name)

            # 检测外部调用
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == "requests":
                    patterns["external_calls"].append("HTTP requests detected")
                elif isinstance(node.func, ast.Attribute) and node.func.attr == "fetch":
                    patterns["external_calls"].append("Data fetch detected")

        return patterns


