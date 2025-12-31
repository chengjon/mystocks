# lnav 日志分析集成指南

## 概述

本指南介绍如何在 MyStocks 项目中使用 lnav 进行实时日志分析和自动化测试日志分析。

## lnav 简介

lnav 是一个高级日志文件查看器，提供：
- 实时日志监控
- 高级筛选和搜索
- SQL 查询支持
- 性能分析
- 自动格式解析

## 安装检查

```bash
# 检查 lnav 是否已安装
which lnav

# 查看版本
lnav --version
```

## 日志目录结构

```
logs/
├── api/              # API 测试日志
├── e2e/              # E2E 测试日志
├── frontend/         # 前端日志
├── backend/          # 后端日志
└── database/         # 数据库日志
```

## 快速开始

### 1. 监控所有日志

```bash
./scripts/lnav-monitor.sh all
```

### 2. 仅监控错误日志

```bash
./scripts/lnav-monitor.sh errors
```

### 3. 仅监控 API 测试日志

```bash
./scripts/lnav-monitor.sh api
```

### 4. 监控性能日志（响应时间 > 1s）

```bash
./scripts/lnav-monitor.sh performance
```

## lnav 常用命令

### 基本操作

| 快捷键 | 功能 |
|--------|------|
| `q` | 退出 |
| `/` | 搜索 |
| `n` | 下一个匹配 |
| `N` | 上一个匹配 |
| `?` | 向上搜索 |

### 筛选命令

| 命令 | 功能 |
|------|------|
| `:filter-in <expr>` | 筛选包含表达式的行 |
| `:filter-out <expr>` | 排除包含表达式的行 |
| `:filter-reset` | 重置所有筛选 |

### 统计命令

| 命令 | 功能 |
|------|------|
| `:stats` | 显示统计信息 |
| `:pie-chart` | 显示饼图 |
| `:bar-chart` | 显示柱状图 |

### SQL 查询

| 命令 | 功能 |
|------|------|
| `:db SELECT * FROM log_file WHERE log_level = 'ERROR'` | 查询错误日志 |
| `:db SELECT log_level, COUNT(*) FROM log_file GROUP BY log_level` | 统计日志级别 |
| `:db SELECT * FROM log_file ORDER BY timestamp DESC LIMIT 10` | 最近10条日志 |

## 高级筛选示例

### 按模块筛选

```bash
# 在 lnav 中执行
:filter-in module = 'frontend'
:filter-in module = 'backend'
:filter-in module = 'api'
```

### 按 API 路径筛选

```bash
# 在 lnav 中执行
:filter-in path = '/api/auth/login'
:filter-in path LIKE '/api/market/%'
```

### 按响应时间筛选

```bash
# 在 lnav 中执行
:filter-in response_time > 1000
:filter-in response_time BETWEEN 500 AND 1000
```

### 按错误类型筛选

```bash
# 在 lnav 中执行
:filter-in log_level IN ('ERROR', 'CRITICAL')
```

## 自动化测试日志分析

### 完整分析

```bash
./scripts/analyze-test-logs.sh analyze
```

这将生成以下分析：
- 错误分析（按模块统计）
- 性能分析（响应时间、慢请求）
- 测试覆盖率

### 仅分析错误

```bash
./scripts/analyze-test-logs.sh errors
```

### 仅分析性能

```bash
./scripts/analyze-test-logs.sh performance
```

### 仅分析覆盖率

```bash
./scripts/analyze-test-logs.sh coverage
```

### 生成报告

```bash
./scripts/analyze-test-logs.sh report
```

### 清空日志

```bash
./scripts/analyze-test-logs.sh clear
```

## 导出日志

### 导出为 JSON

```bash
./scripts/lnav-monitor.sh export json
```

### 导出为 CSV

```bash
./scripts/lnav-monitor.sh export csv
```

### 导出为 HTML

```bash
./scripts/lnav-monitor.sh export html
```

## 日志格式配置

### API 测试日志格式

```json
{
  "timestamp": "2024-12-30 12:00:00.000",
  "log_level": "INFO",
  "test_case_id": "CASE-AUTH-001",
  "module": "api",
  "endpoint": "/api/auth/login",
  "method": "POST",
  "status_code": 200,
  "response_time": 150,
  "message": "测试通过"
}
```

### 高亮规则

已配置以下高亮规则：
- 错误关键词（红色）：`ERROR`, `CRITICAL`, `Exception`, `Traceback`
- 警告关键词（黄色）：`WARNING`, `WARN`, `Deprecated`
- 成功关键词（绿色）：`SUCCESS`, `PASSED`, `✓`, `OK`, `200`, `201`
- 测试用例ID（青色）：`CASE-[A-Z0-9-]+`
- HTTP状态码（品红）：`40[0-9]`, `50[0-9]`
- 数据库错误（红色）：`Connection refused`, `database error`, `SQL.*error`

## 常见场景

### 场景1：查找所有API错误

```bash
./scripts/lnav-monitor.sh errors

# 在 lnav 中执行
:filter-in log_level = 'ERROR'
:filter-in endpoint LIKE '/api/%'
```

### 场景2：查找慢API请求

```bash
./scripts/lnav-monitor.sh api

# 在 lnav 中执行
:filter-in response_time > 1000
```

### 场景3：统计测试失败数量

```bash
./scripts/analyze-test-logs.sh errors

# 或在 lnav 中执行
:filter-in log_level = 'ERROR'
:stats
```

### 场景4：监控特定测试用例

```bash
./scripts/lnav-monitor.sh api

# 在 lnav 中执行
:filter-in test_case_id = 'CASE-AUTH-001'
```

### 场景5：分析认证模块性能

```bash
./scripts/lnav-monitor.sh api

# 在 lnav 中执行
:filter-in endpoint LIKE '/api/auth/%'
:db SELECT AVG(response_time), MAX(response_time), MIN(response_time) FROM log_file
```

## 集成到测试流程

### 在测试执行期间启动监控

```bash
# 终端1：启动服务
cd web/backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 终端2：启动日志监控
./scripts/lnav-monitor.sh api

# 终端3：运行测试
./scripts/run-api-tests.sh all

# 终端4：分析日志
./scripts/analyze-test-logs.sh analyze
```

### 使用 tmux 多窗口环境

```bash
# 启动 tmux 测试环境
./scripts/start-system.sh --tmux

# 在窗口2（日志监控）中执行
:filter-in log_level IN ('ERROR', 'CRITICAL')
```

## 报告输出

分析完成后，将在 `logs/` 目录下生成以下文件：
- `test_analysis.log` - 完整的分析日志
- `errors.log` - 错误详情
- `performance.log` - 性能数据
- `summary.log` - 汇总报告

## 注意事项

1. 日志文件大小：建议定期清理，避免占用过多磁盘空间
2. 性能影响：实时监控会对系统性能产生轻微影响
3. 筛选性能：复杂的筛选条件可能会影响响应速度
4. 内存使用：分析大日志文件时可能占用较多内存

## 故障排查

### 问题：lnav 无法启动

```bash
# 检查 lnav 是否安装
which lnav

# 安装 lnav
sudo apt-get install lnav  # Ubuntu/Debian
brew install lnav           # macOS
```

### 问题：日志文件为空

```bash
# 检查日志目录权限
ls -la logs/

# 检查日志文件是否正在被写入
tail -f logs/api/*.log
```

### 问题：筛选不生效

```bash
# 重置筛选
:filter-reset

# 检查表达式语法
:help filter
```

## 参考资源

- lnav 官方文档：http://lnav.org/
- lnav 快捷键：在 lnav 中执行 `:help`
- lnav SQL 查询：在 lnav 中执行 `:help sql`
