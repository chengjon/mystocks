#!/usr/bin/env python3
"""
HTML to Vue Conversion Utility
用于将HTML页面转换为Vue组件的工具

Author: MyStocks Team
Date: 2026-01-16
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class HTMLAnalysis:
    """HTML文件分析结果"""

    file_path: str
    title: str
    sections: List[str]
    css_variables: Dict[str, str]
    javascript_functions: List[str]
    html_structure: Dict[str, any]


@dataclass
class VueConversionResult:
    """Vue转换结果"""

    template: str
    script: str
    style: str
    component_imports: List[str]
    data_mappings: Dict[str, str]


class HTMLToVueConverter:
    """HTML到Vue转换器"""

    def __init__(self):
        self.html_dir = Path("/opt/mydoc/design/example")
        self.vue_output_dir = Path("web/frontend/src/views/converted")

        # ArtDeco组件映射
        self.component_mappings = {
            "div.card": "ArtDecoCard",
            "button": "ArtDecoButton",
            "input": "ArtDecoInput",
            "select": "ArtDecoSelect",
            "table": "ArtDecoTable",
            "div.stats": "ArtDecoStatCard",
            "div.chart": "ArtDecoKLineChartContainer",
            "div.sidebar": "ArtDecoSidebar",
            "header": "ArtDecoHeader",
            "nav": "ArtDecoTopBar",
        }

        # CSS变量映射
        self.css_variable_mappings = {
            "--web3-background": "--bg-primary",
            "--web3-primary": "--gold",
            "--web3-font-heading": "--font-display",
            "--web3-font-body": "--font-body",
            "--bg-primary": "--bg-primary",
            "--gold": "--gold",
        }

    def analyze_html_file(self, file_path: Path) -> HTMLAnalysis:
        """分析HTML文件结构"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 提取标题
        title_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE)
        title = title_match.group(1) if title_match else "Untitled"

        # 提取章节
        sections = re.findall(r"<section[^>]*>.*?</section>", content, re.DOTALL | re.IGNORECASE)

        # 提取CSS变量
        css_vars = {}
        css_var_pattern = r"--([a-zA-Z0-9-]+):\s*([^;]+);"
        css_matches = re.findall(css_var_pattern, content)
        for var_name, var_value in css_matches:
            css_vars[f"--{var_name}"] = var_value.strip()

        # 提取JavaScript函数
        js_functions = re.findall(r"function\s+(\w+)\s*\([^)]*\)\s*{", content)

        # 分析HTML结构
        structure = self._analyze_html_structure(content)

        return HTMLAnalysis(
            file_path=str(file_path),
            title=title,
            sections=sections,
            css_variables=css_vars,
            javascript_functions=js_functions,
            html_structure=structure,
        )

    def _analyze_html_structure(self, content: str) -> Dict[str, any]:
        """分析HTML结构"""
        structure = {
            "has_navigation": bool(re.search(r"<nav[^>]*>.*?</nav>", content, re.DOTALL | re.IGNORECASE)),
            "has_sidebar": bool(re.search(r'class="[^"]*sidebar[^"]*"', content)),
            "has_charts": bool(re.search(r'class="[^"]*chart[^"]*"', content)),
            "has_tables": bool(re.search(r"<table[^>]*>.*?</table>", content, re.DOTALL | re.IGNORECASE)),
            "has_forms": bool(re.search(r"<form[^>]*>.*?</form>", content, re.DOTALL | re.IGNORECASE)),
            "has_modals": bool(re.search(r'class="[^"]*modal[^"]*"', content)),
            "animation_classes": re.findall(r'class="[^"]*animate[^"]*"', content),
            "data_attributes": re.findall(r'data-[a-zA-Z0-9-]+="[^"]*"', content),
        }
        return structure

    def convert_to_vue_component(self, analysis: HTMLAnalysis) -> VueConversionResult:
        """转换为Vue组件"""
        # 生成模板
        template = self._generate_vue_template(analysis)

        # 生成脚本
        script = self._generate_vue_script(analysis)

        # 生成样式
        style = self._generate_vue_style(analysis)

        # 组件导入
        component_imports = self._extract_component_imports(analysis)

        # 数据映射
        data_mappings = self._extract_data_mappings(analysis)

        return VueConversionResult(
            template=template,
            script=script,
            style=style,
            component_imports=component_imports,
            data_mappings=data_mappings,
        )

    def _generate_vue_template(self, analysis: HTMLAnalysis) -> str:
        """生成Vue模板"""
        template_parts = ["<template>", f'  <div class="{self._get_component_class_name(analysis)}">']

        # 添加ArtDeco头部
        if analysis.html_structure.get("has_navigation"):
            template_parts.append('    <ArtDecoHeader :title="pageTitle" />')

        # 添加侧边栏
        if analysis.html_structure.get("has_sidebar"):
            template_parts.append('    <ArtDecoSidebar :menu="menuItems" />')

        # 添加主要内容区域
        template_parts.append('    <div class="main-content">')

        # 转换章节
        for i, section in enumerate(analysis.sections[:5]):  # 限制前5个章节
            section_content = self._convert_html_section_to_vue(section, i)
            template_parts.append(f"      {section_content}")

        template_parts.extend(["    </div>", "  </div>", "</template>"])

        return "\n".join(template_parts)

    def _convert_html_section_to_vue(self, section_html: str, index: int) -> str:
        """将HTML章节转换为Vue组件"""
        # 简单的转换逻辑 - 可以扩展为更复杂的转换
        section_id = f"section-{index}"

        # 检查是否包含图表
        if "chart" in section_html.lower():
            return f'<ArtDecoCard title="数据可视化" class="{section_id}">\n        <div class="chart-placeholder">\n          <!-- Chart content will be rendered here -->\n        </div>\n      </ArtDecoCard>'
        elif "table" in section_html.lower():
            return f'<ArtDecoCard title="数据表格" class="{section_id}">\n        <ArtDecoTable :data="tableData" />\n      </ArtDecoCard>'
        else:
            return f'<ArtDecoCard title="内容区块 {index + 1}" class="{section_id}">\n        <!-- Converted content -->\n      </ArtDecoCard>'

    def _generate_vue_script(self, analysis: HTMLAnalysis) -> str:
        """生成Vue脚本"""
        component_name = self._get_component_class_name(analysis)

        script_parts = [
            '<script setup lang="ts">',
            "import { ref, onMounted } from 'vue'",
            "// ArtDeco component imports",
            "import { ArtDecoHeader, ArtDecoCard, ArtDecoTable } from '@/components/artdeco'",
            "",
            "// Component logic",
            f"const pageTitle = ref('{analysis.title}')",
            "const menuItems = ref([",
            "  // Menu items based on HTML navigation",
            "])",
            "",
            "// Reactive data",
            "const tableData = ref([])",
            "const chartData = ref({})",
            "",
            "// Methods",
            "const loadData = async () => {",
            "  // Convert HTML data loading logic to Vue",
            "}",
            "",
            "// Lifecycle",
            "onMounted(() => {",
            "  loadData()",
            "})",
            "</script>",
        ]

        return "\n".join(script_parts)

    def _generate_vue_style(self, analysis: HTMLAnalysis) -> str:
        """生成Vue样式"""
        style_parts = [
            '<style scoped lang="scss">',
            "@import '@/styles/artdeco-tokens.scss';",
            "",
            f".{self._get_component_class_name(analysis)} {{",
            "  @include artdeco-layout;",
            "  ",
            "  .main-content {",
            "    @include artdeco-content-spacing;",
            "  }",
            "  ",
            "  .chart-placeholder {",
            "    height: 300px;",
            "    background: linear-gradient(135deg, var(--bg-primary), var(--bg-secondary));",
            "    border-radius: 8px;",
            "    display: flex;",
            "    align-items: center;",
            "    justify-content: center;",
            "    color: var(--fg-muted);",
            "  }",
        ]

        # 添加ArtDeco装饰样式
        style_parts.extend(
            [
                "  ",
                "  // ArtDeco decorative elements",
                "  &::before {",
                '    content: "";',
                "    position: absolute;",
                "    top: 0;",
                "    left: 0;",
                "    right: 0;",
                "    height: 2px;",
                "    background: linear-gradient(90deg, transparent, var(--gold), transparent);",
                "  }",
                "}",
                "</style>",
            ]
        )

        return "\n".join(style_parts)

    def _extract_component_imports(self, analysis: HTMLAnalysis) -> List[str]:
        """提取需要的组件导入"""
        imports = ["ArtDecoCard"]

        if analysis.html_structure.get("has_navigation"):
            imports.append("ArtDecoHeader")
        if analysis.html_structure.get("has_sidebar"):
            imports.append("ArtDecoSidebar")
        if analysis.html_structure.get("has_tables"):
            imports.append("ArtDecoTable")
        if analysis.html_structure.get("has_charts"):
            imports.append("ArtDecoKLineChartContainer")

        return list(set(imports))

    def _extract_data_mappings(self, analysis: HTMLAnalysis) -> Dict[str, str]:
        """提取数据映射"""
        mappings = {}

        # 基于HTML结构推断数据映射
        if analysis.html_structure.get("has_tables"):
            mappings["tableData"] = "Array of table row objects"
        if analysis.html_structure.get("has_charts"):
            mappings["chartData"] = "Chart configuration object"

        return mappings

    def _get_component_class_name(self, analysis: HTMLAnalysis) -> str:
        """获取组件类名"""
        base_name = Path(analysis.file_path).stem
        return f"{base_name}-page"

    def save_vue_component(self, result: VueConversionResult, output_path: Path):
        """保存Vue组件文件"""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 创建.vue文件内容
        vue_content = f"{result.template}\n\n{result.script}\n\n{result.style}"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(vue_content)

        print(f"✅ Converted component saved to: {output_path}")

    def convert_file(self, html_file: Path, output_dir: Optional[Path] = None) -> Path:
        """转换单个HTML文件"""
        if output_dir is None:
            output_dir = self.vue_output_dir

        print(f"🔄 Analyzing {html_file}...")

        # 分析HTML
        analysis = self.analyze_html_file(html_file)

        # 转换到Vue
        result = self.convert_to_vue_component(analysis)

        # 保存结果
        output_file = output_dir / f"{html_file.stem}.vue"
        self.save_vue_component(result, output_file)

        return output_file

    def convert_all_files(self) -> List[Path]:
        """转换所有HTML文件"""
        converted_files = []

        for html_file in self.html_dir.glob("*.html"):
            try:
                output_file = self.convert_file(html_file)
                converted_files.append(output_file)
            except Exception as e:
                print(f"❌ Failed to convert {html_file}: {e}")

        return converted_files


def main():
    """主函数"""
    converter = HTMLToVueConverter()

    print("🎨 MyStocks HTML to Vue Converter")
    print("=" * 50)

    # 转换所有文件
    converted_files = converter.convert_all_files()

    print(f"\n✅ Conversion complete! {len(converted_files)} files converted.")
    print("📁 Converted files saved to: web/frontend/src/views/converted/")

    # 生成摘要报告
    summary = {
        "total_files": len(converted_files),
        "converted_files": [str(f) for f in converted_files],
        "conversion_date": "2026-01-16",
        "artdeco_components_used": [
            "ArtDecoCard",
            "ArtDecoHeader",
            "ArtDecoTable",
            "ArtDecoKLineChartContainer",
            "ArtDecoSidebar",
        ],
    }

    with open("conversion_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("📊 Conversion summary saved to: conversion_summary.json")


if __name__ == "__main__":
    main()
