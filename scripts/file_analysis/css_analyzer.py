#!/usr/bin/env python3
"""
CSS文件分析器
用途：分析CSS文件，提取选择器、规则、媒体查询等信息
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class CSSAnalyzer:
    """CSS文件分析器"""

    def __init__(self):
        self.patterns = {
            # CSS选择器模式
            'selector': re.compile(r'^([^\s{]+)\s*\{'),
            # CSS属性模式
            'property': re.compile(r'([a-zA-Z-]+)\s*:'),
            # @import规则
            'import': re.compile(r'@import\s+[\'"]([^\'"]+)[\'"]'),
            # @media规则
            'media': re.compile(r'@media\s+([^{]+)\{'),
            # @keyframes规则
            'keyframes': re.compile(r'@keyframes\s+(\w+)'),
            # URL引用
            'url': re.compile(r'url\([\'"]?([^\'"\)]+)[\'"]?\)'),
            # 注释
            'comment': re.compile(r'/\*.*?\*/', re.DOTALL)
        }

    def analyze_file(self, file_path: str) -> Optional[Dict]:
        """
        分析CSS文件

        Args:
            file_path: 文件路径

        Returns:
            文件分析结果字典
        """
        logger.info(f"开始分析CSS文件: {file_path}")

        try:
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return None

            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # 获取文件信息
            file_stat = os.stat(file_path)
            file_name = os.path.basename(file_path)

            # 移除注释
            content_clean = self.patterns['comment'].sub('', content)

            # 分析CSS规则
            selectors = self._extract_selectors(content_clean)
            properties = self._extract_properties(content_clean)
            imports = self._extract_imports(content_clean)
            media_queries = self._extract_media_queries(content_clean)
            keyframes = self._extract_keyframes(content_clean)
            url_references = self._extract_urls(content_clean)

            # 计算复杂度
            complexity_score = self._calculate_complexity(
                len(selectors), len(properties), len(media_queries), len(keyframes)
            )

            # 生成功能描述
            file_function = self._generate_function_description(
                file_name, selectors, media_queries, keyframes
            )

            result = {
                'file_name': file_name,
                'file_path': file_path,
                'file_type': 'css',
                'file_size': file_stat.st_size,
                'line_count': len(content.split('\n')),
                'function_count': len(selectors),
                'class_count': 0,
                'file_function': file_function,
                'module_name': None,
                'package_name': None,
                'imports_count': len(imports),
                'exports_count': 0,
                'complexity_score': complexity_score,
                'quality_score': 0,
                'last_modified': self._format_timestamp(file_stat.st_mtime),
                'file_created': self._format_timestamp(file_stat.st_ctime),
                'error': None,
                'details': {
                    'selectors': selectors[:10],  # 只保留前10个
                    'properties_count': len(properties),
                    'media_queries_count': len(media_queries),
                    'keyframes': keyframes,
                    'url_references': url_references[:10],  # 只保留前10个
                    'has_imports': len(imports) > 0,
                    'has_media_queries': len(media_queries) > 0,
                    'has_keyframes': len(keyframes) > 0,
                    'uses_flexbox': any('flex' in prop.lower() for prop in properties),
                    'uses_grid': any('grid' in prop.lower() for prop in properties),
                    'uses_animations': any('animation' in prop.lower() for prop in properties),
                    'uses_transitions': any('transition' in prop.lower() for prop in properties),
                    'uses_variables': any('--' in prop for prop in properties)
                }
            }

            logger.info(f"CSS文件分析完成: {file_name}")
            return result

        except Exception as e:
            logger.error(f"分析CSS文件失败: {file_path} - {e}")
            return {
                'file_name': os.path.basename(file_path),
                'file_path': file_path,
                'file_type': 'css',
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
                'error': str(e),
                'details': {}
            }

    def _extract_selectors(self, content: str) -> List[str]:
        """提取CSS选择器"""
        selectors = []
        for match in self.patterns['selector'].finditer(content):
            selector = match.group(1).strip()
            if selector and not selector.startswith('@'):
                selectors.append(selector)
        return selectors

    def _extract_properties(self, content: str) -> List[str]:
        """提取CSS属性"""
        properties = []
        for match in self.patterns['property'].finditer(content):
            properties.append(match.group(1))
        return properties

    def _extract_imports(self, content: str) -> List[str]:
        """提取@import规则"""
        imports = []
        for match in self.patterns['import'].finditer(content):
            imports.append(match.group(1))
        return imports

    def _extract_media_queries(self, content: str) -> List[str]:
        """提取@media规则"""
        media_queries = []
        for match in self.patterns['media'].finditer(content):
            media_queries.append(match.group(1).strip())
        return media_queries

    def _extract_keyframes(self, content: str) -> List[str]:
        """提取@keyframes规则"""
        keyframes = []
        for match in self.patterns['keyframes'].finditer(content):
            keyframes.append(match.group(1))
        return keyframes

    def _extract_urls(self, content: str) -> List[str]:
        """提取URL引用"""
        urls = []
        for match in self.patterns['url'].finditer(content):
            urls.append(match.group(1))
        return urls

    def _calculate_complexity(
        self, selector_count: int, property_count: int,
        media_count: int, keyframe_count: int
    ) -> int:
        """计算CSS复杂度"""
        complexity = 0

        # 选择器复杂度
        complexity += min(selector_count * 2, 20)

        # 属性复杂度
        complexity += min(property_count / 10, 10)

        # 媒体查询复杂度
        complexity += min(media_count * 3, 15)

        # 动画复杂度
        complexity += min(keyframe_count * 5, 20)

        return min(int(complexity), 30)

    def _generate_function_description(
        self, file_name: str, selectors: List[str],
        media_queries: List[str], keyframes: List[str]
    ) -> str:
        """生成功能描述"""
        parts = []

        if keyframes:
            parts.append(f"{len(keyframes)}个动画")

        if media_queries:
            parts.append(f"{len(media_queries)}个媒体查询")

        if selectors:
            parts.append(f"{len(selectors)}个选择器")

        return ', '.join(parts) if parts else 'CSS样式文件'

    def _format_timestamp(self, timestamp: float) -> str:
        """格式化时间戳"""
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':
    # 测试代码
    import tempfile

    test_css = """
/* 注释 */
.container {
    display: flex;
    justify-content: center;
}

@media (max-width: 768px) {
    .container {
        flex-direction: column;
    }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False) as f:
        f.write(test_css)
        temp_path = f.name

    analyzer = CSSAnalyzer()
    result = analyzer.analyze_file(temp_path)

    print(f"文件名: {result['file_name']}")
    print(f"选择器数: {result['function_count']}")
    print(f"复杂度: {result['complexity_score']}")
    print(f"功能: {result['file_function']}")

    os.unlink(temp_path)