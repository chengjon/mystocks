#!/usr/bin/env python3
"""批量生成带区域分组的元素标注 HTML。
读取 MD 中的 ### 子标题作为区域，同一区域内的元素放在一个分组容器中。
"""

import re
from pathlib import Path
from collections import OrderedDict

ROOT = Path("/opt/claude/mystocks_spec")
MD_PATH = ROOT / "docs/references/PAGE_ELEMENT_INDEX.md"
OUT_DIR = ROOT / "web/frontend/public"

TYPE_COLORS = {
    "Header": "#3742fa", "Status": "#ff6b81", "Badge": "#ff6b81",
    "Stat": "#2ed573", "Chart": "#ffa502", "Card": "#1e90ff",
    "Button": "#a55eea", "Collapse": "#747d8c", "Gauge": "#ff6348",
    "Label": "#7bed9f", "Link": "#70a1ff", "Tab": "#eccc68",
    "List": "#5352ed", "Table": "#2ed573", "Filter": "#ffa502",
    "Form": "#a55eea", "Pagination": "#747d8c", "Alert": "#ff4757",
    "SubPage": "#747d8c", "Image": "#70a1ff", "Text": "#636e72",
    "Info": "#7bed9f", "Dialog": "#ffa502", "Overlay": "#ff4757",
    "Footer": "#636e72", "Panel": "#1e90ff", "Progress": "#2ed573",
}


def parse_md_sections() -> list[dict]:
    """解析 MD，按 ### 子标题分组"""
    text = MD_PATH.read_text(encoding="utf-8")
    pages = []
    current_page_id = None
    current_page_title = ""
    sections = []  # [(section_title, [rows])]
    current_section = "默认"
    current_rows = []
    in_a1 = False

    for line in text.split("\n"):
        # 跳过 A1 的子区域（手动写的布局标注图保留）
        if line.startswith("## 二、A1"):
            in_a1 = True
            continue
        if in_a1 and line.startswith("## 三、"):
            in_a1 = False

        # 页面标识行: ### B1 实时行情
        m = re.match(r"^###\s+(\w+)\s+(.+)$", line)
        if m and not in_a1:
            # 保存上一个页面的数据
            if current_section and current_rows:
                sections.append((current_section, current_rows))
            if current_page_id and sections:
                pages.append({"id": current_page_id, "title": current_page_title, "sections": sections})

            current_page_id = m.group(1)
            current_page_title = m.group(2).strip()
            sections = []
            current_section = "默认"
            current_rows = []
            continue

        # 子区域标题: ### 2.3 市场资金流向概览卡片
        if not in_a1 and current_page_id:
            m_sub = re.match(r"^###\s+([\d.]+)\s+(.+)$", line)
            if m_sub:
                if current_rows:
                    sections.append((current_section, current_rows))
                current_section = m_sub.group(2).strip()
                current_rows = []
                continue

        # 表格行
        if line.startswith("| ") and not line.startswith("| 编号") and not line.startswith("|------"):
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 3 and re.match(r"^[A-Z]\d+-\d+$", parts[0]):
                current_rows.append({
                    "id": parts[0],
                    "type": parts[1] if len(parts) > 1 else "",
                    "name": parts[2] if len(parts) > 2 else "",
                })

    # 最后一个页面
    if current_section and current_rows:
        sections.append((current_section, current_rows))
    if current_page_id and sections:
        pages.append({"id": current_page_id, "title": current_page_title, "sections": sections})

    return pages


def guess_section_style(title: str) -> str:
    """根据区域标题猜测布局风格"""
    t = title.lower()
    if any(k in t for k in ["头部", "header", "标题"]):
        return "header"
    if any(k in t for k in ["元数据", "meta"]):
        return "meta"
    if any(k in t for k in ["折叠", "collapse"]):
        return "collapse"
    if any(k in t for k in ["卡片", "网格", "card", "概览", "指标", "面板"]):
        return "cards"
    if any(k in t for k in ["表格", "列表", "table", "排名", "记录"]):
        return "table"
    if any(k in t for k in ["表单", "输入", "form", "配置"]):
        return "form"
    if any(k in t for k in ["导航", "链接", "link"]):
        return "nav"
    return "cards"  # 默认卡片布局


def build_section_html(section_title: str, rows: list) -> str:
    """生成单个区域的 HTML"""
    style = guess_section_style(section_title)
    items = ""

    if style == "header":
        for r in rows:
            color = TYPE_COLORS.get(r["type"], "#ff4757")
            items += f'<span class="hdr-item"><span class="badge" style="background:{color};">{r["id"]}</span> {r["name"]}</span>\n'
        return f"""<div class="sec sec-header">
<div class="sec-title">{section_title}</div>
<div class="sec-body header-row">{items}</div>
</div>"""

    elif style == "meta":
        for r in rows:
            color = TYPE_COLORS.get(r["type"], "#ff4757")
            items += f'<span class="meta-item"><span class="badge" style="background:{color};">{r["id"]}</span> {r["name"]}</span>\n'
        return f"""<div class="sec sec-meta">
<div class="sec-body meta-row">{items}</div>
</div>"""

    elif style == "collapse":
        for r in rows:
            color = TYPE_COLORS.get(r["type"], "#ff4757")
            items += f'<div class="collapse-item"><span class="badge" style="background:{color};">{r["id"]}</span> <span class="ci-type">[{r["type"]}]</span> {r["name"]}</div>\n'
        return f"""<div class="sec sec-collapse">
<details open><summary class="sec-title collapse-summary">▼ {section_title}</summary>
<div class="sec-body">{items}</div>
</details>
</div>"""

    elif style == "table":
        # 生成迷你表头
        for r in rows:
            color = TYPE_COLORS.get(r["type"], "#ff4757")
            items += f'<div class="trow"><span class="badge" style="background:{color};">{r["id"]}</span> <span class="tcell-type">[{r["type"]}]</span> <span class="tcell-name">{r["name"]}</span></div>\n'
        return f"""<div class="sec sec-table">
<div class="sec-title">{section_title}</div>
<div class="sec-body table-body">{items}</div>
</div>"""

    elif style == "nav":
        for r in rows:
            color = TYPE_COLORS.get(r["type"], "#ff4757")
            items += f'<div class="nav-item"><span class="badge" style="background:{color};">{r["id"]}</span> {r["name"]}</div>\n'
        return f"""<div class="sec sec-nav">
<div class="sec-title">{section_title}</div>
<div class="sec-body nav-grid">{items}</div>
</div>"""

    else:  # cards — 默认网格
        for r in rows:
            color = TYPE_COLORS.get(r["type"], "#ff4757")
            items += f"""<div class="el" style="border-left:3px solid {color};">
<span class="badge" style="background:{color};">{r["id"]}</span>
<span class="el-type">[{r["type"]}]</span>
<span class="el-name">{r["name"]}</span>
</div>"""
        # 选择列数
        n = len(rows)
        cols = 1 if n <= 2 else 2 if n <= 4 else 3 if n <= 6 else 4
        return f"""<div class="sec sec-cards">
<div class="sec-title">{section_title}</div>
<div class="sec-body card-grid cols{cols}">{items}</div>
</div>"""


GROUP_RULES = [
    ("页面头部", {"Header", "Status", "Badge"}),
    ("元数据栏", {"Label"}),
    ("统计指标", {"Stat", "Gauge"}),
    ("内容区域", {"Card", "Chart", "Table", "List", "Panel"}),
    ("操作区", {"Button", "Filter", "Form", "Tab", "Pagination"}),
    ("折叠面板", {"Collapse"}),
    ("其他", set()),
]


def auto_group(rows: list) -> list:
    """按元素类型自动分组，连续同组元素合并"""
    groups = []
    current_title = None
    current_rows = []
    for r in rows:
        t = r["type"]
        title = "其他"
        for gt, gs in GROUP_RULES:
            if t in gs:
                title = gt
                break
        if title == current_title:
            current_rows.append(r)
        else:
            if current_rows:
                groups.append((current_title, current_rows))
            current_title = title
            current_rows = [r]
    if current_rows:
        groups.append((current_title, current_rows))
    return groups


def build_html(page: dict) -> str:
    pid = page["id"]
    title = page["title"]
    pages_sections = page["sections"]
    all_rows = []
    for _, rows in pages_sections:
        all_rows.extend(rows)

    # 自动分组
    sections = auto_group(all_rows)
    total = len(all_rows)

    sections_html = ""
    for sec_title, rows in sections:
        sections_html += build_section_html(sec_title, rows) + "\n"

    # 收集图例
    seen_types = set()
    legend = ""
    for r in all_rows:
        t = r["type"]
        if t not in seen_types:
            seen_types.add(t)
            c = TYPE_COLORS.get(t, "#ff4757")
            legend += f'<div><span class="dot" style="background:{c};"></span> {t}</div>\n'

    css = """*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#0a0e17;color:#e0e6f0;padding:20px}
.page{max-width:1200px;margin:0 auto}
h1{font-size:22px;color:#dfe6e9;margin-bottom:4px}
.sub{font-size:12px;color:#636e72;margin-bottom:18px}
.sec{margin-bottom:14px;border-radius:8px;overflow:hidden}
.sec-title{font-size:11px;color:#636e72;text-transform:uppercase;letter-spacing:1px;padding:6px 10px;background:rgba(255,255,255,0.02);border-bottom:1px solid rgba(255,255,255,0.04);margin-bottom:0}
.sec-body{padding:8px 10px}
.badge{display:inline-block;color:#fff;font-size:10px;font-weight:700;font-family:Consolas,monospace;padding:1px 5px;border-radius:3px;vertical-align:middle}
/* header */
.sec-header{background:rgba(55,66,250,0.06);border:1px solid rgba(55,66,250,0.12)}
.header-row{display:flex;flex-wrap:wrap;align-items:center;gap:14px;font-size:13px}
.hdr-item{white-space:nowrap}
/* meta */
.sec-meta{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.04)}
.meta-row{display:flex;gap:20px;font-family:Consolas,monospace;font-size:11px;color:#636e72}
/* collapse */
.sec-collapse{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.04)}
.collapse-summary{font-size:12px;color:#a4b0be;cursor:pointer;list-style:none}
.collapse-summary::-webkit-details-marker{display:none}
.collapse-item{padding:4px 0;font-size:12px;border-bottom:1px solid rgba(255,255,255,0.03)}
.ci-type{font-size:9px;color:#636e72}
/* cards */
.sec-cards{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.04)}
.card-grid{display:grid;gap:8px}
.card-grid.cols1{grid-template-columns:1fr}
.card-grid.cols2{grid-template-columns:1fr 1fr}
.card-grid.cols3{grid-template-columns:repeat(3,1fr)}
.card-grid.cols4{grid-template-columns:repeat(4,1fr)}
.el{background:rgba(255,255,255,0.03);border-radius:6px;padding:9px 10px 9px 13px;font-size:12px}
.el-type{font-size:9px;color:#636e72;margin:0 4px}
.el-name{font-size:12px;color:#dfe6e9}
/* table */
.sec-table{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.04)}
.table-body{font-size:12px}
.trow{padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.03);display:flex;align-items:center;gap:8px}
.tcell-type{font-size:9px;color:#636e72}
.tcell-name{color:#dfe6e9}
/* nav */
.sec-nav{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.04)}
.nav-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:8px}
.nav-item{padding:8px 10px;background:rgba(255,255,255,0.03);border-radius:6px;font-size:12px;border:1px solid rgba(255,255,255,0.04)}
/* legend */
.legend{position:fixed;bottom:12px;right:12px;background:rgba(0,0,0,0.88);border-radius:8px;padding:10px 14px;font-size:10px;z-index:100;border:1px solid rgba(255,255,255,0.08);display:grid;grid-template-columns:auto auto;gap:3px 10px}
.legend .dot{display:inline-block;width:8px;height:8px;border-radius:2px;margin-right:4px}
"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{pid} {title} — 元素编号标注</title>
<style>{css}</style></head>
<body>
<div class="page">
<h1>{pid} {title}</h1>
<div class="sub">{len(sections)} 个区域 · {total} 个元素 · 按页面 DOM 顺序从上到下排列</div>
{sections_html}
</div>
<div class="legend">{legend}</div>
</body></html>"""


def main():
    pages = parse_md_sections()
    print(f"Parsed {len(pages)} pages with sections")
    generated = []
    for p in pages:
        if p["id"] in ("A1",):  # A1 already hand-crafted
            continue
        if not p["sections"]:
            print(f"  SKIP {p['id']} — no sections")
            continue
        html = build_html(p)
        filename = f"{p['id']}_ELEMENT_MAP.html"
        (OUT_DIR / filename).write_text(html, encoding="utf-8")
        generated.append(filename)
        print(f"  {filename} — {len(p['sections'])} sections, {sum(len(r) for _,r in p['sections'])} elements")

    # 共用页面
    for src, dst in [("E2", "F3"), ("G1", "F7"), ("G4", "H3")]:
        src_path = OUT_DIR / f"{src}_ELEMENT_MAP.html"
        dst_path = OUT_DIR / f"{dst}_ELEMENT_MAP.html"
        if src_path.exists():
            dst_path.write_text(src_path.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"  COPY {src} → {dst}")

    print(f"\nGenerated {len(generated)} files → {OUT_DIR}")


if __name__ == "__main__":
    main()
