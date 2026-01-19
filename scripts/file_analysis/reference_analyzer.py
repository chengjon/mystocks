#!/usr/bin/env python3
"""
引用关系分析器
用途：分析文件之间的引用关系，包括导入、导出、继承等
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import logging

logger = logging.getLogger(__name__)


class ReferenceAnalyzer:
    """引用关系分析器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.file_index = {}  # 文件路径到文件ID的映射
        self.module_index = {}  # 模块名到文件路径的映射

    def build_file_index(self, file_list: List[Dict]) -> None:
        """
        构建文件索引

        Args:
            file_list: 文件元数据列表
        """
        logger.info("开始构建文件索引")

        for file_info in file_list:
            file_path = file_info['file_path']
            file_id = file_info.get('id')

            if file_id:
                self.file_index[file_path] = file_id

                # 构建模块名索引
                module_name = file_info.get('module_name')
                if module_name:
                    self.module_index[module_name] = file_path

                package_name = file_info.get('package_name')
                if package_name and module_name:
                    self.module_index[f"{package_name}.{module_name}"] = file_path

        logger.info(f"文件索引构建完成，共{len(self.file_index)}个文件")

    def analyze_references(self, file_info: Dict) -> List[Dict]:
        """
        分析文件的引用关系

        Args:
            file_info: 文件元数据

        Returns:
            引用关系列表
        """
        logger.info(f"开始分析引用关系: {file_info['file_name']}")

        references = []

        try:
            file_type = file_info.get('file_type', 'unknown')

            if file_type == 'python':
                references = self._analyze_python_references(file_info)
            elif file_type in ['typescript', 'javascript']:
                references = self._analyze_ts_js_references(file_info)
            elif file_type in ['vue', 'html']:
                references = self._analyze_vue_html_references(file_info)

            logger.info(f"引用关系分析完成: {len(references)}个引用")
            return references

        except Exception as e:
            logger.error(f"分析引用关系失败: {e}")
            return []

    def _analyze_python_references(self, file_info: Dict) -> List[Dict]:
        """分析Python文件的引用"""
        references = []
        imports = file_info.get('imports', [])

        for imp in imports:
            module = imp.get('module', '')
            name = imp.get('name', '')
            line = imp.get('line', 0)

            # 解析引用路径
            target_path = self._resolve_python_reference(module, name, file_info['file_path'])

            if target_path:
                target_file_id = self.file_index.get(target_path)
                is_valid = target_file_id is not None

                references.append({
                    'source_file_id': file_info.get('id'),
                    'target_file_id': target_file_id,
                    'reference_type': imp.get('type', 'import'),
                    'reference_line': line,
                    'reference_code': f"import {module}",
                    'is_external': not is_valid,
                    'is_valid': is_valid,
                    'validation_message': 'Valid' if is_valid else 'External or not found'
                })

        return references

    def _analyze_ts_js_references(self, file_info: Dict) -> List[Dict]:
        """分析TypeScript/JavaScript文件的引用"""
        references = []
        imports = file_info.get('imports', [])

        for imp in imports:
            module = imp.get('module', '')
            line = imp.get('line', 0)

            # 解析引用路径
            target_path = self._resolve_ts_js_reference(module, file_info['file_path'])

            if target_path:
                target_file_id = self.file_index.get(target_path)
                is_valid = target_file_id is not None

                references.append({
                    'source_file_id': file_info.get('id'),
                    'target_file_id': target_file_id,
                    'reference_type': imp.get('type', 'import'),
                    'reference_line': line,
                    'reference_code': f"import from '{module}'",
                    'is_external': not is_valid,
                    'is_valid': is_valid,
                    'validation_message': 'Valid' if is_valid else 'External or not found'
                })

        return references

    def _analyze_vue_html_references(self, file_info: Dict) -> List[Dict]:
        """分析Vue/HTML文件的引用"""
        references = []

        # 分析组件引用
        components = file_info.get('components', [])
        for component in components:
            # 尝试解析组件路径
            target_path = self._resolve_component_reference(component, file_info['file_path'])

            if target_path:
                target_file_id = self.file_index.get(target_path)
                is_valid = target_file_id is not None

                references.append({
                    'source_file_id': file_info.get('id'),
                    'target_file_id': target_file_id,
                    'reference_type': 'component',
                    'reference_line': 0,
                    'reference_code': f"<{component}>",
                    'is_external': not is_valid,
                    'is_valid': is_valid,
                    'validation_message': 'Valid' if is_valid else 'External or not found'
                })

        # 如果有script部分，分析其中的导入
        script_content = file_info.get('script_content', '')
        if script_content:
            # 简单的import解析
            import_pattern = re.compile(r"import\s+(?:{[^}]+}\s+from\s+)?['\"]([^'\"]+)['\"]")
            for match in import_pattern.finditer(script_content):
                module = match.group(1)
                target_path = self._resolve_ts_js_reference(module, file_info['file_path'])

                if target_path:
                    target_file_id = self.file_index.get(target_path)
                    is_valid = target_file_id is not None

                    references.append({
                        'source_file_id': file_info.get('id'),
                        'target_file_id': target_file_id,
                        'reference_type': 'import',
                        'reference_line': script_content[:match.start()].count('\n') + 1,
                        'reference_code': match.group(0),
                        'is_external': not is_valid,
                        'is_valid': is_valid,
                        'validation_message': 'Valid' if is_valid else 'External or not found'
                    })

        return references

    def _resolve_python_reference(self, module: str, name: str, source_path: str) -> str:
        """解析Python引用路径"""
        if not module:
            return None

        # 检查是否为标准库或第三方库
        if module.startswith(('os.', 'sys.', 'json.', 'datetime.')):
            return None  # 标准库

        # 相对导入
        if module.startswith('.'):
            # 解析相对路径
            source_dir = Path(source_path).parent
            levels = module.count('.')
            target_dir = source_dir

            for _ in range(levels - 1):
                target_dir = target_dir.parent

            # 尝试不同的文件扩展名
            for ext in ['.py', '/__init__.py']:
                target_path = target_dir / (module.lstrip('.').replace('.', '/') + ext)
                if target_path.exists():
                    return str(target_path)

        # 绝对导入
        else:
            # 在项目中查找
            for root_dir in [self.project_root / 'src', self.project_root / 'scripts']:
                target_path = root_dir / (module.replace('.', '/') + '.py')
                if target_path.exists():
                    return str(target_path)

                # 检查__init__.py
                init_path = root_dir / (module.replace('.', '/') / '__init__.py')
                if init_path.exists():
                    return str(init_path)

        return None

    def _resolve_ts_js_reference(self, module: str, source_path: str) -> str:
        """解析TypeScript/JavaScript引用路径"""
        if not module:
            return None

        # 检查是否为外部库
        if module.startswith(('@', 'react', 'vue', 'axios', 'pinia', 'vue-router')):
            return None  # 外部库

        source_dir = Path(source_path).parent

        # 相对路径导入
        if module.startswith('./') or module.startswith('../'):
            target_path = (source_dir / module).resolve()

            # 尝试不同的文件扩展名
            for ext in ['.ts', '.tsx', '.js', '.jsx', '.vue']:
                test_path = target_path.with_suffix(ext)
                if test_path.exists():
                    return str(test_path)

            # 检查是否为目录（可能包含index文件）
            if target_path.is_dir():
                for index_file in ['index.ts', 'index.js', 'index.vue']:
                    test_path = target_path / index_file
                    if test_path.exists():
                        return str(test_path)

        # 绝对路径导入（基于项目根目录）
        else:
            for root_dir in [self.project_root / 'src', self.project_root / 'web/frontend/src']:
                target_path = root_dir / module

                # 尝试不同的文件扩展名
                for ext in ['.ts', '.tsx', '.js', '.jsx', '.vue']:
                    test_path = target_path.with_suffix(ext)
                    if test_path.exists():
                        return str(test_path)

                # 检查是否为目录
                if target_path.is_dir():
                    for index_file in ['index.ts', 'index.js', 'index.vue']:
                        test_path = target_path / index_file
                        if test_path.exists():
                            return str(test_path)

        return None

    def _resolve_component_reference(self, component: str, source_path: str) -> str:
        """解析Vue组件引用路径"""
        source_dir = Path(source_path).parent

        # 尝试在当前目录查找
        for ext in ['.vue', '.ts', '.tsx', '.js', '.jsx']:
            target_path = source_dir / f"{component}{ext}"
            if target_path.exists():
                return str(target_path)

        # 尝试在components目录查找
        components_dir = source_dir / 'components'
        if components_dir.exists():
            for ext in ['.vue', '.ts', '.tsx', '.js', '.jsx']:
                target_path = components_dir / f"{component}{ext}"
                if target_path.exists():
                    return str(target_path)

        # 尝试在src/components查找
        src_components = self.project_root / 'src' / 'components'
        if src_components.exists():
            for ext in ['.vue', '.ts', '.tsx', '.js', '.jsx']:
                target_path = src_components / f"{component}{ext}"
                if target_path.exists():
                    return str(target_path)

        return None

    def get_reverse_references(self, file_id: int, all_references: List[Dict]) -> List[Dict]:
        """
       获取反向引用（被哪些文件引用）

        Args:
            file_id: 文件ID
            all_references: 所有引用关系

        Returns:
            反向引用列表
        """
        return [ref for ref in all_references if ref.get('target_file_id') == file_id]

    def validate_references(self, references: List[Dict]) -> Tuple[int, int]:
        """
        验证引用关系

        Args:
            references: 引用关系列表

        Returns:
            (有效引用数, 无效引用数)
        """
        valid_count = sum(1 for ref in references if ref.get('is_valid', False))
        invalid_count = len(references) - valid_count

        return valid_count, invalid_count


if __name__ == '__main__':
    # 测试代码
    import tempfile

    # 创建测试文件
    test_files = [
        {
            'id': 1,
            'file_path': '/test/src/utils.ts',
            'file_name': 'utils.ts',
            'file_type': 'typescript',
            'module_name': 'utils',
            'imports': [
                {'module': './helper', 'type': 'import', 'line': 1}
            ]
        },
        {
            'id': 2,
            'file_path': '/test/src/helper.ts',
            'file_name': 'helper.ts',
            'file_type': 'typescript',
            'module_name': 'helper',
            'imports': []
        }
    ]

    analyzer = ReferenceAnalyzer('/test')
    analyzer.build_file_index(test_files)

    references = analyzer.analyze_references(test_files[0])
    print(f"发现 {len(references)} 个引用")

    for ref in references:
        print(f"  - {ref['reference_type']}: {ref['validation_message']}")