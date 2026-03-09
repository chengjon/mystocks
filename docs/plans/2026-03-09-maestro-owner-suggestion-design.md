# Maestro Owner Suggestion Design

## Context

当前 `maestro.collab` 已经能持久化 assignment，并且运行时会根据 assignment 做 owner-aware dispatch。
但 `main CLI` 在真正写入 assignment 之前，仍然需要手动结合：

- `.FILE_OWNERSHIP`
- `TASK.md`
- 当前任务涉及的文件/模块

来决定最合适的 owner。这个判断本质上仍应由 `main CLI` 做最终裁决，但可以由系统先给出“带理由的建议”。

## Goals

- 提供一个保守的 owner suggestion 能力
- 优先使用 `.FILE_OWNERSHIP` 的规则匹配
- 可从 `TASK.md` 中提取路径提示，辅助 main CLI 判断
- 输出候选 owner、匹配路径、未覆盖路径和理由
- 不自动改写 assignment，保持 main CLI 最终决策权

## Non-Goals

- 本轮不自动从自然语言完全理解复杂任务语义
- 本轮不直接根据建议自动 assign
- 本轮不替代 `.FILE_OWNERSHIP` 的人工治理角色

## Recommended Approach

采用 **规则优先的半自动建议器**：

1. 解析 `.FILE_OWNERSHIP`
2. 收集候选路径：
   - CLI 显式传入的 `--path`
   - `TASK.md` 中提取到的路径样式提示
3. 用路径匹配归属 owner
4. 按命中数量与覆盖度给出排序建议
5. 对未覆盖路径统一回落到 `main`

## Matching Rules

- 目录模式（如 `src/`）匹配目录下任意文件
- 通配模式（如 `docs/guides/GPU_MONITORING*`）使用 glob/fnmatch
- 精确文件模式精确匹配
- 未匹配路径默认 owner 为 `main`

## Output Shape

建议结果包括：

- `suggested_owner`
- `candidate_owners`
- `matched_paths`
- `unowned_paths`
- `task_path_hints`
- `reasons`

## Operator Flow

1. `main CLI` 编写 / 更新 `TASK.md`
2. 运行 `maestro_collab.py suggest`
3. 查看建议 owner 与理由
4. 再决定是否执行 `assign`

这样既能节省判断成本，也不会让运行时越权替代主协调者。
