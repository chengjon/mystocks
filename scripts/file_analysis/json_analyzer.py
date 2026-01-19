#!/usr/bin/env python3
"""
JSON文件分析器
用途：分析JSON文件，提取键值对、嵌套结构、引用信息等
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class JSONAnalyzer:
    """JSON文件分析器"""

    def __init__(self):
        pass

    def analyze_file(self, file_path: str) -> Optional[Dict]:
        """
        分析JSON文件

        Args:
            file_path: 文件路径

        Returns:
            文件分析结果字典
        """
        logger.info(f"开始分析JSON文件: {file_path}")

        try:
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return None

            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # 解析JSON
            data = json.loads(content)

            # 获取文件信息
            file_stat = os.stat(file_path)
            file_name = os.path.basename(file_path)

            # 分析JSON结构
            keys = self._extract_keys(data)
            structure_type = self._determine_structure_type(data)
            depth = self._calculate_depth(data)
            array_count = self._count_arrays(data)
            object_count = self._count_objects(data)

            # 检查是否包含文件引用
            file_references = self._find_file_references(data)

            # 计算复杂度
            complexity_score = self._calculate_complexity(
                len(keys), depth, array_count, object_count
            )

            # 生成功能描述
            file_function = self._generate_function_description(
                file_name, structure_type, keys, depth
            )

            result = {
                'file_name': file_name,
                'file_path': file_path,
                'file_type': 'json',
                'file_size': file_stat.st_size,
                'line_count': len(content.split('\n')),
                'function_count': len(keys),
                'class_count': 0,
                'file_function': file_function,
                'module_name': None,
                'package_name': None,
                'imports_count': len(file_references),
                'exports_count': 0,
                'complexity_score': complexity_score,
                'quality_score': 0,
                'last_modified': self._format_timestamp(file_stat.st_mtime),
                'file_created': self._format_timestamp(file_stat.st_ctime),
                'error': None,
                'details': {
                    'keys': keys[:20],  # 只保留前20个键
                    'structure_type': structure_type,
                    'nesting_depth': depth,
                    'array_count': array_count,
                    'object_count': object_count,
                    'total_keys': len(keys),
                    'file_references': file_references[:10],  # 只保留前10个
                    'is_config_file': self._is_config_file(file_name, keys),
                    'is_data_file': self._is_data_file(file_name, keys),
                    'has_nested_arrays': depth > 1 and array_count > 0,
                    'has_nested_objects': depth > 1 and object_count > 0
                }
            }

            logger.info(f"JSON文件分析完成: {file_name}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {file_path} - {e}")
            return self._create_error_result(file_path, str(e))
        except Exception as e:
            logger.error(f"分析JSON文件失败: {file_path} - {e}")
            return self._create_error_result(file_path, str(e))

    def _extract_keys(self, data, prefix='') -> List[str]:
        """提取所有键"""
        keys = []

        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{prefix}.{key}" if prefix else key
                keys.append(full_key)
                keys.extend(self._extract_keys(value, full_key))

        elif isinstance(data, list):
            for i, item in enumerate(data):
                keys.extend(self._extract_keys(item, f"{prefix}[{i}]"))

        return keys

    def _determine_structure_type(self, data) -> str:
        """确定JSON结构类型"""
        if isinstance(data, dict):
            return 'object'
        elif isinstance(data, list):
            return 'array'
        elif isinstance(data, (str, int, float, bool)):
            return 'primitive'
        elif data is None:
            return 'null'
        else:
            return 'unknown'

    def _calculate_depth(self, data, current_depth=0) -> int:
        """计算嵌套深度"""
        if isinstance(data, dict):
            if not data:
                return current_depth
            return max(self._calculate_depth(v, current_depth + 1) for v in data.values())
        elif isinstance(data, list):
            if not data:
                return current_depth
            return max(self._calculate_depth(item, current_depth + 1) for item in data)
        else:
            return current_depth

    def _count_arrays(self, data) -> int:
        """计算数组数量"""
        count = 0
        if isinstance(data, list):
            count = 1
            for item in data:
                count += self._count_arrays(item)
        elif isinstance(data, dict):
            for value in data.values():
                count += self._count_arrays(value)
        return count

    def _count_objects(self, data) -> int:
        """计算对象数量"""
        count = 0
        if isinstance(data, dict):
            count = 1
            for value in data.values():
                count += self._count_objects(value)
        elif isinstance(data, list):
            for item in data:
                count += self._count_objects(item)
        return count

    def _find_file_references(self, data) -> List[str]:
        """查找文件引用"""
        references = []

        def search_in_value(value):
            if isinstance(value, str):
                # 检查文件路径模式
                if any(pattern in value for pattern in ['/', '\\', '.json', '.js', '.ts', '.py']):
                    references.append(value)
            elif isinstance(value, (dict, list)):
                if isinstance(value, dict):
                    for v in value.values():
                        search_in_value(v)
                elif isinstance(value, list):
                    for item in value:
                        search_in_value(item)

        search_in_value(data)
        return references

    def _calculate_complexity(
        self, key_count: int, depth: int,
        array_count: int, object_count: int
    ) -> int:
        """计算JSON复杂度"""
        complexity = 0

        # 键数量复杂度
        complexity += min(key_count / 5, 15)

        # 嵌套深度复杂度
        complexity += min(depth * 3, 15)

        # 数组复杂度
        complexity += min(array_count * 2, 10)

        # 对象复杂度
        complexity += min(object_count * 2, 10)

        return min(int(complexity), 30)

    def _generate_function_description(
        self, file_name: str, structure_type: str,
        keys: List[str], depth: int
    ) -> str:
        """生成功能描述"""
        parts = []

        if structure_type == 'object':
            parts.append(f"{len(keys)}个键")
        elif structure_type == 'array':
            parts.append("数组结构")
        else:
            parts.append(f"{structure_type}类型")

        if depth > 1:
            parts.append(f"{depth}层嵌套")

        return ', '.join(parts) if parts else 'JSON数据文件'

    def _is_config_file(self, file_name: str, keys: List[str]) -> bool:
        """判断是否为配置文件"""
        config_keywords = ['config', 'setting', 'option', 'parameter', 'env']
        return any(keyword in file_name.lower() for keyword in config_keywords)

    def _is_data_file(self, file_name: str, keys: List[str]) -> bool:
        """判断是否为数据文件"""
        data_keywords = ['data', 'list', 'items', 'records', 'entries']
        return any(keyword in file_name.lower() for keyword in data_keywords)

    def _create_error_result(self, file_path: str, error_msg: str) -> Dict:
        """创建错误结果"""
        return {
            'file_name': os.path.basename(file_path),
            'file_path': file_path,
            'file_type': 'json',
            'file_size': 0,
            'line_count': 0,
            'function_count': 0,
            'class_count': 0,
            'file_function': '',
            'module_name': None,
            'package_name': None,
            'imports_count': 0,
            'exports_count': 0,
            'complexity_score': 0,
            'quality_score': 0,
            'last_modified': None,
            'file_created': None,
            'error': error_msg,
            'details': {}
        }

    def _format_timestamp(self, timestamp: float) -> str:
        """格式化时间戳"""
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':
    # 测试代码
    import tempfile

    test_json = """
{
    "name": "MyStocks",
    "version": "1.0.0",
    "config": {
        "database": {
            "host": "localhost",
            "port": 5432
        },
        "features": ["monitoring", "trading", "analysis"]
    },
    "modules": [
        {"name": "core", "path": "/src/core"},
        {"name": "api", "path": "/src/api"}
    ]
}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(test_json)
        temp_path = f.name

    analyzer = JSONAnalyzer()
    result = analyzer.analyze_file(temp_path)

    print(f"文件名: {result['file_name']}")
    print(f"键数量: {result['function_count']}")
    print(f"结构类型: {result['details']['structure_type']}")
    print(f"嵌套深度: {result['details']['nesting_depth']}")
    print(f"复杂度: {result['complexity_score']}")
    print(f"功能: {result['file_function']}")

    os.unlink(temp_path)
