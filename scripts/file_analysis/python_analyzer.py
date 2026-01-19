#!/usr/bin/env python3
"""
Python文件分析器
用途：分析Python源代码文件，提取元数据、函数、类、导入等信息
"""

import os
import ast
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class PythonAnalyzer:
    """Python文件分析器"""

    def __init__(self):
        self.import_pattern = re.compile(r'^\s*(?:from\s+(\S+)\s+)?import\s+(.+)', re.MULTILINE)

    def analyze_file(self, file_path: str) -> Dict:
        """
        分析Python文件

        Args:
            file_path: Python文件路径

        Returns:
            包含文件分析结果的字典
        """
        logger.info(f"开始分析Python文件: {file_path}")

        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # 解析AST
            tree = ast.parse(content, filename=file_path)

            # 提取基本信息
            result = {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'file_type': 'python',
                'file_size': os.path.getsize(file_path),
                'line_count': len(content.splitlines()),
                'content': content,
                'module_name': self._extract_module_name(file_path),
                'package_name': self._extract_package_name(file_path),
                'functions': [],
                'classes': [],
                'imports': [],
                'exports': [],
                'docstring': ast.get_docstring(tree),
                'last_modified': datetime.fromtimestamp(os.path.getmtime(file_path)),
                'file_created': datetime.fromtimestamp(os.path.getctime(file_path))
            }

            # 分析AST节点
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    result['functions'].append(self._analyze_function(node))
                elif isinstance(node, ast.AsyncFunctionDef):
                    func_info = self._analyze_function(node)
                    func_info['is_async'] = True
                    result['functions'].append(func_info)
                elif isinstance(node, ast.ClassDef):
                    result['classes'].append(self._analyze_class(node))
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        result['imports'].append({
                            'module': alias.name,
                            'alias': alias.asname,
                            'type': 'import',
                            'line': node.lineno
                        })
                elif isinstance(node, ast.ImportFrom):
                    module = node.module if node.module else ''
                    for alias in node.names:
                        result['imports'].append({
                            'module': module,
                            'name': alias.name,
                            'alias': alias.asname,
                            'type': 'from_import',
                            'line': node.lineno
                        })

            # 统计信息
            result['function_count'] = len(result['functions'])
            result['class_count'] = len(result['classes'])
            result['imports_count'] = len(result['imports'])

            # 识别导出（__all__）
            result['exports'] = self._extract_exports(tree)
            result['exports_count'] = len(result['exports'])

            # 生成文件功能描述
            result['file_function'] = self._generate_function_description(result)

            # 计算复杂度
            result['complexity_score'] = self._calculate_complexity(result)

            logger.info(f"Python文件分析完成: {file_path}")
            return result

        except SyntaxError as e:
            logger.error(f"Python文件语法错误: {file_path} - {e}")
            return self._create_error_result(file_path, str(e))
        except Exception as e:
            logger.error(f"分析Python文件失败: {file_path} - {e}")
            return self._create_error_result(file_path, str(e))

    def _extract_module_name(self, file_path: str) -> str:
        """提取模块名"""
        return os.path.splitext(os.path.basename(file_path))[0]

    def _extract_package_name(self, file_path: str) -> Optional[str]:
        """提取包名"""
        parts = Path(file_path).parts
        if 'src' in parts:
            src_index = parts.index('src')
            if src_index + 1 < len(parts):
                return parts[src_index + 1]
        return None

    def _analyze_function(self, node: ast.FunctionDef) -> Dict:
        """分析函数"""
        return {
            'name': node.name,
            'lineno': node.lineno,
            'args': [arg.arg for arg in node.args.args],
            'decorators': [self._get_decorator_name(d) for d in node.decorator_list],
            'is_async': False,
            'docstring': ast.get_docstring(node),
            'returns': self._get_return_annotation(node)
        }

    def _analyze_class(self, node: ast.ClassDef) -> Dict:
        """分析类"""
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(item.name)

        return {
            'name': node.name,
            'lineno': node.lineno,
            'bases': [self._get_base_name(base) for base in node.bases],
            'decorators': [self._get_decorator_name(d) for d in node.decorator_list],
            'methods': methods,
            'docstring': ast.get_docstring(node)
        }

    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """获取装饰器名称"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{decorator.value.id}.{decorator.attr}"
        elif isinstance(decorator, ast.Call):
            return self._get_decorator_name(decorator.func)
        return str(decorator)

    def _get_base_name(self, base: ast.expr) -> str:
        """获取基类名称"""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return f"{base.value.id}.{base.attr}"
        return str(base)

    def _get_return_annotation(self, node: ast.FunctionDef) -> Optional[str]:
        """获取返回类型注解"""
        if node.returns:
            return ast.unparse(node.returns)
        return None

    def _extract_exports(self, tree: ast.AST) -> List[str]:
        """提取导出列表"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == '__all__':
                        if isinstance(node.value, ast.List):
                            return [elt.value for elt in node.value.elts
                                   if isinstance(elt, ast.Constant)]
        return []

    def _generate_function_description(self, result: Dict) -> str:
        """生成文件功能描述"""
        descriptions = []

        # 基于文件名
        file_name = result['file_name'].lower()
        if 'test' in file_name:
            descriptions.append("测试文件")
        elif 'mock' in file_name:
            descriptions.append("模拟数据文件")
        elif 'adapter' in file_name:
            descriptions.append("适配器")
        elif 'service' in file_name:
            descriptions.append("服务模块")
        elif 'model' in file_name:
            descriptions.append("数据模型")
        elif 'api' in file_name:
            descriptions.append("API接口")
        elif 'util' in file_name or 'helper' in file_name:
            descriptions.append("工具模块")

        # 基于内容
        if result['function_count'] > 0:
            descriptions.append(f"{result['function_count']}个函数")
        if result['class_count'] > 0:
            descriptions.append(f"{result['class_count']}个类")

        # 基于导入
        import_keywords = []
        for imp in result['imports']:
            if 'flask' in imp.get('module', '').lower() or 'fastapi' in imp.get('module', '').lower():
                import_keywords.append("Web框架")
            if 'sqlalchemy' in imp.get('module', '').lower() or 'psycopg2' in imp.get('module', '').lower():
                import_keywords.append("数据库")
            if 'pytest' in imp.get('module', '').lower():
                import_keywords.append("测试框架")

        if import_keywords:
            descriptions.append(f"使用{','.join(set(import_keywords))}")

        return "、".join(descriptions) if descriptions else "Python源代码文件"

    def _calculate_complexity(self, result: Dict) -> int:
        """计算复杂度评分"""
        score = 0

        # 基于行数
        score += min(result['line_count'] // 50, 10)

        # 基于函数数量
        score += min(result['function_count'] // 2, 10)

        # 基于类数量
        score += min(result['class_count'] * 2, 10)

        # 基于导入数量
        score += min(result['imports_count'] // 3, 5)

        return min(score, 30)  # 最大30分

    def _create_error_result(self, file_path: str, error_msg: str) -> Dict:
        """创建错误结果"""
        return {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'file_type': 'python',
            'error': error_msg,
            'analyzed': False
        }


if __name__ == '__main__':
    # 测试代码
    analyzer = PythonAnalyzer()
    test_file = __file__

    result = analyzer.analyze_file(test_file)
    print(f"文件: {result['file_name']}")
    print(f"功能: {result['file_function']}")
    print(f"函数数: {result['function_count']}")
    print(f"类数: {result['class_count']}")
    print(f"导入数: {result['imports_count']}")
    print(f"复杂度: {result['complexity_score']}")