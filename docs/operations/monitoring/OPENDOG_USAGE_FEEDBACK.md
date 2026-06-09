# OPENDOG Usage Feedback

> 目的:
> 这是 `mystocks` 使用 OpenDog 的长期反馈主文档。
> 文档分为两层:
> 1. 日常使用经验
> 2. 可直接驱动 OpenDog 调优的工程证据
>
> 主要读者:
> - `mystocks` 开发和运维人员
> - OpenDog 维护者
>
> 核心原则:
> 记录证据, 不只记录结论。

## 如何使用本文档

- 按日期持续追加, 不要每次重写整份文件。
- 优先记录短摘要, 同时保留精确命令、输出文件路径、复现说明。
- 如果原始输出很大, 请把原始内容放到单独 artifact 文件, 这里只写摘要并附路径。
- 明确区分“发生了什么”和“我们猜测原因是什么”。
- 不要把 `unused` 直接理解为“可以删除”。
- 不要粘贴密钥、token、账号口令等敏感信息。

## 记录规则

- 每条记录至少包含:
  - 日期
  - 记录人
  - OpenDog 使用入口: `MCP` 或 `CLI`
  - 项目状态: snapshot 是否新鲜, monitor 是否开启
  - 精确命令或 tool call
  - 期望行为
  - 实际行为
  - 对真实工作的影响
- 能写绝对路径就写绝对路径, 能写精确时间就写精确时间。
- 如果问题是偶发的, 要明确标注。
- 如果问题只在大结果集上出现, 要写出大致文件数量级。

## 当前最值得帮助 OpenDog 验证的问题

这些是后续 OpenDog 调优价值最高的问题。

1. `get_stats` 和 `get_unused_files` 的 MCP 失败, 是否主要和超大 payload 有关, 而不是 daemon 复用冲突?
2. OpenDog 是否需要文件分类层, 把 infrastructure 文件和 source 文件分开, 同时改善 `unused` 噪声和热点结果可读性?
3. MCP 工具在跨会话、重启、重连后是否稳定出现, 其状态字段是否准确表达“daemon 存活”和“项目正在被监控”的区别?
4. 在 `OPENDOG_HOME` 固定的前提下, daemon 复用在跨终端、重连、长会话场景里是否稳定?
5. 访问次数、修改次数、最后访问时间是否符合开发者直觉?
6. `limit`、分页、目录过滤、文件类型过滤是否会显著改善真实使用体验?
7. `get_guidance` 在实践中是否真的有帮助, 还是还需要更强的项目级优先级表达?

## 建议保留的证据命令

按需使用, 不要求每次都全跑。

```bash
opendog list
opendog stats --id mystocks
opendog unused --id mystocks
opendog agent-guidance --project mystocks --json
opendog decision-brief --project mystocks --json
opendog report window --id mystocks --window 24h --json
opendog report trend --id mystocks --window 7d --json
opendog report compare --id mystocks --json
```

如果问题是 MCP 专属, 还应补充记录:

- MCP host 名称
- 相同行为是否可通过 CLI 成功完成
- 项目当时是否已经处于 `monitoring`
- `OPENDOG_HOME` 是否固定

## 第一层: 日常使用经验

这一层只记录真实开发工作中的使用体验。

### 记录模板

```md
### YYYY-MM-DD - 简短标题

- 记录人:
- 目标:
- 使用入口: MCP / CLI
- 项目状态:
- 命令或 tool calls:
- 哪些地方有帮助:
- 哪些地方有困惑或摩擦:
- 临时绕行方案:
- 结果:
- 后续跟进:
```

### 2026-05-08 - 初始基线

- 记录人: bootstrap / validation run
- 目标: 验证 OpenDog 能否完成 `mystocks` 注册、初始快照、启动监控、输出可用统计
- 使用入口: MCP + CLI
- 项目状态: project registered, initial snapshot completed, monitor active
- 命令或 tool calls:
  - MCP: `register_project`, `take_snapshot`, `start_monitor`
  - CLI: `opendog stats --id mystocks`
  - CLI: `opendog unused --id mystocks`
- 哪些地方有帮助:
  - 项目注册和快照流程可用
  - `start_monitor` 成功
  - CLI `stats` 和 `unused` 稳定且可立即用于观察
- 哪些地方有困惑或摩擦:
  - `unused` 中出现大量 `.claude/`、`.claude/hooks/`、`.claude/agents/`、`.amazonq/` 等基础设施文件
  - 这些文件属于“未观测到访问”, 但不等于“应删除”
  - 对 5 万级文件仓库, MCP `get_stats` 和 `get_unused_files` 的实用性低于 CLI
- 临时绕行方案:
  - 项目生命周期操作继续用 MCP
  - 大结果集观察优先用 CLI
- 结果:
  - 初始基线已建立
  - OpenDog 已经能提供真实使用价值, 但结果整形和噪声控制仍需调优
- 后续跟进:
  - 持续收集 payload 大小、结果噪声、热点排序价值等证据

### 2026-05-09 - MCP 四项核心工具验证（release rebuild）

- 记录人: Claude (GLM-5.1)
- 目标: 重新构建 release 二进制后，验证 `list_projects`、`get_stats`、`get_unused_files`、`get_guidance` 的 MCP 可用性
- 使用入口: MCP + CLI
- 项目状态: snapshot 50087 文件, daemon running (PID 3746676), file_stats 3196 条, file_events 269249 条, file_sightings 828296 条
- 命令或 tool calls:
  - `cargo build --release` → 成功, 新二进制 02:00:43
  - MCP: `list_projects` → 成功，含完整 guidance 嵌入
  - MCP: `get_stats {id: "mystocks"}` → MCP error -32000: Connection closed
  - MCP: `get_unused_files {id: "mystocks"}` → 成功但 5.9M chars 过大被截断到文件
  - MCP: `get_guidance {project_id: "mystocks", detail: "decision", top: 3}` → serialization_error: EOF while parsing a value at line 1 column 0
  - CLI: `opendog stats --id mystocks` → 成功, 50087 files | 36 accessed | 50051 unused
  - CLI: `opendog unused --id mystocks` → 成功, 50051 条
  - CLI: `opendog decision-brief --project mystocks --top 3` → 成功, 完整 8-layer 信号输出
  - CLI: `opendog agent-guidance --project mystocks --top 3` → 成功
- 哪些地方有帮助:
  - `list_projects` MCP 首次成功返回含 guidance 嵌入的完整响应
  - `decision-brief` CLI 输出质量高: 8-layer 信号、执行模板、repo risk 分析全部可用
  - `agent-guidance` CLI 清晰展示了 verification_missing 阻塞状态
  - daemon 自动运行（PID 3746676），跨终端复用稳定
- 哪些地方有困惑或摩擦:
  - `get_stats` MCP 仍崩溃 (Case A 更新)
  - `get_guidance` (decision) MCP 返回 serialization_error (Case G 新增)
  - `get_unused_files` MCP 返回 5.9M chars 超出 token 限制
  - `/root/.opendog/data/mystocks.db` 为 0 bytes 残留空文件，真实 DB 在 `projects/` 子目录
- 临时绕行方案:
  - stats 和 guidance 全部走 CLI
  - unused 走 CLI + 管道过滤
  - MCP 仅用于 list_projects 和生命周期操作
- 结果:
  - release 重建成功，新二进制已部署
  - MCP 3/4 核心读取工具仍有问题，CLI 全部正常
  - Case A 根因更新: 50K 文件全量序列化 JSON 过大导致 MCP transport 断开（之前假设"payload 很小"有误）
  - Case G 新增: daemon socket 响应截断导致 decision_brief 反序列化失败
- 后续跟进:
  - 新会话验证 MCP 是否能正常使用新二进制
  - 等待 opendog 添加 `limit` 参数后重测 get_stats

### 2026-05-08 - MCP + CLI 混合验证会话

- 记录人: Claude (GLM-5.1)
- 目标: 配置 OpenDog MCP、激活监控、采集初始观测证据、审阅反馈模板
- 使用入口: MCP + CLI
- 项目状态: snapshot 50087 文件, monitor active, file_stats 1271 条
- 命令或 tool calls:
  - MCP: `register_project {id: "mystocks", path: "/opt/claude/mystocks_spec"}`
  - MCP: `take_snapshot {id: "mystocks"}` → 50087 files
  - MCP: `start_monitor {id: "mystocks"}` → already_running: true, status: monitoring
  - MCP: `get_stats {id: "mystocks"}` → MCP error -32000: Connection closed
  - MCP: `get_unused_files {id: "mystocks"}` → MCP error -32000: Connection closed
  - CLI: `opendog stats --id mystocks` → 成功, 4.5KB 输出
  - CLI: `opendog unused --id mystocks` → 成功, 6.3KB, 103 行
  - CLI: `sqlite3 mystocks.db "SELECT ..."` → 直接查 DB 确认 attribution 异常
- 哪些地方有帮助:
  - CLI stats/unused 稳定可用, 不受 MCP 连接状态影响
  - SQLite 直接查询能验证 MCP/CLI 报告的准确性
  - daemon 自动拉起机制可靠, 跨终端可用
- 哪些地方有困惑或摩擦:
  - `get_stats` 和 `get_unused_files` MCP 调用失败, CLI 同等操作成功 (Case A)
  - 30 个 `.claude/` 文件共享完全相同的 access_count=5293 和 duration=16051000ms (Case D)
  - 源码文件 (src/*, web/*) 的 access_count 全部为 0, 只有 modification_count > 0 (Case C)
  - `start_monitor` 返回 `already_running: true` 但首次调用时 file_stats=0 (Case F)
- 临时绕行方案:
  - 所有读取操作走 CLI, 仅生命周期操作 (register/snapshot/start) 用 MCP
  - 手动过滤 `.claude/` 目录来获得有意义的热点视图
- 结果:
  - Case A 确认: CLI 成功 (4.5KB stats, 6.3KB unused), MCP 失败, 排除大 payload 假设 (payload 很小)
  - Case B 确认: unused 输出中 1239/1271 条为基础设施文件
  - Case C 确认: 热点前 30 名全是 .claude/ 配置文件, 零源码文件
  - Case D 确认: 30 个 .claude/ 文件共享完全相同的 attribution 数值 (5293 access, 16051000ms)
  - Case F 确认: already_running 字段语义含混
- 后续跟进:
  - 在源码密集编辑会话中复测 Case D
  - 测试 MCP 单独调用 get_stats (不与 start_monitor 并发) 是否稳定

## 第二层: OpenDog 调优证据

这一层只记录那些应该影响 OpenDog 设计、默认值、接口契约或结果表达方式的问题。

### 记录模板

```md
### YYYY-MM-DD - 调优项标题

- 类型: bug / design gap / UX friction / performance / classification noise / documentation gap
- 严重度: low / medium / high
- 是否稳定复现: yes / no / unknown
- 涉及入口: MCP / CLI / daemon / mixed
- 项目事实:
  - snapshot 文件数:
  - accessed 数:
  - unused 数:
  - monitor 是否开启:
- 环境:
  - host:
  - terminal 或 IDE:
  - OPENDOG_HOME:
- 精确步骤:
  1.
  2.
  3.
- 期望行为:
- 实际行为:
- 对真实工作的影响:
- 证据:
  - command:
  - output 摘要:
  - artifact 路径:
- 假设:
- 建议的调优方向:
```

### 优先关注的调优案例

#### Case A - MCP 观察结果过大

- 触发条件:
  - 大仓库
  - `get_unused_files` 返回数万条路径
  - `get_stats` 返回很大的 `files` 数组
- 建议记录:
  - CLI 是否成功而 MCP 失败
  - 是否只有 `stats` 和 `unused` 出问题
  - 结果集的大致规模
  - 近似响应大小:
    - CLI 输出约多少 KB / 多少行
    - MCP JSON payload 若可获得约多少 KB
  - 重试后是否有变化
- 为什么重要:
  - OpenDog 可能需要分页、`limit`、目录过滤或 summary-first 契约

#### Case B - `unused` 中的基础设施噪声

- 触发条件:
  - `.claude/`、`.amazonq/`、hook 脚本、agent 提示词、工具元数据在 unused 结果里占比过高
- 建议记录:
  - 哪些目录组应视为噪声
  - 它们更适合被默认忽略、软分类、还是单独标注
  - 相同模式是否在多天内持续出现
- 为什么重要:
  - “未观测到访问”不等于“值得进入清理候选”

#### Case C - 热点结果被 AI 工具文件主导

- 触发条件:
  - 最活跃文件主要是配置和编排文件, 而不是业务源码
- 建议记录:
  - 开发者是否仍然觉得当前排序有价值
  - `source-only view` 是否会更有帮助
  - 按路径族过滤是否会明显改善体验
- 为什么重要:
  - OpenDog 可能需要替代性的热点视图

#### Case D - attribution 可信度

- 触发条件:
  - 访问次数或时间戳与开发者真实操作明显不符
- 建议记录:
  - 开发者实际做了什么
  - 哪些文件本应被看到
  - 哪些文件被漏记或高估
  - 这个偏差是否能重复出现
- 为什么重要:
  - attribution 可信度是 OpenDog 的核心价值

#### Case G - daemon socket 响应截断导致 MCP serialization_error

- 触发条件:
  - daemon 正在运行
  - MCP 调用 `get_guidance` (detail=decision) 通过 Unix socket 与 daemon 通信
  - daemon 返回的 JSON 响应较大
- 建议记录:
  - CLI 同等操作是否成功
  - daemon 是否正在运行（pid 文件 + 进程存活）
  - socket 文件是否存在
  - 错误信息中是否包含 "EOF while parsing"
- 为什么重要:
  - `DaemonClient::send()` 在 `serde_json::from_slice` 对空/截断响应直接报错
  - 未区分"daemon 未运行"和"daemon 响应截断"两种情况
  - 阻塞了 MCP guidance 功能的可用性

#### Case E - guidance 的实战价值

- 触发条件:
  - `get_guidance` 太泛、太吵, 或者非常有用
- 建议记录:
  - guidance 的原始摘要
  - 推荐的下一步是否符合真实需要
  - 开发者最终改用了什么动作
- 为什么重要:
  - OpenDog 的 guidance 应该降低决策成本, 而不是增加又一层摘要负担

#### Case F - MCP 会话生命周期与状态语义

- 触发条件:
  - 某次会话里能看到 MCP 工具, 重启后工具消失
  - `opendog mcp` 声称会自动复用 daemon, 但宿主会话中工具面不稳定
  - `start_monitor` 返回 `already_running = true`, 但项目证据表为空或项目并未实际进入有效观测
- 建议记录:
  - MCP 工具在当前宿主是否可见
  - daemon 是否存在
  - 项目是否真的有新增 `file_stats` / `file_events` / `file_sightings`
  - 返回字段是否容易误导操作者
  - CLI 与 MCP 在同一时刻的表现是否一致
- 为什么重要:
  - 如果 MCP 生命周期和状态语义不稳定, 用户会退回 CLI, 这会直接削弱 MCP 集成价值

### 2026-05-08 - Case A: get_stats MCP 失败但 payload 很小

- 类型: bug
- 严重度: medium
- 是否稳定复现: yes (同会话内重试仍失败)
- 涉及入口: MCP
- 项目事实:
  - snapshot 文件数: 50087
  - accessed 数: 32
  - unused 数: 1239
  - monitor 是否开启: yes (status: monitoring)
- 环境:
  - host: WSL2 Linux 6.6.87.2
  - terminal: Claude Code CLI (GLM-5.1 model)
  - OPENDOG_HOME: /root/.opendog
- 精确步骤:
  1. MCP `start_monitor {id: "mystocks"}` → 成功, already_running: true
  2. MCP `get_stats {id: "mystocks"}` → MCP error -32000: Connection closed
  3. MCP `get_unused_files {id: "mystocks"}` → MCP error -32000: Connection closed
  4. CLI `opendog stats --id mystocks` → 成功, 输出 4.5KB / 50 行
  5. CLI `opendog unused --id mystocks` → 成功, 输出 6.3KB / 103 行
- 期望行为: MCP get_stats 返回与 CLI stats 相同的结果
- 实际行为: MCP 返回 connection closed, CLI 同等操作成功
- 对真实工作的影响: 必须退回 CLI 做所有读取操作, MCP 仅用于 register/snapshot/start
- 证据:
  - command: `opendog stats --id mystocks | wc -c` → 4537 bytes
  - command: `opendog unused --id mystocks | wc -c` → 6321 bytes
  - payload 很小, 排除"超大 payload 导致连接断开"的假设
  - 三次调用在同一 turn 并发发出, start_monitor 成功后两个读取失败
- 假设: 并发 MCP 调用导致 stdio pipe 竞态, 或 start_monitor 的 daemon 重连中断了已有 MCP 连接
- 建议的调优方向:
  - 测试 MCP 串行调用 (start_monitor 完成后再调用 get_stats) 是否稳定
  - 在 MCP 服务端增加 stdio pipe 错误恢复机制

### 2026-05-08 - Case C+D: attribution 异常 — 同目录 30 个文件共享完全相同的访问计数

- 类型: bug
- 严重度: high
- 是否稳定复现: yes
- 涉及入口: daemon (observation), CLI (readout)
- 项目事实:
  - snapshot 文件数: 50087
  - accessed 数: 32
  - unused 数: 1239
  - monitor 是否开启: yes
- 环境:
  - host: WSL2 Linux 6.6.87.2
  - terminal: Claude Code CLI
  - OPENDOG_HOME: /root/.opendog
- 精确步骤:
  1. `sqlite3 mystocks.db "SELECT file_path, access_count, estimated_duration_ms FROM file_stats WHERE access_count > 0 ORDER BY access_count DESC"`
  2. 结果: 30 个 `.claude/` 文件全部 access_count=5293, estimated_duration_ms=16051000
  3. 仅 2 个文件有不同 attribution: settings.local.json (access=17, dur=49000) 和 .env (access=1, dur=0)
  4. 源码文件 (src/*, web/*) 的 access_count 全部为 0, 仅 modification_count > 0
- 期望行为: 不同文件有不同的访问计数, 反映实际访问频率差异
- 实际行为: 30 个 .claude/ 文件共享完全相同的 access_count=5293 和 duration=16051000ms
- 对真实工作的影响: 热点分析完全不可用 — 无法区分哪些配置文件真正被频繁访问, 源码热点完全缺失
- 证据:
  - command: `sqlite3 mystocks.db "SELECT COUNT(*) as n, access_count, estimated_duration_ms FROM file_stats WHERE access_count > 0 GROUP BY access_count, estimated_duration_ms ORDER BY n DESC;"`
  - output: `30|5293|16051000` — 30 个文件共享同一组数值
  - output: `1|1|0` — .env 唯一独立值
  - output: `1|17|49000` — settings.local.json 唯一独立值
  - 源码查询: `SELECT FROM file_stats WHERE path LIKE 'src/%' AND access_count > 0` → 空
- 假设: `/proc/<pid>/fd/` 扫描发现进程打开了 `.claude/` 目录 fd, 将目录级访问归因到目录下所有快照中的文件
- 建议的调优方向:
  - 在 attribution 逻辑中区分文件级 fd 和目录级 fd
  - 仅当 fd 指向具体文件 (非目录) 时才计入 access_count
  - 增加去重: 同一次扫描周期内同一 fd 不应重复计入

### 2026-05-09 - Case A 更新: get_stats MCP 崩溃根因确认 — 50K 条目全量 JSON 过大

- 类型: bug / performance
- 严重度: high
- 是否稳定复现: yes
- 涉及入口: MCP (daemon socket → MCP stdio)
- 项目事实:
  - snapshot 文件数: 50087
  - accessed 数: 36
  - unused 数: 50051
  - file_stats: 3196 条
  - monitor 是否开启: yes
- 环境:
  - host: WSL2 Linux 6.6.87.2
  - terminal: Claude Code CLI (GLM-5.1 model)
  - OPENDOG_HOME: /root/.opendog
  - release binary: /opt/claude/opendog/target/release/opendog (built 2026-05-09 02:00:43)
  - daemon: PID 3746676, socket /root/.opendog/data/daemon.sock
- 精确步骤:
  1. `cargo build --release` → 成功
  2. MCP `list_projects` → 成功, 含完整 guidance
  3. MCP `get_stats {id: "mystocks"}` → MCP error -32000: Connection closed
  4. MCP `get_unused_files {id: "mystocks"}` → 成功, 5.9M chars (截断到文件)
  5. MCP `get_guidance {detail: "decision", top: 3}` → serialization_error
  6. CLI `opendog stats --id mystocks` → 成功
  7. CLI `opendog decision-brief --project mystocks --top 3` → 成功 (101KB JSON)
- 期望行为: MCP get_stats 返回与 CLI stats 等价的 JSON
- 实际行为: MCP 连接断开, CLI 正常
- 对真实工作的影响: 所有 stats/guidance 读取操作必须退回 CLI
- 证据:
  - `stats_payload` 函数将 50087 条 file_stats 全量序列化为 JSON (每条 7 字段)
  - `get_unused_files` 成功但 5.9M chars → MCP stdio 能传大数据但接近极限
  - `get_stats` 每条 7 字段 vs `get_unused_files` 每条 3 字段 → stats payload 更大, 超过传输极限
  - CLI `decision-brief --json` = 101KB → 正常大小
  - daemon 进程确认运行: PID 3746676, socket 存在
  - 真实数据库: `/root/.opendog/data/projects/mystocks.db` (204MB)
  - 残留空文件: `/root/.opendog/data/mystocks.db` (0 bytes, 应清理)
- 假设:
  - 之前的 05-08 记录中"payload 很小(4.5KB)"是 CLI 文本输出的截断显示, 不是完整 JSON payload
  - 完整 JSON payload 包含所有 50K 条目, 远超 MCP stdio 或 daemon socket 缓冲
- 建议的调优方向:
  - `get_stats` MCP 增加 `limit` 参数, 默认返回前 50 条, 附 summary 概览
  - `get_unused_files` MCP 同样增加分页
  - daemon socket 传输考虑大响应分块机制
  - 或提供 `stats_summary` MCP 工具, 只返回 summary 不返回 files 数组

### 2026-05-09 - Case G: get_guidance (decision) MCP 返回 serialization_error

- 类型: bug
- 严重度: medium
- 是否稳定复现: yes (同会话)
- 涉及入口: MCP + daemon (socket IPC)
- 项目事实:
  - snapshot 文件数: 50087
  - file_stats: 3196
  - monitor 是否开启: yes
- 环境:
  - host: WSL2 Linux 6.6.87.2
  - terminal: Claude Code CLI (GLM-5.1 model)
  - OPENDOG_HOME: /root/.opendog
  - daemon: PID 3746676, socket /root/.opendog/data/daemon.sock 存在
- 精确步骤:
  1. MCP `get_guidance {project_id: "mystocks", detail: "decision", top: 3}`
  2. → `{"error":"Serialization error: EOF while parsing a value at line 1 column 0","error_code":"serialization_error","project_id":"mystocks","schema_version":"opendog.mcp.decision-brief.v1","status":"error"}`
  3. CLI `opendog decision-brief --project mystocks --top 3` → 成功, 完整输出
  4. CLI `opendog decision-brief --project mystocks --top 3 --json` → 成功, 101322 bytes 有效 JSON
- 期望行为: MCP 返回与 CLI 等价的 decision brief JSON
- 实际行为: MCP 返回 serialization_error, CLI 正常
- 对真实工作的影响: decision brief 必须走 CLI
- 证据:
  - daemon 正在运行且 socket 存在
  - `DaemonClient::send()` 通过 Unix socket 发送请求, daemon 返回响应
  - 当 daemon 响应被 socket 截断或为空时, `serde_json::from_slice(&response)` 报 "EOF at line 1 column 0"
  - 该错误通过 `#[from] serde_json::Error` 自动转为 `OpenDogError::Serialization`
  - `error_json_for` 将其包装为结构化错误返回
  - CLI 等价操作产出 101KB 有效 JSON, 证明业务逻辑正确
- 假设:
  - daemon socket 响应过大被内核截断
  - 或 daemon 在序列化 50K stats 条目到 socket 时 I/O 中断
- 建议的调优方向:
  - daemon socket 响应发送增加完整性校验
  - `DaemonClient::send()` 增加空响应/截断检测, 区分 "daemon 未运行" vs "daemon 响应损坏"
  - decision brief 在 daemon 端不加载全量 stats (用 summary 代替)

### 2026-05-08 - Case B: unused 结果中 97.7% 为基础设施文件

- 类型: classification noise
- 严重度: medium
- 是否稳定复现: yes
- 涉及入口: CLI
- 项目事实:
  - snapshot 文件数: 50087
  - file_stats: 1271
  - accessed: 32
  - unused: 1239
  - monitor 是否开启: yes
- 环境:
  - host: WSL2 Linux 6.6.87.2
  - OPENDOG_HOME: /root/.opendog
- 精确步骤:
  1. CLI `opendog unused --id mystocks`
  2. 输出 103 行, 前 60+ 行全部是 `.claude/hooks/`, `.claude/agents/`, `.amazonq/prompts/` 文件
- 期望行为: unused 列表优先展示业务代码中的低活跃文件
- 实际行为: unused 列表被工具基础设施文件主导
- 对真实工作的影响: 无法从 unused 列表直接获得有价值的清理建议
- 证据:
  - command: `opendog unused --id mystocks | head -60`
  - 前 60 行全部为: `.claude/hooks/*.sh`, `.claude/hooks/*.py`, `.claude/agents/*.md`, `.amazonq/prompts/*.md`, `.claude/commands/*.md`
  - 这些是 Claude Code 工具链基础设施, 不应作为清理候选
- 假设: 默认 ignore patterns 不包含 AI 工具目录
- 建议的调优方向:
  - 默认 ignore 增加: `.claude/`, `.amazonq/`, `.cursor/`, `*.bak.*`, `*.backup*`
  - 或增加文件分类: infrastructure vs source, 允许 unused 按分类过滤

## 解释边界

- `unused` 的含义是“在当前证据窗口中未观测到访问”。
- `unused` 不等于:
  - dead code
  - safe to delete
  - 对工具链不重要
  - 对后续流程不重要
- 一个文件完全可能在运维或工具链上很重要, 但仍然显示为 `unused`。
- 在做清理、删除、重构判断前, 必须结合仓库上下文、验证证据、人工 review 一起判断。

## 月度总结模板

当证据积累到一定程度后, 用这一节做阶段总结。

```md
## YYYY-MM Summary

- OpenDog 最有帮助的地方:
- 最主要的摩擦点:
- 重复出现的误报或噪声模式:
- CLI 与 MCP 的分工现状:
- 证据量:
  - 总调优案例数:
  - 已确认可稳定复现的案例数:
  - 后续自行消失或无法复现的案例数:
- 下一周期最值得做的调优请求:
- 证据链接:
```
