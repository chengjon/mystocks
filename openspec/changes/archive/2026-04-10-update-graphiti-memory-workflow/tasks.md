## 1. Implementation

> **使用说明**:
> 本文件用于记录当前 OpenSpec 变更的执行清单、操作步骤或协作约束，帮助跟踪实施过程。
> 其中勾选状态、执行顺序和局部说明仅代表任务推进视角，不应脱离 proposal、design、正式 specs、`architecture/STANDARDS.md` 与实际验证结果单独解读为最终事实。


- [x] 1.1 Add an OpenSpec delta that defines Graphiti MCP as the project memory layer and preserves Mongo as the coordination source of truth.
- [x] 1.2 Update `.mcp.json` to include the verified Graphiti MCP HTTP endpoint and remove Apifox from active project MCP usage.
- [x] 1.3 Update `config/.mcp.json` to stop advertising the legacy Apifox MCP entry.
- [x] 1.4 Add a Graphiti workflow guide that defines usage boundaries, `group_id` conventions, and recommended tool call order.
- [x] 1.5 Update the Mongo multi-CLI guide with explicit Graphiti/Mongo boundary rules.
- [x] 1.6 Run focused validation on the changed JSON and OpenSpec files.
