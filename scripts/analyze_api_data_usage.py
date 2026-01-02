#!/usr/bin/env python3
"""
MyStocks API和Web前端数据使用分析工具（增强版）
支持增量分析、更准确的API调用提取和可视化报告
"""

import json
import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
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


class ReportGenerator:
    """生成分析报告"""

    def __init__(self, api_endpoints: List[Dict], frontend_pages: List[Dict], frontend_api_calls: List[Dict]):
        self.api_endpoints = api_endpoints
        self.frontend_pages = frontend_pages
        self.frontend_api_calls = frontend_api_calls

    def generate_json_reports(self, output_dir: Path):
        """生成JSON格式的清单"""
        output_dir.mkdir(parents=True, exist_ok=True)

        # API数据清单
        api_inventory = {
            "generated_at": datetime.now().isoformat(),
            "total_endpoints": len(self.api_endpoints),
            "endpoints": self.api_endpoints,
        }

        with open(output_dir / "api_data_inventory.json", "w", encoding="utf-8") as f:
            json.dump(api_inventory, f, indent=2, ensure_ascii=False)

        print(f"📄 生成 API数据清单: {output_dir / 'api_data_inventory.json'}")

        # Web API调用清单
        web_api_calls = {
            "generated_at": datetime.now().isoformat(),
            "total_pages": len(self.frontend_pages),
            "total_api_calls": len(self.frontend_api_calls),
            "pages": self.frontend_pages,
            "api_calls": self.frontend_api_calls,
        }

        with open(output_dir / "web_api_calls.json", "w", encoding="utf-8") as f:
            json.dump(web_api_calls, f, indent=2, ensure_ascii=False)

        print(f"📄 生成 Web API调用清单: {output_dir / 'web_api_calls.json'}")

    def generate_markdown_report(self, output_file: Path):
        """生成Markdown格式的详细报告"""
        print("📝 生成分析报告...")

        # 构建映射关系
        api_by_path = {ep["path"]: ep for ep in self.api_endpoints}
        api_usage_count = defaultdict(int)
        api_unused = set(api_by_path.keys())

        # 统计API使用情况（从HTTP调用和endpoint字段提取）
        for call in self.frontend_api_calls:
            endpoint = None
            if call["type"] == "http" and "endpoint" in call:
                endpoint = call["endpoint"]
            elif call["type"] == "api_function" and "endpoint" in call and call["endpoint"]:
                endpoint = call["endpoint"]

            if endpoint:
                # 尝试匹配API路径
                matched_path = self._match_api_path(endpoint, api_by_path.keys())
                if matched_path:
                    api_usage_count[matched_path] += 1
                    if matched_path in api_unused:
                        api_unused.remove(matched_path)

        # 查找前端请求但未实现的API
        frontend_requests = defaultdict(set)
        for call in self.frontend_api_calls:
            if call["type"] == "http" and "endpoint" in call:
                matched_path = self._match_api_path(call["endpoint"], api_by_path.keys())
                if matched_path and matched_path not in api_by_path:
                    frontend_requests[matched_path].add(call["source_file"])

        unimplemented = list(frontend_requests.keys())

        with open(output_file, "w", encoding="utf-8") as f:
            # 写入报告头部
            f.write("# API与Web前端数据使用分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # 写入概览
            self._write_overview(f, api_usage_count, unimplemented)

            # 写入API端点统计
            self._write_api_endpoints(f)

            # 写入页面API调用清单
            self._write_page_api_calls(f)

            # 写入数据使用分析
            self._write_data_usage_analysis(f, api_unused, unimplemented)

            # 写入数据库依赖分析
            self._write_database_analysis(f)

            # 写入数据源类型统计
            self._write_source_type_analysis(f)

            # 写入推荐改进
            self._write_recommendations(f)

        print(f"📄 生成分析报告: {output_file}")

    def _match_api_path(self, frontend_path: str, backend_paths: Set[str]) -> str:
        """尝试匹配前端路径到后端API"""
        # 直接匹配
        if frontend_path in backend_paths:
            return frontend_path

        # 去除前导/后的匹配
        normalized = frontend_path.lstrip("/")
        if normalized in backend_paths:
            return normalized

        # 模糊匹配（路径参数替换）
        frontend_parts = frontend_path.split("/")
        for backend_path in backend_paths:
            backend_parts = backend_path.split("/")
            if len(frontend_parts) == len(backend_parts):
                match = True
                for fp, bp in zip(frontend_parts, backend_parts):
                    if fp != bp and not (bp.startswith("{") and bp.endswith("}")):
                        match = False
                        break
                if match:
                    return backend_path

        return None

    def _write_overview(self, f, api_usage_count: Dict[str, int], unimplemented: List[str]):
        """写入概览"""
        f.write("## 概览\n\n")
        f.write(f"- **API端点总数**: {len(self.api_endpoints)}\n")
        f.write(f"- **前端页面总数**: {len(self.frontend_pages)}\n")
        f.write(f"- **API调用总数**: {len(self.frontend_api_calls)}\n")
        f.write(f"- **已使用的API**: {len(api_usage_count)}\n")
        f.write(f"- **未使用的API**: {len(self.api_endpoints) - len(api_usage_count)}\n")
        f.write(f"- **前端请求但未实现的API**: {len(unimplemented)}\n\n")

        # 添加可视化条形图
        f.write("### API使用情况可视化\n\n")
        total = len(self.api_endpoints)

        if total > 0:
            used = len(api_usage_count)
            unused = total - used

            f.write(f"```\n")
            f.write(f"已使用: {'█' * int(used / total * 50)} {used} ({used / total * 100:.1f}%)\n")
            f.write(f"未使用: {'░' * int(unused / total * 50)} {unused} ({unused / total * 100:.1f}%)\n")
            f.write(f"```\n\n")
        else:
            f.write("```\n")
            f.write("无API端点数据\n")
            f.write("```\n\n")

    def _write_api_endpoints(self, f):
        """写入API端点统计"""
        f.write("## API端点统计\n\n")
        f.write("### 按HTTP方法分类\n\n")
        f.write("| 方法 | 数量 | 占比 |\n")
        f.write("|------|------|------|\n")

        method_count = defaultdict(int)
        for ep in self.api_endpoints:
            method_count[ep["method"]] += 1

        total = len(self.api_endpoints)
        for method, count in sorted(method_count.items()):
            percentage = (count / total * 100) if total > 0 else 0
            f.write(f"| {method} | {count} | {percentage:.1f}% |\n")

        f.write("\n### API端点详情（按路径分组）\n\n")

        # 按路径分组
        api_by_prefix = defaultdict(list)
        for ep in self.api_endpoints:
            parts = ep["path"].split("/")
            if len(parts) > 1:
                prefix = f"/{parts[1]}"
            else:
                prefix = "其他"
            api_by_prefix[prefix].append(ep)

        for prefix, endpoints in sorted(api_by_prefix.items()):
            f.write(f"#### {prefix} ({len(endpoints)}个端点)\n\n")
            f.write("| 路径 | 方法 | 返回模型 | 数据源 | 文件:行号 |\n")
            f.write("|------|------|----------|--------|-----------|\n")

            for ep in endpoints:
                f.write(
                    f"| {ep['path']} | {ep['method']} | {ep['return_model']} | {ep['source_type']} | {ep['file']}:{ep['line_number']} |\n"
                )

            f.write("\n")

    def _write_page_api_calls(self, f):
        """写入页面API调用清单"""
        f.write("## 前端页面API调用清单\n\n")

        # 只显示有API调用的页面
        pages_with_calls = [p for p in self.frontend_pages if p["api_calls"]]

        # 按API调用数量排序
        pages_with_calls.sort(key=lambda x: x["api_count"], reverse=True)

        f.write(f"### Top 10 API调用最多的页面\n\n")
        f.write("| 页面 | 类型 | API调用数 |\n")
        f.write("|------|------|-----------|\n")
        for page in pages_with_calls[:10]:
            f.write(f"| {page['path']} | {page['type']} | {page['api_count']} |\n")

        f.write("\n### 详细API调用清单\n\n")

        for page in pages_with_calls:
            f.write(f"#### {page['path']}\n\n")
            f.write(f"**类型**: {page['type']}  \n")
            f.write(f"**API调用数**: {page['api_count']}  \n\n")

            # 按类型分组显示
            http_calls = [c for c in page["api_calls"] if c["type"] == "http"]
            api_object_calls = [c for c in page["api_calls"] if c["type"] == "api_object"]
            other_calls = [c for c in page["api_calls"] if c["type"] not in ["http", "api_object"]]

            if http_calls:
                f.write("##### HTTP调用\n\n")
                f.write("| 方法 | 端点 | 行号 |\n")
                f.write("|------|------|------|\n")
                for call in http_calls[:10]:  # 限制显示数量
                    f.write(f"| {call['method']} | {call['endpoint']} | {call['line']} |\n")
                if len(http_calls) > 10:
                    f.write(f"| ... | 还有 {len(http_calls) - 10} 个 | ... |\n")
                f.write("\n")

            if api_object_calls:
                f.write("##### API对象调用\n\n")
                f.write("| API对象 | 方法 | 行号 |\n")
                f.write("|---------|------|------|\n")
                for call in api_object_calls[:10]:
                    f.write(f"| {call['api_name']} | {call['method']} | {call['line']} |\n")
                if len(api_object_calls) > 10:
                    f.write(f"| ... | 还有 {len(api_object_calls) - 10} 个 | ... |\n")
                f.write("\n")

            if other_calls:
                f.write("##### 其他调用\n\n")
                f.write(f"共 {len(other_calls)} 个其他调用（类型: {[c['type'] for c in other_calls[:5]]}...）\n\n")

    def _write_data_usage_analysis(self, f, api_unused: Set[str], unimplemented: List[str]):
        """写入数据使用分析"""
        f.write("## 数据使用分析\n\n")

        # 未使用的API
        f.write("### API返回但前端未使用\n\n")
        if api_unused:
            f.write(f"共 {len(api_unused)} 个API端点未被前端使用：\n\n")
            f.write("| 路径 | 方法 | 返回模型 | 文件 |\n")
            f.write("|------|------|----------|------|\n")

            for path in sorted(api_unused)[:50]:  # 限制显示数量
                ep = next((e for e in self.api_endpoints if e["path"] == path), None)
                if ep:
                    f.write(f"| {ep['path']} | {ep['method']} | {ep['return_model']} | {ep['file']} |\n")

            if len(api_unused) > 50:
                f.write(f"| ... | ... | ... | ... (还有 {len(api_unused) - 50} 个) |\n")
        else:
            f.write("✅ 所有API端点都已被前端使用\n\n")

        f.write("\n### 前端请求但API未实现\n\n")
        if unimplemented:
            f.write(f"共 {len(unimplemented)} 个端点前端请求但后端未实现：\n\n")
            f.write("| 端点 | 请求页面数 |\n")
            f.write("|------|-----------|\n")

            for endpoint in sorted(unimplemented)[:20]:  # 限制显示数量
                pages = len(frontend_requests.get(endpoint, set()))
                f.write(f"| {endpoint} | {pages} |\n")

            if len(unimplemented) > 20:
                f.write(f"| ... | ... (还有 {len(unimplemented) - 20} 个) |\n")
        else:
            f.write("✅ 所有前端请求的API都已实现\n\n")

    def _write_database_analysis(self, f):
        """写入数据库依赖分析"""
        f.write("## 数据库依赖分析\n\n")

        # 统计数据库表使用
        db_tables = defaultdict(list)
        for ep in self.api_endpoints:
            for table in ep["db_dependencies"]:
                db_tables[table].append(ep["path"])

        if db_tables:
            f.write("### API使用的数据库表\n\n")
            f.write("| 表名 | 被API端点使用次数 | 端点示例 |\n")
            f.write("|------|------------------|----------|\n")

            for table, endpoints in sorted(db_tables.items(), key=lambda x: len(x[1]), reverse=True):
                f.write(f"| {table} | {len(endpoints)} | {', '.join(endpoints[:3])} |\n")
        else:
            f.write("ℹ️  未检测到明确的数据库表依赖\n\n")

    def _write_source_type_analysis(self, f):
        """写入数据源类型统计"""
        f.write("## 数据源类型统计\n\n")
        f.write("| 数据源类型 | API数量 | 占比 |\n")
        f.write("|-----------|---------|------|\n")

        source_count = defaultdict(int)
        for ep in self.api_endpoints:
            source_count[ep["source_type"]] += 1

        total = len(self.api_endpoints)
        for source_type, count in sorted(source_count.items()):
            percentage = (count / total * 100) if total > 0 else 0
            f.write(f"| {source_type} | {count} | {percentage:.1f}% |\n")

        f.write("\n### Mock数据API清单\n\n")
        mock_apis = [ep for ep in self.api_endpoints if ep["source_type"] == "mock"]
        if mock_apis:
            f.write("| 路径 | 方法 | 文件 |\n")
            f.write("|------|------|------|\n")
            for ep in mock_apis:
                f.write(f"| {ep['path']} | {ep['method']} | {ep['file']} |\n")
        else:
            f.write("✅ 没有使用Mock数据的API\n\n")

    def _write_recommendations(self, f):
        """写入推荐改进"""
        f.write("## 推荐改进\n\n")

        # 统计数据
        api_by_path = {ep["path"]: ep for ep in self.api_endpoints}
        api_usage_count = defaultdict(int)
        for call in self.frontend_api_calls:
            if call["type"] == "http" and "endpoint" in call:
                matched = self._match_api_path(call["endpoint"], api_by_path.keys())
                if matched:
                    api_usage_count[matched] += 1

        api_unused = set(api_by_path.keys()) - set(api_usage_count.keys())

        recommendations = []

        # 1. 清理未使用的API
        if len(api_unused) > 10:
            recommendations.append(
                {
                    "priority": "高",
                    "category": "代码清理",
                    "description": f"有 {len(api_unused)} 个API端点未被前端使用，建议评估是否需要删除或标记为deprecated",
                }
            )

        # 2. Mock数据替换
        mock_count = sum(1 for ep in self.api_endpoints if ep["source_type"] == "mock")
        if mock_count > 0:
            recommendations.append(
                {
                    "priority": "中",
                    "category": "数据源",
                    "description": f"有 {mock_count} 个API仍在使用Mock数据，建议替换为真实数据源",
                }
            )

        # 3. API调用优化
        if len(self.frontend_api_calls) > 2000:
            recommendations.append(
                {
                    "priority": "低",
                    "category": "性能优化",
                    "description": f"前端共 {len(self.frontend_api_calls)} 个API调用，建议分析是否有重复或冗余调用",
                }
            )

        if recommendations:
            f.write("| 优先级 | 类别 | 建议 |\n")
            f.write("|--------|------|------|\n")
            for rec in recommendations:
                f.write(f"| {rec['priority']} | {rec['category']} | {rec['description']} |\n")
        else:
            f.write("✅ 未发现明显改进点\n\n")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="MyStocks API与Web前端数据使用分析工具")
    parser.add_argument("--incremental", "-i", action="store_true", help="增量分析模式，只分析修改的文件")
    args = parser.parse_args()

    print("=" * 60)
    print("MyStocks API与Web前端数据使用分析工具")
    if args.incremental:
        print("模式: 增量分析")
    print("=" * 60)

    # 路径配置
    backend_dir = Path("web/backend/app/api")
    frontend_dir = Path("web/frontend/src")
    output_dir = Path("docs/reports")
    report_file = output_dir / "API_WEB_DATA_USAGE_REPORT.md"

    # 检查目录是否存在
    if not backend_dir.exists():
        print(f"❌ 后端API目录不存在: {backend_dir}")
        return

    if not frontend_dir.exists():
        print(f"❌ 前端目录不存在: {frontend_dir}")
        return

    # 分析API
    api_analyzer = APIAnalyzer(str(backend_dir))
    api_endpoints = api_analyzer.analyze(incremental=args.incremental)

    # 分析前端
    frontend_analyzer = FrontendAnalyzer(str(frontend_dir))
    frontend_pages, frontend_api_calls = frontend_analyzer.analyze(incremental=args.incremental)

    # 生成报告
    report_generator = ReportGenerator(api_endpoints, frontend_pages, frontend_api_calls)
    report_generator.generate_json_reports(output_dir)
    report_generator.generate_markdown_report(report_file)

    print("\n" + "=" * 60)
    print("✅ 分析完成！")
    print(f"   - API端点: {len(api_endpoints)}")
    print(f"   - 前端页面: {len(frontend_pages)}")
    print(f"   - API调用: {len(frontend_api_calls)}")
    print(f"\n   报告位置: {report_file}")
    print(f"   JSON清单: {output_dir / 'api_data_inventory.json'}")
    print(f"   JSON清单: {output_dir / 'web_api_calls.json'}")
    if args.incremental:
        print("\n💡 提示: 使用 --incremental 参数可以加速后续分析")
    print("=" * 60)


if __name__ == "__main__":
    main()
