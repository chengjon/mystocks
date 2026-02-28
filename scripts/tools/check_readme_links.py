#!/usr/bin/env python3
"""检查 README.md 中的所有本地 Markdown 链接是否有效

使用方法:
    python3 scripts/tools/check_readme_links.py

退出码:
    0 - 所有链接有效
    1 - 存在失效链接或文件读取失败
"""

import re
import sys
from pathlib import Path


def check_readme_links():
    """检查 README.md 中的本地链接"""
    readme_path = Path('README.md')

    if not readme_path.exists():
        print(f"❌ README.md 不存在: {readme_path}")
        return False

    try:
        content = readme_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"❌ 读取 README.md 失败: {e}")
        return False

    # 提取所有 Markdown 链接: [text](url)
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    links = re.findall(link_pattern, content)

    print(f"找到 {len(links)} 个链接\n")

    broken_links = []
    valid_links = []
    external_links = []
    anchor_links = []

    for text, url in links:
        # 跳过外部链接和锚点
        if url.startswith('http://') or url.startswith('https://'):
            external_links.append((text, url))
            continue

        if url.startswith('#'):
            anchor_links.append((text, url))
            continue

        # 检查本地文件是否存在
        file_path = Path(url)
        exists = file_path.exists()

        if exists:
            valid_links.append((text, url))
            print(f"✅ [{text}]({url})")
        else:
            broken_links.append((text, url))
            print(f"❌ [{text}]({url})")

    print(f"\n=== 摘要 ===")
    print(f"本地有效链接: {len(valid_links)}")
    print(f"本地失效链接: {len(broken_links)}")
    print(f"外部链接: {len(external_links)} (未检查)")
    print(f"锚点链接: {len(anchor_links)} (未检查)")

    if broken_links:
        print(f"\n失效链接列表:")
        for text, url in broken_links:
            print(f"  - [{text}]({url})")
        return False

    return True


if __name__ == '__main__':
    try:
        success = check_readme_links()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n检查被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 检查过程出错: {e}")
        sys.exit(1)
