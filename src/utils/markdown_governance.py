from __future__ import annotations

import re


BOUNDARY_NOTE_TITLES: tuple[str, ...] = (
    "权威来源声明",
    "导航说明",
    "使用说明",
    "Usage Note",
    "历史分析说明",
    "历史计划说明",
    "历史索引说明",
    "历史文档说明",
    "历史总结说明",
    "历史架构说明",
    "参考指南说明",
    "设计方案说明",
    "补充规范说明",
    "历史决策说明",
    "历史路线图说明",
    "历史状态说明",
    "历史实施说明",
    "历史任务说明",
    "历史归档说明",
    "历史复盘说明",
    "参考方法说明",
    "专题方案说明",
    "参考模板说明",
    "历史盘点说明",
    "历史部署说明",
)

BOUNDARY_NOTE_PATTERN = re.compile(
    rf"^> \*\*({'|'.join(re.escape(title) for title in BOUNDARY_NOTE_TITLES)})\*\*:",
    re.M,
)

BOUNDARY_NOTE_PRESETS: dict[str, dict[str, str | tuple[str, ...]]] = {
    "navigation": {
        "title": "导航说明",
        "body_lines": (
            "本文件是导航页或索引页，不是当前仓库共享规则或实现状态的唯一事实来源。",
            "若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及具体执行入口，再按职责分别参考根目录 `AGENTS.md` 与根目录 `CLAUDE.md`。",
        ),
    },
    "authority": {
        "title": "权威来源声明",
        "body_lines": (
            "本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。",
            "若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。",
        ),
    },
    "usage": {
        "title": "使用说明",
        "body_lines": (
            "本文件是执行入口或使用说明，不是仓库共享规则的唯一事实来源。",
            "仓库级共享规则与当前执行口径以 `architecture/STANDARDS.md` 为准；若涉及执行流程、命令与协作约束，再参考根目录 `AGENTS.md` 与根目录 `CLAUDE.md`。",
        ),
    },
    "supplemental": {
        "title": "补充规范说明",
        "body_lines": (
            "本文件是补充标准、执行细则或专题规范，不是仓库共享规则的唯一事实来源。",
            "仓库级共享规则总入口仍以 `architecture/STANDARDS.md` 为准；执行流程、命令与协作约束再参考根目录 `AGENTS.md`，涉及 OpenSpec 提案、规格或变更流程时再参考 `openspec/AGENTS.md`。",
        ),
    },
    "historical": {
        "title": "历史文档说明",
        "body_lines": (
            "本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。",
            "若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。",
        ),
    },
}


def recommend_boundary_note_preset(path_value: str) -> str:
    normalized = path_value.lower()
    file_name = path_value.rsplit("/", 1)[-1].lower()
    parts = set(path_value.split("/"))

    if file_name in {"index.md", "readme.md"}:
        return "navigation"
    if file_name in {"agents.md", "claude.md", "gemini.md"}:
        return "usage"
    if file_name == "task.md" or path_value.startswith(".agent/"):
        return "usage"
    if {"reports", "archive", "worklogs"} & parts or path_value.startswith(".planning/") or "changes/" in normalized:
        return "historical"
    if {"standards", "architecture"} & parts or "charter" in normalized or "constitution" in normalized:
        return "supplemental"
    return "authority"
