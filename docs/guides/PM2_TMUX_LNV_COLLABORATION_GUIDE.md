# PM2、Tmux 和 Lnav 协作开发运维指南（可执行版）

## 文档目标

本指南用于在 MyStocks 项目中建立一套“可落地、可复现”的协作流程：

- `PM2` 负责服务进程管理（启动、重启、日志、状态）
- `Tmux` 负责多人/多任务并行终端协作
- `Lnav` 负责日志聚合与故障定位

> 本文档已按当前仓库现状修订，优先保证命令可执行。

---

## 当前基线（必须统一）

- 后端服务名：`mystocks-backend`
- 前端服务名：`mystocks-frontend`
- 后端地址：`http://localhost:8000`
- 前端地址：`http://localhost:3020`

快速校验：

```bash
pm2 list
curl -f http://localhost:8000/health
curl -f http://localhost:3020
```

---

## 一、PM2 协作规范

### 1. 启动/重启命令（推荐）

```bash
# 在仓库根目录执行
pm2 start web/backend/ecosystem.config.js --only mystocks-backend
pm2 start web/frontend/ecosystem.config.js --only mystocks-frontend

# 重启单服务
pm2 restart mystocks-backend
pm2 restart mystocks-frontend

# 查看状态与详细信息
pm2 list
pm2 describe mystocks-backend
pm2 describe mystocks-frontend
```

### 2. 日志查看（优先 PM2）

```bash
pm2 logs mystocks-backend --lines 100
pm2 logs mystocks-frontend --lines 100
pm2 monit
```

### 3. 常用排障动作

```bash
# 快速确认端口监听
lsof -i :8000
lsof -i :3020

# 重载配置（不中断服务）
pm2 reload web/frontend/ecosystem.config.js --only mystocks-frontend
pm2 reload web/backend/ecosystem.config.js --only mystocks-backend
```

---

## 二、Tmux 协作规范

### 1. 推荐脚本

当前可用的 tmux 会话脚本：

- `scripts/dev/tmux_session.sh`（开发会话）
- `scripts/setup_tmux_session.sh`（CI/CD 会话）
- `scripts/dev/start-tmux-simple.sh`（简化 5 窗格）

推荐使用：

```bash
./scripts/dev/tmux_session.sh start
```

常用命令：

```bash
tmux list-sessions
tmux attach -t mystocks_dev
tmux kill-session -t mystocks_dev
```

### 2. 协作建议布局

- 窗口 1：`PM2` 状态和重启操作
- 窗口 2：后端日志/健康检查
- 窗口 3：前端日志/页面访问验证
- 窗口 4：`Lnav` 深度分析

---

## 三、Lnav 日志分析规范

### 1. 推荐日志输入

优先使用真实存在的日志文件：

- `web/frontend/logs/frontend-error.log`
- `web/frontend/logs/frontend-out.log`
- `web/backend/logs/backend.log`
- `/root/.pm2/logs/mystocks-backend-error.log`
- `/root/.pm2/logs/mystocks-backend-out.log`

### 2. 示例命令

```bash
# 后端日志分析
lnav web/backend/logs/backend.log /root/.pm2/logs/mystocks-backend-error.log

# 前端日志分析
lnav web/frontend/logs/frontend-error.log web/frontend/logs/frontend-out.log

# 按错误级别过滤
lnav -c ":filter-in ERROR|CRITICAL" web/backend/logs/backend.log

# 导出 JSON 报告
lnav -c ":export-to-json /tmp/mystocks-log-report.json" web/backend/logs/backend.log
```

### 3. 辅助脚本

可使用：

```bash
./scripts/lnav-monitor.sh help
```

---

## 四、监控脚本集成（当前状态）

监控脚本位置为：`scripts/dev/automation/monitor_and_fix.py`

```bash
# 单次检查
python scripts/dev/automation/monitor_and_fix.py --check-once
```

注意事项：

- 默认配置路径在脚本内写的是 `scripts/automation/monitor_config.json`，仓库实际配置为 `scripts/dev/automation/monitor_config.json`。
- 若需指定配置，建议显式传参：

```bash
python scripts/dev/automation/monitor_and_fix.py \
  --config /opt/claude/mystocks_spec/scripts/dev/automation/monitor_config.json \
  --check-once
```

- `--daemon` 模式当前不稳定（脚本内部尚有待修复项），不建议用于生产值守。

---

## 五、标准协作流程（建议）

1. 启动并确认 PM2 双服务在线：`mystocks-backend` / `mystocks-frontend`
2. 用 `tmux` 建立协作会话并固定窗口职责
3. 用 `pm2 logs` 做实时观察，用 `lnav` 做深度分析
4. 每次变更后执行健康检查：`/health` 与前端首页
5. 问题闭环后记录“故障现象-根因-命令证据”

---

## 六、已知限制与替代方案

### 1. 不建议使用的脚本

`scripts/dev/tmux-enhanced-session.sh` 当前存在语法错误，暂不作为标准入口。

### 2. 文档路径统一

历史文档中的以下路径已过时：

- `scripts/automation/monitor_and_fix.py`（应为 `scripts/dev/automation/monitor_and_fix.py`）
- `ecosystem.enhanced.config.js`（应使用仓库内实际路径，如 `config/pm2/ecosystem.enhanced.config.js`）

---

## 七、关联文件

- 前端 PM2 配置：`web/frontend/ecosystem.config.js`
- 后端 PM2 配置：`web/backend/ecosystem.config.js`
- 增强 PM2 配置（历史增强版）：`config/pm2/ecosystem.enhanced.config.js`
- Tmux 开发脚本：`scripts/dev/tmux_session.sh`
- Lnav 辅助脚本：`scripts/lnav-monitor.sh`
- 监控脚本：`scripts/dev/automation/monitor_and_fix.py`
- Lnav 格式：`config/lnav_formats.json`

---

**最后更新**: 2026-02-24  
**文档维护**: MyStocks 开发团队
