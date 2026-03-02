# frontend-pages-interactive-audit Learnings

- Source inventory: `/opt/claude/mystocks_spec/reports/frontend-pages-inventory.json` with 252 entries.
- Generated standalone report: `/opt/claude/mystocks_spec/reports/frontend-pages-interactive-audit.html`.
- Report data enhancement includes: real file size/line count refresh, component name extraction, inferred description fallback, imports top10, first 80-line code snippet.
- Implemented interactions: directory tree expand/collapse, virtualized row rendering, search/filter/sort, detail panel rendering, batch selection with JSON/CSV export, suggestions counters.
- Visualization panels include overall stats, quality/health/type distribution bars, and domain pie chart.
- No external assets are linked via `<script src>`/`<link href>` and all data is inlined for offline usage.
- New visual report generated at `/opt/claude/mystocks_spec/reports/frontend-pages-visual-audit.html` with 4 switchable views (卡片/列表/分类/建议), card-first metrics, suggestion grouping, detail modal with full source content, and offline embedded dataset/code map.
- 2026-03-02 修复可视化报告代码片段空行问题：重新逐条读取 252 个 Vue 文件，提取前 100 行并压缩连续空行为最多 1 行；卡片仅展示名称/描述/指标/标签，代码仅在详情弹窗展示，并新增文件大小/行数/组件名元信息与代码高亮。
- 2026-03-02 重新生成“简化版”可视化报告：移除复杂视图与重逻辑，保留基础卡片网格 + 搜索/过滤/排序 + 详情弹窗，使用内联 252 条数据并在 DOMContentLoaded 直接渲染，输出文件体积约 86KB（<2MB）。
