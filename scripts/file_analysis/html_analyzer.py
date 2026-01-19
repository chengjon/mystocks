#!/usr/bin/env python3
"""
HTML/Vue文件分析器
用途：分析HTML和Vue单文件组件，提取模板、脚本、样式等信息
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class HTMLAnalyzer:
    """HTML/Vue文件分析器"""

    def __init__(self):
        # Vue SFC 块正则
        self.template_pattern = re.compile(r'<template[^>]*>(.*?)</template>', re.DOTALL)
        self.script_pattern = re.compile(r'<script[^>]*>(.*?)</script>', re.DOTALL)
        self.style_pattern = re.compile(r'<style[^>]*>(.*?)</style>', re.DOTALL)

        # 组件引用正则
        self.component_pattern = re.compile(r'<(?:component|el-|v-|@|:)[a-z-]+[^>]*>', re.IGNORECASE)

        # HTML标签正则
        self.html_tag_pattern = re.compile(r'<([a-z][a-z0-9]*)', re.IGNORECASE)

    def analyze_file(self, file_path: str) -> Dict:
        """
        分析HTML/Vue文件

        Args:
            file_path: 文件路径

        Returns:
            包含文件分析结果的字典
        """
        logger.info(f"开始分析HTML/Vue文件: {file_path}")

        try:
            # 确定文件类型
            file_ext = Path(file_path).suffix.lower()
            if file_ext == '.vue':
                file_type = 'vue'
            elif file_ext in ['.html', '.htm']:
                file_type = 'html'
            else:
                file_type = 'html'

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
                'last_modified': datetime.fromtimestamp(os.path.getmtime(file_path)),
                'file_created': datetime.fromtimestamp(os.path.getctime(file_path))
            }

            # Vue文件特殊处理
            if file_type == 'vue':
                result.update(self._analyze_vue_file(content))
            else:
                result.update(self._analyze_html_file(content))

            # 生成文件功能描述
            result['file_function'] = self._generate_function_description(result)

            # 计算复杂度
            result['complexity_score'] = self._calculate_complexity(result)

            logger.info(f"HTML/Vue文件分析完成: {file_path}")
            return result

        except Exception as e:
            logger.error(f"分析HTML/Vue文件失败: {file_path} - {e}")
            return self._create_error_result(file_path, str(e))

    def _analyze_vue_file(self, content: str) -> Dict:
        """分析Vue单文件组件"""
        result = {
            'has_template': False,
            'has_script': False,
            'has_style': False,
            'template_content': '',
            'script_content': '',
            'style_content': '',
            'components': [],
            'html_tags': []
        }

        # 提取template
        template_match = self.template_pattern.search(content)
        if template_match:
            result['has_template'] = True
            result['template_content'] = template_match.group(1)
            result['components'] = self._extract_components(result['template_content'])
            result['html_tags'] = self._extract_html_tags(result['template_content'])

        # 提取script
        script_match = self.script_pattern.search(content)
        if script_match:
            result['has_script'] = True
            result['script_content'] = script_match.group(1)

        # 提取style
        style_match = self.style_pattern.search(content)
        if style_match:
            result['has_style'] = True
            result['style_content'] = style_match.group(1)

        return result

    def _analyze_html_file(self, content: str) -> Dict:
        """分析HTML文件"""
        return {
            'has_template': True,
            'has_script': False,
            'has_style': False,
            'template_content': content,
            'script_content': '',
            'style_content': '',
            'components': [],
            'html_tags': self._extract_html_tags(content)
        }

    def _extract_module_name(self, file_path: str) -> str:
        """提取模块名"""
        return os.path.splitext(os.path.basename(file_path))[0]

    def _extract_components(self, template_content: str) -> List[str]:
        """提取组件引用"""
        components = set()

        # 提取自定义组件（通常以大写字母开头）
        for match in re.finditer(r'<([A-Z][a-zA-Z0-9]*)', template_content):
            component_name = match.group(1)
            if component_name not in ['Template', 'Script', 'Style']:
                components.add(component_name)

        # 提取Element Plus组件
        for match in re.finditer(r'<el-([a-z-]+)', template_content):
            components.add(f"el-{match.group(1)}")

        return sorted(list(components))

    def _extract_html_tags(self, content: str) -> List[str]:
        """提取HTML标签"""
        tags = set()

        for match in self.html_tag_pattern.finditer(content):
            tag = match.group(1).lower()
            if tag and not tag.startswith('!'):
                tags.add(tag)

        return sorted(list(tags))

    def _generate_function_description(self, result: Dict) -> str:
        """生成文件功能描述"""
        descriptions = []

        # 基于文件类型
        if result['file_type'] == 'vue':
            descriptions.append("Vue组件")

            # 检查Vue组件结构
            parts = []
            if result.get('has_template'):
                parts.append("模板")
            if result.get('has_script'):
                parts.append("脚本")
            if result.get('has_style'):
                parts.append("样式")

            if parts:
                descriptions.append(f"包含{'+'.join(parts)}")

            # 基于组件数量
            component_count = len(result.get('components', []))
            if component_count > 0:
                descriptions.append(f"{component_count}个子组件")

        else:
            descriptions.append("HTML页面")

            # 基于HTML标签
            html_tags = result.get('html_tags', [])
            if 'form' in html_tags:
                descriptions.append("表单页面")
            elif 'table' in html_tags:
                descriptions.append("表格页面")
            elif 'canvas' in html_tags or 'svg' in html_tags:
                descriptions.append("图形页面")

        # 基于文件名
        file_name = result['file_name'].lower()
        if 'dashboard' in file_name:
            descriptions.append("仪表盘")
        elif 'login' in file_name:
            descriptions.append("登录页面")
        elif 'home' in file_name or 'index' in file_name:
            descriptions.append("首页")
        elif 'detail' in file_name:
            descriptions.append("详情页")
        elif 'list' in file_name:
            descriptions.append("列表页")

        return "、".join(descriptions) if descriptions else f"{result['file_type']}文件"

    def _calculate_complexity(self, result: Dict) -> int:
        """计算复杂度评分"""
        score = 0

        # 基于行数
        score += min(result['line_count'] // 50, 10)

        # 基于组件数量
        component_count = len(result.get('components', []))
        score += min(component_count * 2, 10)

        # 基于HTML标签数量
        html_tags = result.get('html_tags', [])
        score += min(len(html_tags) // 5, 10)

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
    analyzer = HTMLAnalyzer()

    # 创建一个测试Vue文件
    test_content = """
<template>
  <div class="dashboard">
    <el-card>
      <h2>{{ title }}</h2>
      <el-button @click="handleClick">点击</el-button>
    </el-card>
    <MyComponent :data="items" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import MyComponent from './MyComponent.vue';

const title = ref('Dashboard');
const items = ref([]);

const handleClick = () => {
  console.log('Clicked');
};
</script>

<style scoped>
.dashboard {
  padding: 20px;
}
</style>
"""

    # 写入临时文件测试
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.vue', delete=False) as f:
        f.write(test_content)
        test_file = f.name

    try:
        result = analyzer.analyze_file(test_file)
        print(f"文件: {result['file_name']}")
        print(f"类型: {result['file_type']}")
        print(f"功能: {result['file_function']}")
        print(f"组件数: {len(result['components'])}")
        print(f"HTML标签数: {len(result['html_tags'])}")
        print(f"复杂度: {result['complexity_score']}")
    finally:
        os.unlink(test_file)