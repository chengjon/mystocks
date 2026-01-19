#!/usr/bin/env python3
"""
TypeScript/JavaScript文件分析器
用途：分析TypeScript和JavaScript源代码文件，提取元数据、函数、类、导入等信息
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class TypeScriptAnalyzer:
    """TypeScript/JavaScript文件分析器"""

    def __init__(self):
        # 导入语句正则表达式
        self.import_pattern = re.compile(
            r'^\s*import\s+(?:(?:\{([^}]+)\}\s+from\s+)?|(\*\s+as\s+\w+\s+from\s+)?|(\w+)\s+from\s+)?[\'"]([^\'"]+)[\'"]',
            re.MULTILINE
        )
        self.require_pattern = re.compile(
            r'^\s*(?:const|let|var)?\s*\w+\s*=\s*require\([\'"]([^\'"]+)[\'"]\)',
            re.MULTILINE
        )
        self.export_pattern = re.compile(
            r'^\s*export\s+(?:default\s+)?(?:const|let|var|function|class|interface|type)\s+(\w+)',
            re.MULTILINE
        )

        # 函数定义正则
        self.function_pattern = re.compile(
            r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*(?::\s*\w+)?\s*=\s*(?:async\s+)?\(?|\(\s*\w+\s*\)\s*(?::\s*\w+)?\s*=>)',
            re.MULTILINE
        )

        # 类定义正则
        self.class_pattern = re.compile(
            r'^\s*(?:export\s+)?(?:default\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?',
            re.MULTILINE
        )

        # 接口定义正则
        self.interface_pattern = re.compile(
            r'^\s*(?:export\s+)?interface\s+(\w+)(?:\s+extends\s+(\w+(?:\s*,\s*\w+)*))?',
            re.MULTILINE
        )

    def analyze_file(self, file_path: str) -> Dict:
        """
        分析TypeScript/JavaScript文件

        Args:
            file_path: 文件路径

        Returns:
            包含文件分析结果的字典
        """
        logger.info(f"开始分析TS/JS文件: {file_path}")

        try:
            # 确定文件类型
            file_ext = Path(file_path).suffix.lower()
            if file_ext in ['.ts', '.tsx']:
                file_type = 'typescript'
            elif file_ext in ['.js', '.jsx', '.mjs']:
                file_type = 'javascript'
            else:
                file_type = 'typescript'

            # 读取文件
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # 提取基本信息
            result = {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'file_type': file_type,
                'file_size': os.path.getsize(file_path),
                'line_count': len(content.splitlines()),
                'content': content,
                'module_name': self._extract_module_name(file_path),
                'package_name': self._extract_package_name(file_path),
                'functions': [],
                'classes': [],
                'interfaces': [],
                'imports': [],
                'exports': [],
                'last_modified': datetime.fromtimestamp(os.path.getmtime(file_path)),
                'file_created': datetime.fromtimestamp(os.path.getctime(file_path))
            }

            # 分析导入
            result['imports'] = self._extract_imports(content)

            # 分析导出
            result['exports'] = self._extract_exports(content)

            # 分析函数
            result['functions'] = self._extract_functions(content)

            # 分析类
            result['classes'] = self._extract_classes(content)

            # 分析接口（仅TypeScript）
            if file_type == 'typescript':
                result['interfaces'] = self._extract_interfaces(content)

            # 统计信息
            result['function_count'] = len(result['functions'])
            result['class_count'] = len(result['classes'])
            result['imports_count'] = len(result['imports'])
            result['exports_count'] = len(result['exports'])

            # 生成文件功能描述
            result['file_function'] = self._generate_function_description(result)

            # 计算复杂度
            result['complexity_score'] = self._calculate_complexity(result)

            logger.info(f"TS/JS文件分析完成: {file_path}")
            return result

        except Exception as e:
            logger.error(f"分析TS/JS文件失败: {file_path} - {e}")
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

    def _extract_imports(self, content: str) -> List[Dict]:
        """提取导入语句"""
        imports = []

        # ES6 import
        for match in self.import_pattern.finditer(content):
            named_imports = match.group(1)
            wildcard_import = match.group(2)
            default_import = match.group(3)
            module_path = match.group(4)

            import_info = {
                'module': module_path,
                'type': 'import',
                'line': content[:match.start()].count('\n') + 1
            }

            if named_imports:
                import_info['named_imports'] = [imp.strip() for imp in named_imports.split(',')]
            elif wildcard_import:
                import_info['wildcard_import'] = True
            elif default_import:
                import_info['default_import'] = default_import

            imports.append(import_info)

        # CommonJS require
        for match in self.require_pattern.finditer(content):
            imports.append({
                'module': match.group(1),
                'type': 'require',
                'line': content[:match.start()].count('\n') + 1
            })

        return imports

    def _extract_exports(self, content: str) -> List[Dict]:
        """提取导出语句"""
        exports = []

        for match in self.export_pattern.finditer(content):
            exports.append({
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            })

        # 检查export default
        if 'export default' in content:
            exports.append({
                'name': 'default',
                'type': 'default',
                'line': content.find('export default')
            })

        return exports

    def _extract_functions(self, content: str) -> List[Dict]:
        """提取函数定义"""
        functions = []

        for match in self.function_pattern.finditer(content):
            function_name = match.group(1) or match.group(2)
            if function_name:
                functions.append({
                    'name': function_name,
                    'line': content[:match.start()].count('\n') + 1
                })

        return functions

    def _extract_classes(self, content: str) -> List[Dict]:
        """提取类定义"""
        classes = []

        for match in self.class_pattern.finditer(content):
            class_info = {
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            }

            if match.group(2):
                class_info['extends'] = match.group(2)

            classes.append(class_info)

        return classes

    def _extract_interfaces(self, content: str) -> List[Dict]:
        """提取接口定义"""
        interfaces = []

        for match in self.interface_pattern.finditer(content):
            interface_info = {
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            }

            if match.group(2):
                interface_info['extends'] = [ext.strip() for ext in match.group(2).split(',')]

            interfaces.append(interface_info)

        return interfaces

    def _generate_function_description(self, result: Dict) -> str:
        """生成文件功能描述"""
        descriptions = []

        # 基于文件名
        file_name = result['file_name'].lower()
        if 'test' in file_name or 'spec' in file_name:
            descriptions.append("测试文件")
        elif 'component' in file_name:
            descriptions.append("组件")
        elif 'service' in file_name:
            descriptions.append("服务模块")
        elif 'store' in file_name or 'state' in file_name:
            descriptions.append("状态管理")
        elif 'router' in file_name:
            descriptions.append("路由配置")
        elif 'api' in file_name or 'client' in file_name:
            descriptions.append("API客户端")
        elif 'type' in file_name or 'interface' in file_name:
            descriptions.append("类型定义")
        elif 'util' in file_name or 'helper' in file_name:
            descriptions.append("工具模块")

        # 基于内容
        if result['function_count'] > 0:
            descriptions.append(f"{result['function_count']}个函数")
        if result['class_count'] > 0:
            descriptions.append(f"{result['class_count']}个类")
        if result.get('interface_count', 0) > 0:
            descriptions.append(f"{result['interface_count']}个接口")

        # 基于导入
        import_keywords = []
        for imp in result['imports']:
            module = imp.get('module', '').lower()
            if 'react' in module or 'vue' in module:
                import_keywords.append("前端框架")
            elif 'axios' in module or 'fetch' in module:
                import_keywords.append("HTTP客户端")
            elif 'pinia' in module or 'vuex' in module:
                import_keywords.append("状态管理")
            elif 'vue-router' in module:
                import_keywords.append("路由")

        if import_keywords:
            descriptions.append(f"使用{','.join(set(import_keywords))}")

        return "、".join(descriptions) if descriptions else f"{result['file_type']}源代码文件"

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

        return min(score, 30)

    def _create_error_result(self, file_path: str, error_msg: str) -> Dict:
        """创建错误结果"""
        return {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'file_type': 'unknown',
            'error': error_msg,
            'analyzed': False
        }


if __name__ == '__main__':
    # 测试代码
    analyzer = TypeScriptAnalyzer()

    # 创建一个测试文件
    test_content = """
import React from 'react';
import { useState } from 'react';

interface Props {
    name: string;
}

export const MyComponent: React.FC<Props> = ({ name }) => {
    const [count, setCount] = useState(0);

    const handleClick = () => {
        setCount(count + 1);
    };

    return <div onClick={handleClick}>{name}</div>;
};

export default MyComponent;
"""

    # 写入临时文件测试
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tsx', delete=False) as f:
        f.write(test_content)
        test_file = f.name

    try:
        result = analyzer.analyze_file(test_file)
        print(f"文件: {result['file_name']}")
        print(f"类型: {result['file_type']}")
        print(f"功能: {result['file_function']}")
        print(f"导入数: {result['imports_count']}")
        print(f"导出数: {result['exports_count']}")
        print(f"复杂度: {result['complexity_score']}")
    finally:
        os.unlink(test_file)
