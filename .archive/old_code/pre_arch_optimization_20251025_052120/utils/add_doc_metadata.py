#!/usr/bin/env python3
"""
批量为MD文档添加元数据标记

用法:
    python utils/add_doc_metadata.py --doc README.md --creator "JohnC & Claude" --version "2.1.0"
"""

import argparse
import os
from datetime import datetime


METADATA_TEMPLATE = """**创建人**: {creator}
**版本**: {version}
**批准日期**: {approved_date}
**最后修订**: {last_modified}
**本次修订内容**: {revision_notes}

---

"""


def add_metadata(file_path: str, creator: str, version: str,
                 approved_date: str = None, revision_notes: str = "添加文档元数据标记"):
    """
    为MD文档添加元数据

    Args:
        file_path: 文档路径
        creator: 创建人
        version: 版本号
        approved_date: 批准日期 (可选，默认今天)
        revision_notes: 修订内容描述
    """
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False

    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否已有元数据
    if "**创建人**:" in content:
        print(f"⚠️  {file_path} 已包含元数据，跳过")
        return False

    # 准备元数据
    today = datetime.now().strftime("%Y-%m-%d")
    approved = approved_date if approved_date else today

    metadata = METADATA_TEMPLATE.format(
        creator=creator,
        version=version,
        approved_date=approved,
        last_modified=today,
        revision_notes=revision_notes
    )

    # 找到第一个#标题后插入
    lines = content.split('\n')
    insert_index = 0

    for i, line in enumerate(lines):
        if line.strip().startswith('#'):
            insert_index = i + 1
            break

    # 插入元数据
    lines.insert(insert_index, "")
    lines.insert(insert_index + 1, metadata.strip())

    # 写回文件
    new_content = '\n'.join(lines)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ {file_path} 元数据添加成功")
    return True


def batch_add_metadata():
    """批量为核心文档添加元数据"""

    # 核心文档清单 (来自Phase 0 R2)
    docs = [
        # 根目录文档
        ("README.md", "JohnC & Claude", "2.1.0", "2025-10-15", "系统架构和使用说明"),
        ("CHANGELOG_v2.1.md", "Claude", "2.1.0", "2025-10-15", "v2.1版本更新日志"),
        ("QUICKSTART.md", "Claude", "2.1.0", "2025-10-15", "快速开始指南和开发规范"),
        ("DELIVERY_v2.1.md", "Claude", "2.1.0", "2025-10-15", "v2.1交付文档"),

        # 适配器文档
        ("adapters/README.md", "JohnC & Claude", "2.0.0", "2025-08-01", "数据源适配器说明"),
        ("adapters/README_TDX.md", "Claude", "2.1.0", "2025-10-15", "通达信TDX集成说明"),

        # Web系统文档
        ("web/PORTS.md", "Claude", "2.1.0", "2025-10-15", "端口配置说明"),
        ("web/TDX_SETUP_COMPLETE.md", "Claude", "2.1.0", "2025-10-15", "TDX设置完成文档"),

        # 监控系统文档
        ("monitoring/grafana_setup.md", "Claude", "2.0.0", "2025-09-01", "Grafana监控设置"),
        ("monitoring/MANUAL_SETUP_GUIDE.md", "Claude", "2.0.0", "2025-09-01", "手动设置指南"),
        ("monitoring/生成监控数据说明.md", "Claude", "2.0.0", "2025-09-01", "监控数据生成说明"),

        # 功能规格文档
        ("specs/005-tdx-web-tdx/spec.md", "Claude & Spec-Kit", "1.0.0", "2025-10-15", "TDX功能规格"),
        ("specs/005-tdx-web-tdx/README.md", "Claude", "1.0.0", "2025-10-15", "TDX功能README"),
    ]

    print("\n" + "="*80)
    print("批量添加文档元数据")
    print("="*80 + "\n")

    added = 0
    skipped = 0
    failed = 0

    for doc, creator, version, approved, notes in docs:
        file_path = os.path.join("/opt/claude/mystocks_spec", doc)

        try:
            result = add_metadata(file_path, creator, version, approved, notes)
            if result:
                added += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"❌ {doc} 处理失败: {str(e)}")
            failed += 1

    print("\n" + "="*80)
    print(f"完成统计: 添加 {added}, 跳过 {skipped}, 失败 {failed}")
    print("="*80)


def main():
    parser = argparse.ArgumentParser(description="为MD文档添加元数据")
    parser.add_argument("--doc", help="单个文档路径")
    parser.add_argument("--creator", default="Claude", help="创建人")
    parser.add_argument("--version", default="1.0.0", help="版本号")
    parser.add_argument("--batch", action="store_true", help="批量处理核心文档")

    args = parser.parse_args()

    if args.batch:
        batch_add_metadata()
    elif args.doc:
        add_metadata(args.doc, args.creator, args.version)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
