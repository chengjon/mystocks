#!/usr/bin/env python3
"""
MyStocks API和Web前端数据使用分析工具（增强版）
支持增量分析、更准确的API调用提取和可视化报告
"""

import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple
from hashlib import md5

class APIAnalyzer:
    """分析后端API端点"""

    def __init__(self, api_dir: str):
        self.api_dir = Path(api_dir)
        self.api_endpoints: List[Dict] = []
        self.pydantic_models: Dict[str, List[str]] = {}
        self.file_hashes: Dict[str, str] = {}

    def analyze(self, incremental: bool = False) -> List[Dict]:
        """分析所有API文件"""
        print("🔍 扫描API端点...")

        if incremental:
            print("  模式: 增量分析")
            self._load_cache()

        for py_file in self.api_dir.rglob("*.py"):
            if "test" in py_file.name or "__pycache__" in str(py_file):
                continue

            # 增量分析：跳过未修改的文件
            if incremental:
                current_hash = self._calculate_file_hash(py_file)
                rel_path = str(py_file.relative_to(self.api_dir))
                if rel_path in self.file_hashes and self.file_hashes[rel_path] == current_hash:
                    continue
                self.file_hashes[rel_path] = current_hash

            self._analyze_python_file_with_regex(py_file)

        print(f"✅ 找到 {len(self.api_endpoints)} 个API端点")
        print(f"✅ 找到 {len(self.pydantic_models)} 个数据模型")

        if incremental:
            self._save_cache()

        return self.api_endpoints

    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件hash用于增量分析"""
        try:
            with open(file_path, "rb") as f:
                return md5(f.read()).hexdigest()
        except:
            return ""

    def _load_cache(self):
        """加载增量分析缓存"""
        cache_file = self.api_dir / ".analysis_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    cache = json.load(f)
                    self.file_hashes = cache.get("file_hashes", {})
            except:
                pass

    def _save_cache(self):
        """保存增量分析缓存"""
        cache_file = self.api_dir / ".analysis_cache.json"
        try:
            with open(cache_file, "w") as f:
                json.dump({"file_hashes": self.file_hashes}, f)
        except:
            pass

    def _analyze_python_file_with_regex(self, file_path: Path):
        """使用正则表达式分析Python文件提取API信息"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 提取路由定义
            # 匹配 @router.get("/path") 或 @app.get("/path") 格式
            route_pattern = r'@(?:router|app)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
            matches = list(re.finditer(route_pattern, content))

            for match in matches:
                method = match.group(1).upper()
                path = match.group(2)

                # 查找对应的函数定义
                func_match = re.search(r"async\s+def\s+(\w+)\s*\(", content[match.end() : match.end() + 500])
                if func_match:
                    func_name = func_match.group(1)

                    # 提取函数内容
                    func_start = match.end() + func_match.end()
                    func_end = self._find_function_end(content, func_start)

                    # 获取函数内容
                    func_content = content[func_start:func_end]

                    # 提取返回模型
                    return_model = self._extract_return_model_from_content(content, match.start())

                    # 提取数据字段
                    data_fields = self._extract_data_fields_from_content(func_content, return_model)

                    # 检查数据库依赖
                    db_dependencies = self._extract_db_dependencies(func_content)

                    # 判断数据源类型
                    source_type = self._determine_source_type(func_content)

                    # 计算文件相对路径
                    rel_path = str(file_path.relative_to(self.api_dir))
                    line_number = content[: match.start()].count("\n") + 1

                    endpoint_info = {
                        "path": path,
                        "method": method,
                        "file": rel_path,
                        "function": func_name,
                        "return_model": return_model,
                        "data_fields": data_fields,
                        "db_dependencies": db_dependencies,
                        "source_type": source_type,
                        "line_number": line_number,
                    }

                    self.api_endpoints.append(endpoint_info)

            # 提取Pydantic模型
            self._extract_pydantic_models_with_regex(content, file_path)

        except Exception as e:
            print(f"⚠️  解析文件失败 {file_path}: {e}")

    def _find_function_end(self, content: str, start_pos: int) -> int:
        """查找函数结束位置"""
        pos = start_pos

        # 跳过冒号和空白
        while pos < len(content) and content[pos] not in "\n:":
            pos += 1

        if pos >= len(content):
            return pos

        if content[pos] == ":":
            pos += 1

        # 跳过换行符
        while pos < len(content) and content[pos] in "\n\t ":
            pos += 1

        # 查找函数体结束
        while pos < len(content):
            if content[pos] == "\n":
                # 检查下一行的缩进
                next_pos = pos + 1
                while next_pos < len(content) and content[next_pos] in "\t ":
                    next_pos += 1

                if next_pos < len(content) and content[next_pos] not in "\n\t ":
                    # 简单的缩进检查
                    if next_pos - (pos + 1) <= 4:
                        break

            pos += 1

        return min(pos, len(content))

    def _extract_return_model_from_content(self, content: str, decorator_pos: int) -> str:
        """从函数内容中提取返回模型"""
        # 查找 -> 类型标注
        end_content = content[decorator_pos : decorator_pos + 1000]
        return_match = re.search(r"->\s*([\w\[\],\s]+)\s*:", end_content)
        if return_match:
            return return_match.group(1).strip()
        return "dict"

    def _extract_data_fields_from_content(self, content: str, return_model: str) -> List[str]:
        """从函数内容中提取数据字段"""
        fields = []

        # 从返回语句中提取字典键
        return_pattern = r"return\s*\{([^}]+)\}"
        return_matches = re.findall(return_pattern, content, re.DOTALL)

        for match in return_matches:
            # 提取键名
            key_pattern = r'["\'](\w+)["\']'
            keys = re.findall(key_pattern, match)
            fields.extend(keys)

        return list(set(fields))

    def _extract_pydantic_models_with_regex(self, content: str, file_path: Path):
        """使用正则表达式提取Pydantic模型"""
        # 匹配类定义
        class_pattern = r"class\s+(\w+)\s*\(([^)]+)\):"
        class_matches = re.finditer(class_pattern, content)

        for match in class_matches:
            class_name = match.group(1)
            base_classes = match.group(2)

            # 检查是否继承自BaseModel
            if "BaseModel" in base_classes:
                # 提取类内容
                class_start = match.end()
                class_end = self._find_class_end(content, class_start)
                class_content = content[class_start:class_end]

                # 提取字段
                field_pattern = r"(\w+)\s*:\s*(?:\w+|Optional\[\w+\]|List\[\w+\])\s*(?:=\s*.+)?"
                fields = re.findall(field_pattern, class_content)

                # 过滤掉常见的非字段
                skip_fields = ["Config", "model_config", "__init__"]
                fields = [f for f in fields if f not in skip_fields]

                if fields:
                    self.pydantic_models[class_name] = fields

    def _find_class_end(self, content: str, start_pos: int) -> int:
        """查找类结束位置"""
        pos = start_pos

        # 跳过冒号和空白
        while pos < len(content) and content[pos] not in "\n:":
            pos += 1

        if pos >= len(content):
            return pos

        if content[pos] == ":":
            pos += 1

        # 查找类结束
        while pos < len(content):
            if content[pos] == "\n":
                # 检查下一行的缩进
                next_pos = pos + 1
                while next_pos < len(content) and content[next_pos] in "\t ":
                    next_pos += 1

                if next_pos < len(content) and content[next_pos] not in "\n\t ":
                    if next_pos - (pos + 1) <= 4:
                        break

            pos += 1

        return min(pos, len(content))

    def _extract_db_dependencies(self, content: str) -> List[str]:
        """提取数据库依赖"""
        db_tables = []

        # 查找常见的数据库操作模式
        patterns = [
            r'db\.query\(["\']([^"\']+)["\']\)',
            r'db\.select\(["\']([^"\']+)["\']\)',
            r'db\.table\(["\']([^"\']+)["\']\)',
            r"pd\.read_sql.*from\s+(\w+)",
            r"SELECT\s+.*FROM\s+(\w+)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            db_tables.extend(matches)

        return list(set(db_tables))

    def _determine_source_type(self, content: str) -> str:
        """判断数据源类型"""
        # 检查是否使用mock
        mock_keywords = ["mock", "Mock", "MOCK"]
        for keyword in mock_keywords:
            if keyword in content:
                return "mock"

        # 检查是否使用factory
        if "factory" in content.lower():
            return "factory"

        # 检查是否使用TDengine
        if "tdengine" in content.lower():
            return "tdengine"

        # 默认为PostgreSQL
        return "postgresql"


class FrontendAnalyzer:
    """分析前端页面和组件"""

    def __init__(self, frontend_dir: str):
        self.frontend_dir = Path(frontend_dir)
        self.pages: List[Dict] = []
        self.api_calls: List[Dict] = []
        self.file_hashes: Dict[str, str] = {}

    def analyze(self, incremental: bool = False) -> Tuple[List[Dict], List[Dict]]:
        """分析所有前端文件"""
        print("🔍 扫描前端页面...")

        if incremental:
            print("  模式: 增量分析")
            self._load_cache()

        vue_files = list(self.frontend_dir.rglob("*.vue"))
        ts_js_files = list(self.frontend_dir.rglob("*.ts")) + list(self.frontend_dir.rglob("*.js"))

        print(f"  找到 {len(vue_files)} 个Vue文件")
        print(f"  找到 {len(ts_js_files)} 个TS/JS文件")

        # 分析Vue页面
        for vue_file in vue_files:
            if incremental:
                current_hash = self._calculate_file_hash(vue_file)
                rel_path = str(vue_file.relative_to(self.frontend_dir))
                if rel_path in self.file_hashes and self.file_hashes[rel_path] == current_hash:
                    continue
                self.file_hashes[rel_path] = current_hash

            self._analyze_vue_file(vue_file)

        # 分析TS/JS文件（主要是API调用）
        for ts_file in ts_js_files:
            if "test" in ts_file.name or "spec" in ts_file.name:
                continue

            if incremental:
                current_hash = self._calculate_file_hash(ts_file)
                rel_path = str(ts_file.relative_to(self.frontend_dir))
                if rel_path in self.file_hashes and self.file_hashes[rel_path] == current_hash:
                    continue
                self.file_hashes[rel_path] = current_hash

            self._analyze_api_file(ts_file)

        if incremental:
            self._save_cache()

        print(f"✅ 分析了 {len(self.pages)} 个页面")
        print(f"✅ 找到 {len(self.api_calls)} 个API调用")
        return self.pages, self.api_calls

    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件hash用于增量分析"""
        try:
            with open(file_path, "rb") as f:
                return md5(f.read()).hexdigest()
        except:
            return ""

    def _load_cache(self):
        """加载增量分析缓存"""
        cache_file = self.frontend_dir / ".analysis_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    cache = json.load(f)
                    self.file_hashes = cache.get("file_hashes", {})
            except:
                pass

    def _save_cache(self):
        """保存增量分析缓存"""
        cache_file = self.frontend_dir / ".analysis_cache.json"
        try:
            with open(cache_file, "w") as f:
                json.dump({"file_hashes": self.file_hashes}, f)
        except:
            pass

    def _analyze_vue_file(self, file_path: Path):
        """分析Vue文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            rel_path = str(file_path.relative_to(self.frontend_dir))

            # 提取API调用
            api_calls = self._extract_vue_api_calls(content, rel_path)

            if api_calls:
                self.pages.append(
                    {
                        "path": rel_path,
                        "type": "view" if "/views/" in rel_path else "component",
                        "api_calls": api_calls,
                        "api_count": len(api_calls),
                    }
                )

                # 添加到总API调用列表
                self.api_calls.extend(api_calls)

        except Exception as e:
            print(f"⚠️  解析Vue文件失败 {file_path}: {e}")

    def _extract_vue_api_calls(self, content: str, file_path: str) -> List[Dict]:
        """从Vue文件中提取API调用"""
        api_calls = []

        # 模式1: HTTP调用（axios/request）
        http_patterns = [
            r'axios\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
            r'request\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
        ]

        for pattern in http_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                api_calls.append(
                    {
                        "source_file": file_path,
                        "type": "http",
                        "method": match.group(1).upper(),
                        "endpoint": match.group(2),
                        "line": content[: match.start()].count("\n") + 1,
                    }
                )

        # 模式2: API对象调用（dataApi.xxx, authApi.xxx等）
        api_object_pattern = r"(\w+Api)\.(\w+)\s*\("
        api_object_matches = re.finditer(api_object_pattern, content)

        for match in api_object_matches:
            api_calls.append(
                {
                    "source_file": file_path,
                    "type": "api_object",
                    "api_name": match.group(1),
                    "method": match.group(2),
                    "line": content[: match.start()].count("\n") + 1,
                }
            )

        return api_calls

    def _analyze_api_file(self, file_path: Path):
        """分析API调用文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            rel_path = str(file_path.relative_to(self.frontend_dir))

            # 提取API函数定义
            api_functions = self._extract_api_functions(content, rel_path)

            # 如果在api目录下，添加到API调用列表
            if "/api/" in rel_path:
                for func in api_functions:
                    self.api_calls.append(
                        {
                            "source_file": rel_path,
                            "type": "api_function",
                            "function_name": func["name"],
                            "endpoint": func.get("endpoint", ""),
                            "line": func["line"],
                        }
                    )

        except Exception as e:
            print(f"⚠️  解析API文件失败 {file_path}: {e}")

    def _extract_api_functions(self, content: str, file_path: str) -> List[Dict]:
        """提取API函数定义"""
        functions = []

        # 匹配函数定义
        pattern = r"(?:export\s+(?:async\s+)?(?:const|function)\s+(\w+)|const\s+(\w+)\s*=.*?(?:export\s+))\s*=\s*(?:async\s+)?\([^)]*\)\s*=>\s*\{"
        matches = re.finditer(pattern, content)

        for match in matches:
            func_name = match.group(1) or match.group(2)
            if func_name:
                # 提取函数体中的API调用
                func_start = match.end()
                func_content = self._extract_function_body(content, func_start)

                # 提取endpoint
                endpoint_match = re.search(r'["\']([^"\']+)["\']', func_content[:200])
                endpoint = endpoint_match.group(1) if endpoint_match else ""

                functions.append(
                    {
                        "name": func_name,
                        "endpoint": endpoint,
                        "line": content[: match.start()].count("\n") + 1,
                    }
                )

        return functions

    def _extract_function_body(self, content: str, start_pos: int) -> str:
        """提取函数体"""
        depth = 1
        pos = start_pos

        while pos < len(content) and depth > 0:
            if content[pos] == "{":
                depth += 1
            elif content[pos] == "}":
                depth -= 1
            pos += 1

        return content[start_pos:pos]


