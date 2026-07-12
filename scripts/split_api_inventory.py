#!/usr/bin/env python3
"""将api_data_inventory.json拆分成多个小文件，并创建索引"""

import json
from collections import defaultdict
from pathlib import Path


def split_api_inventory():
    """拆分API清单文件"""
    print("📁 拆分API数据清单文件...")

    # 读取原始文件
    with open("docs/reports/api_data_inventory.json", encoding="utf-8") as f:
        data = json.load(f)

    # 创建输出目录
    output_dir = Path("docs/reports/api_split")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 按路径前缀分组
    api_by_prefix = defaultdict(list)

    for endpoint in data["endpoints"]:
        path = endpoint["path"]
        # 路径前缀（如 /auth, /data, /dashboard）
        parts = path.split("/")
        if len(parts) > 1:
            prefix = f"/{parts[1]}"
        else:
            prefix = "/root"

        api_by_prefix[prefix].append(endpoint)

    # 为每个前缀创建单独的文件
    split_files = []

    for prefix, endpoints in sorted(api_by_prefix.items()):
        # 清理前缀作为文件名
        filename = prefix.replace("/", "_").replace("{", "").replace("}", "")
        filename = filename.removeprefix("_")

        # 创建子文件数据
        split_data = {
            "generated_at": data["generated_at"],
            "prefix": prefix,
            "total_endpoints": len(endpoints),
            "endpoints": endpoints,
        }

        # 保存文件
        output_file = output_dir / f"api_{filename}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(split_data, f, indent=2, ensure_ascii=False)

        split_files.append(
            {"prefix": prefix, "filename": f"api_{filename}.json", "count": len(endpoints), "file": output_file.name},
        )

        print(f"  ✅ 生成: {output_file.name} ({len(endpoints)} 个端点)")

    # 创建索引文件
    index_data = {
        "generated_at": data["generated_at"],
        "total_endpoints": data["total_endpoints"],
        "split_files": split_files,
        "summary": {
            "total_files": len(split_files),
            "endpoints_per_file_avg": data["total_endpoints"] // len(split_files) if split_files else 0,
            "files": [{"prefix": f["prefix"], "file": f["file"], "count": f["count"]} for f in split_files],
        },
    }

    index_file = output_dir / "api_index.json"
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)

    print(f"  ✅ 生成索引: {index_file.name}")

    # 创建Markdown索引文档
    create_markdown_index(index_data, output_dir)

    print("\n✅ 拆分完成！")
    print(f"   总文件数: {len(split_files) + 2}")
    print(f"   输出目录: {output_dir}")


def create_markdown_index(index_data: dict, output_dir: Path):
    """创建Markdown格式的索引文档"""
    with open(output_dir / "API_SPLIT_INDEX.md", "w", encoding="utf-8") as f:
        # 写入头部
        f.write("# API数据清单索引\n\n")
        f.write(f"**生成时间**: {index_data['generated_at']}\n\n")

        # 写入概览
        f.write("## 概览\n\n")
        f.write(f"- **总API端点数**: {index_data['total_endpoints']}\n")
        f.write(f"- **拆分文件数**: {index_data['summary']['total_files']}\n")
        f.write(f"- **平均每文件**: {index_data['summary']['endpoints_per_file_avg']} 个端点\n\n")

        # 写入文件列表
        f.write("## 拆分文件列表\n\n")
        f.write("| 路径前缀 | 文件名 | 端点数量 | 链接 |\n")
        f.write("|---------|--------|----------|------|\n")

        for file_info in index_data["split_files"]:
            # 计算占比
            percentage = file_info["count"] / index_data["total_endpoints"] * 100
            # 创建相对链接
            link = f"[{file_info['file']}]({file_info['file']})"
            f.write(
                f"| {file_info['prefix']} | {file_info['file']} | {file_info['count']} ({percentage:.1f}%) | {link} |\n",
            )

        # 写入使用说明
        f.write("\n## 使用说明\n\n")
        f.write("### 查找特定API\n\n")
        f.write("1. 根据API路径前缀（如 `/auth`, `/data`, `/dashboard`）找到对应文件\n")
        f.write("2. 点击链接打开对应的JSON文件\n")
        f.write("3. 在文件中查找具体的API端点\n\n")

        f.write("### 快速导航\n\n")
        f.write("```bash\n")
        f.write("# 查看所有文件\n")
        f.write(f"ls -lh {output_dir}/\n\n")
        f.write("# 查看特定文件\n")
        f.write(f"cat {output_dir}/api_auth.json\n\n")
        f.write("# 搜索特定API\n")
        f.write(f'grep -r "/login" {output_dir}/\n')
        f.write("```\n\n")

        f.write("### 文件说明\n\n")
        f.write("- **`api_index.json`**: 索引文件，包含所有拆分文件的元数据\n")
        f.write("- **`api_*.json`**: 按路径前缀拆分的API数据文件\n")
        f.write("- **`API_SPLIT_INDEX.md`**: 本文档，提供友好的索引界面\n\n")

        f.write("### 数据格式\n\n")
        f.write("每个拆分文件包含以下字段：\n\n")
        f.write("```json\n")
        f.write("{\n")
        f.write('  "generated_at": "2026-01-02T00:32:22.264253",\n')
        f.write('  "prefix": "/auth",\n')
        f.write('  "total_endpoints": 5,\n')
        f.write('  "endpoints": [\n')
        f.write("    {\n")
        f.write('      "path": "/login",\n')
        f.write('      "method": "POST",\n')
        f.write('      "file": "auth.py",\n')
        f.write('      "function": "login_for_access_token",\n')
        f.write('      "return_model": "dict",\n')
        f.write('      "data_fields": [],\n')
        f.write('      "db_dependencies": [],\n')
        f.write('      "source_type": "postgresql",\n')
        f.write('      "line_number": 172\n')
        f.write("    }\n")
        f.write("  ]\n")
        f.write("}\n")
        f.write("```\n\n")

        # 写入按文件分组的信息
        f.write("## 按API文件分组\n\n")
        endpoints_by_file = defaultdict(list)

        for file_info in index_data["split_files"]:
            # 读取拆分文件获取详细信息
            split_file = output_dir / file_info["file"]
            try:
                with open(split_file, encoding="utf-8") as sf:
                    split_data = json.load(sf)
                    for ep in split_data["endpoints"]:
                        endpoints_by_file[ep["file"]].append(ep)
            except:
                pass

        if endpoints_by_file:
            f.write("| 后端文件 | API端点数 | 路径示例 |\n")
            f.write("|---------|-----------|----------|\n")

            for filename, endpoints in sorted(endpoints_by_file.items()):
                examples = ", ".join([ep["path"] for ep in endpoints[:3]])
                if len(endpoints) > 3:
                    examples += f" ... (+{len(endpoints) - 3})"
                f.write(f"| {filename} | {len(endpoints)} | {examples} |\n")

    print("  ✅ 生成Markdown索引: API_SPLIT_INDEX.md")


if __name__ == "__main__":
    split_api_inventory()
