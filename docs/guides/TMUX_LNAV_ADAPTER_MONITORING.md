# tmux + lnav 适配器调用日志监控方案

## 一、方案概述

**核心逻辑**: 借助系统已安装的 tmux（分屏并行）和 lnav（日志高效分析），以"极简日志埋点为基础、工具能力为核心"，快速实现适配器调用的可观测性。

**核心价值**:
- 零成本落地：复用已安装的 tmux 和 lnav
- 效率翻倍：问题排查从"小时级"压缩到"分钟级"
- 无侵入性：日志埋点极简，不影响系统性能

---

## 二、实施步骤

### 第一步：结构化日志埋点（已完成）

**文件**: `src/database/database_service.py`

**日志格式** (用 `|` 分隔，lnav 可解析):
```
ADAPTER_CALL|2026-01-27T12:00:00.123456|akshare|get_stock_daily|params={'symbol': '600000'}|status=SUCCESS|duration_ms=45.67
ADAPTER_CALL|2026-01-27T12:00:01.234567|tdx|get_realtime_quotes|params={'symbols': ['600000']}|status=FAIL|error=Connection timeout|duration_ms=3000.00
```

**日志字段**:
| 字段 | 说明 | 示例 |
|------|------|------|
| 时间戳 | ISO格式 | 2026-01-27T12:00:00.123456 |
| 适配器类型 | adapter_type | akshare, tdx, baostock... |
| 方法名 | method | get_stock_daily, get_realtime_quotes... |
| 参数摘要 | 截取前200字符 | params={'symbol': '600000'} |
| 状态 | SUCCESS/FAIL | SUCCESS |
| 耗时 | 毫秒 | 45.67 |
| 错误信息 | FAIL时才有 | Connection timeout |

---

### 第二步：tmux 分屏操作

#### 2.1 启动 tmux 会话
```bash
# 创建专用会话
tmux new -s adapter_log

# 后续恢复会话
tmux attach -t adapter_log
```

#### 2.2 分屏布局
```bash
# 在 tmux 会话中：
Ctrl+b %    # 左右分屏（左屏运行系统，右屏看日志）
Ctrl+b 方向键  # 切换分屏
```

#### 2.3 分屏任务分配

**左屏 - 运行系统**:
```bash
# 启动后端服务
cd /opt/claude/mystocks_spec/web/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 或运行其他脚本
python scripts/runtime/run_realtime_market_saver.py
```

**右屏 - 实时跟踪日志**:
```bash
# 跟踪适配器调用日志（推荐）
tail -f /tmp/backend.log | grep "ADAPTER_CALL"

# 或过滤特定适配器
tail -f /tmp/backend.log | grep "ADAPTER_CALL" | grep "akshare"

# 实时查看所有日志（需要先配置日志文件）
lnav -f /var/log/mystocks_adapter.log
```

#### 2.4 会话管理
```bash
Ctrl+b d        # detach 会话（保留状态）
tmux ls         # 查看所有会话
tmux kill-session -t adapter_log  # 删除会话
```

---

### 第三步：lnav 日志分析操作

#### 3.1 启动 lnav
```bash
# 进入日志目录
cd /opt/claude/mystocks_spec/logs

# 启动 lnav
lnav backend.log

# 或实时跟踪
lnav -f /tmp/backend.log
```

#### 3.2 高频操作

**搜索"调用失败"的日志**:
```
# 在 lnav 中：
/调用失败
n   # 看下一条
N   # 看上一条
```

**只看"akshare"适配器日志**:
```
:filter-in ADAPTER_CALL.*akshare
:filter-clear   # 取消过滤
```

**统计各适配器调用成功率**:
```
:aggregate -c count() -g adapter_type,method,status
```

**找耗时最长的调用**:
```
:sort -k duration_ms:-r
```

**按时间范围过滤**:
```
:filter-between-time 12:00:00 12:30:00
```

#### 3.3 退出 lnav
```
q   # 直接退出
```

---

## 三、tmux + lnav 联合工作流

### 完整操作流程

```bash
# 1. 启动 tmux 会话
tmux new -s adapter_log

# 2. 分屏
Ctrl+b %

# 3. 左屏：启动系统
# (手动切换到左屏，运行服务)
cd /opt/claude/mystocks_spec/web/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 4. 右屏：启动 lnav 实时分析
# (切换到右屏)
cd /opt/claude/mystocks_spec/logs
lnav -f /tmp/backend.log

# 5. 在 lnav 中执行分析操作：
#   - 按 / 搜索关键词
#   - 按 : 执行命令（如 filter-in, aggregate）
#   - 按 q 退出

# 6. 完成后 detach
Ctrl+b d
```

---

## 四、实战场景

### 场景1：开发阶段实时监控

```bash
# 左屏运行服务
python -m uvicorn app.main:app --reload

# 右屏实时查看适配器调用
tail -f /tmp/backend.log | grep "ADAPTER_CALL" | awk -F'|' '{print $3, $4, $6}'
```

**输出示例**:
```
akshare get_stock_daily SUCCESS
tdx get_realtime_quotes SUCCESS
baostock get_stock_daily FAIL
```

### 场景2：测试阶段统计成功率

```bash
# 在 lnav 中执行：
:filter-in ADAPTER_CALL
:aggregate -c count() -g adapter_type,status
```

**输出示例**:
```
adapter_type | status  | count
------------|---------|------
akshare     | SUCCESS | 145
akshare     | FAIL    | 3
tdx         | SUCCESS | 89
tdx         | FAIL    | 12
```

### 场景3：线上故障排查

```bash
# 快速定位失败调用
:filter-in ADAPTER_CALL.*FAIL
:sort -k time:-r

# 查看具体错误
# (高亮显示错误日志，一目了然)
```

---

## 五、注意事项

### 5.1 日志格式要点
- ✅ 分隔符统一用 `|`
- ✅ 关键字段位置固定（adapter_type, method, status）
- ✅ 参数摘要限制 200 字符以内
- ✅ 时间戳使用 ISO 格式

### 5.2 lnav 快捷键速查

| 操作 | 快捷键 |
|------|--------|
| 搜索 | `/关键词` |
| 下一条搜索结果 | `n` |
| 上一条搜索结果 | `N` |
| 进入命令模式 | `:` |
| 取消过滤 | `:filter-clear` |
| 按时间过滤 | `:filter-between-time HH:MM:SS HH:MM:SS` |
| 退出 | `q` |

### 5.3 tmux 快捷键速查

| 操作 | 快捷键 |
|------|--------|
| 分屏（左右） | `Ctrl+b %` |
| 分屏（上下） | `Ctrl+b "` |
| 切换分屏 | `Ctrl+b 方向键` |
| 调整分屏大小 | `Ctrl+b Ctrl+方向键` |
| detach 会话 | `Ctrl+b d` |
| 列出会话 | `tmux ls` |

---

## 六、进阶技巧

### 6.1 日志文件配置（可选）

如果需要将适配器日志单独输出到文件，在 `logging.conf` 中添加：

```ini
[handler_adapter_handler]
class = FileHandler
args = ("/opt/claude/mystocks_spec/logs/adapter.log", "a")
formatter = adapter_formatter

[formatter_adapter_formatter]
format = %(message)s
datefmt = %Y-%m-%dT%H:%M:%S
```

### 6.2 常用 lnav 命令脚本

创建 `~/.lnav/commands/mystocks.sql`:

```sql
-- 适配器调用统计
:aggregate -c count() -g $4, $6;

-- 失败调用统计
:filter-in ADAPTER_CALL.*FAIL;

-- 最慢调用 TOP 10
:sort -k duration_ms:-r
:head 10;
```

然后在 lnav 中执行：
```
:mystocks.sql
```

---

## 七、总结

**核心优势**:
1. **零成本**: 复用 tmux + lnav，不额外部署
2. **高效率**: tmux 分屏省去终端切换，lnav 分析快准狠
3. **易上手**: 记住几个快捷键就能覆盖 90% 场景

**最佳实践**:
- 开发时：左屏跑服务，右屏开 lnav，调用立刻可见
- 测试时：lnav 过滤统计，快速判断适配器健康度
- 故障时：/FAIL + sort，快速定位慢调用和错误

---

## 八、相关文档

- lnav 官方文档: https://lnav.org/
- tmux 快速入门: https://tmuxcheatsheet.com/
