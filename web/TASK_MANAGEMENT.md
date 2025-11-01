# MyStocks 任务管理系统说明文档

## 目录
1. [概述](#概述)
2. [系统架构](#系统架构)
3. [核心功能](#核心功能)
4. [任务配置](#任务配置)
5. [使用指南](#使用指南)
6. [API接口](#api接口)
7. [最佳实践](#最佳实践)
8. [故障排查](#故障排查)

---

## 概述

MyStocks任务管理系统是一个完整的分布式任务调度和执行框架，用于自动化处理股票数据采集、指标计算、策略回测等周期性任务。

### 主要特性

- ✅ **多种任务类型支持**: 定时任务、数据同步、指标计算、市场数据获取等
- ✅ **灵活的调度策略**: 支持Cron表达式、固定间隔、一次性任务
- ✅ **完善的监控体系**: 实时任务状态、执行历史、统计分析
- ✅ **任务依赖管理**: 支持任务间的依赖关系和顺序执行
- ✅ **错误处理机制**: 自动重试、失败告警、日志记录
- ✅ **Web管理界面**: 可视化任务管理、配置和监控

---

## 系统架构

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      Web管理界面                              │
│  (任务列表、执行历史、统计分析、配置管理)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ RESTful API
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    FastAPI后端                                │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ 任务管理器   │  │  任务调度器   │  │  任务执行器   │       │
│  │TaskManager  │  │TaskScheduler │  │Task Executor │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                         │
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    任务实现层                                 │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ 数据同步     │  │  指标计算     │  │  市场数据     │       │
│  │data_sync    │  │indicators    │  │market_data   │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### 核心组件

#### 1. TaskManager (任务管理器)
- 任务注册和注销
- 任务执行和控制
- 执行记录管理
- 统计信息收集

#### 2. TaskScheduler (任务调度器)
- 基于APScheduler实现
- 支持多种调度策略
- 任务暂停/恢复
- 错过任务处理

#### 3. Task Executor (任务执行器)
- 异步任务执行
- 超时控制
- 重试机制
- 结果收集

---

## 核心功能

### 1. 任务类型

系统支持以下任务类型：

| 类型 | 说明 | 典型场景 |
|------|------|----------|
| `cron` | 定时任务 | 每日数据同步、每月维护 |
| `supervisor` | 进程管理任务 | Web服务、后台服务 |
| `manual` | 手动任务 | 一次性数据导入、回测 |
| `data_sync` | 数据同步任务 | 股票数据、财务数据同步 |
| `indicator_calc` | 指标计算任务 | 技术指标、策略信号计算 |
| `market_fetch` | 市场数据获取 | 龙虎榜、资金流向 |

### 2. 调度策略

#### Cron表达式
```yaml
schedule:
  schedule_type: "cron"
  cron_expression: "0 16 * * 1-5"  # 工作日下午4点
  enabled: true
```

**常用Cron表达式：**
- `0 0 * * *` - 每天零点
- `0 * * * *` - 每小时
- `*/5 * * * *` - 每5分钟
- `0 9-17 * * 1-5` - 工作日9点到17点整点

#### 固定间隔
```yaml
schedule:
  schedule_type: "interval"
  interval_seconds: 3600  # 每小时
  enabled: true
```

#### 一次性任务
```yaml
schedule:
  schedule_type: "once"
  start_time: "2025-10-17T09:00:00"
  enabled: true
```

### 3. 任务优先级

| 优先级 | 数值 | 说明 |
|--------|------|------|
| 关键 | 100 | 最高优先级，立即执行 |
| 高 | 200 | 高优先级 |
| 普通 | 500 | 默认优先级 |
| 低 | 800 | 低优先级 |
| 批处理 | 900 | 最低优先级 |

### 4. 任务依赖

支持任务间的依赖关系：

```yaml
dependencies:
  - "sync_basic_stock_info"  # 必须先执行此任务
  - "calc_technical_indicators"
```

### 5. 错误处理

```yaml
timeout: 3600           # 超时时间(秒)
retry_count: 3          # 重试次数
retry_delay: 300        # 重试延迟(秒)
auto_restart: false     # 是否自动重启
stop_on_error: true     # 错误时停止
```

---

## 任务配置

### 配置文件位置
```
/opt/claude/mystocks_spec/web/backend/config/tasks.yaml
```

### 配置示例

```yaml
tasks:
  - task_id: "daily_data_sync"
    task_name: "每日股票数据同步"
    task_type: "cron"
    task_module: "app.tasks.data_sync"
    task_function: "sync_daily_stock_data"
    description: "每天收盘后同步当日股票交易数据"
    priority: 200

    schedule:
      schedule_type: "cron"
      cron_expression: "0 16 * * 1-5"
      enabled: true

    params:
      data_source: "akshare"
      include_basic: true
      include_kline: true

    timeout: 3600
    retry_count: 3
    retry_delay: 300

    tags:
      - "daily"
      - "data_sync"
      - "important"
```

### 任务组配置

批量管理相关任务：

```yaml
task_groups:
  - group_id: "daily_job"
    group_name: "每日数据处理任务组"
    tasks:
      - "daily_data_sync"
      - "calc_technical_indicators"
      - "calc_strategy_signals"
    execution_mode: "sequential"  # 顺序执行
    enabled: true
```

---

## 使用指南

### 1. Web界面使用

#### 访问任务管理页面
```
http://localhost:3001/tasks
```

#### 主要功能
1. **任务列表**: 查看所有已注册任务
2. **任务操作**: 启动、停止、编辑、删除任务
3. **执行历史**: 查看任务执行记录
4. **统计分析**: 任务成功率、平均耗时等统计

#### 新建任务
1. 点击"新建任务"按钮
2. 填写任务基本信息
3. 配置调度策略
4. 设置高级选项
5. 提交保存

### 2. API接口使用

#### 注册任务
```bash
curl -X POST http://localhost:8888/api/tasks/register \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "test_task",
    "task_name": "测试任务",
    "task_type": "manual",
    "task_module": "app.tasks.data_sync",
    "task_function": "sync_daily_stock_data",
    "priority": 500,
    "timeout": 300
  }'
```

#### 启动任务
```bash
curl -X POST http://localhost:8888/api/tasks/test_task/start
```

#### 查询任务状态
```bash
curl http://localhost:8888/api/tasks/test_task
```

#### 查看执行历史
```bash
curl http://localhost:8888/api/tasks/executions/?task_id=test_task
```

### 3. Python代码使用

#### 注册和执行任务
```python
from app.services.task_manager import task_manager
from app.models.task import TaskConfig, TaskType, TaskPriority

# 创建任务配置
task_config = TaskConfig(
    task_id="my_task",
    task_name="我的任务",
    task_type=TaskType.MANUAL,
    task_module="app.tasks.data_sync",
    task_function="sync_daily_stock_data",
    priority=TaskPriority.NORMAL,
    params={"data_source": "akshare"},
    timeout=600
)

# 注册任务
response = task_manager.register_task(task_config)

# 启动任务
await task_manager.start_task("my_task")
```

#### 注册任务函数
```python
from app.services.task_manager import task_manager

def my_custom_task(params):
    """自定义任务函数"""
    print(f"Executing with params: {params}")
    return {"status": "success"}

# 注册函数
task_manager.register_function("my_custom_task", my_custom_task)
```

### 4. 创建新任务

#### 步骤1: 编写任务函数

在 `app/tasks/` 目录下创建任务实现：

```python
# app/tasks/my_tasks.py

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

def my_data_process_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    自定义数据处理任务

    Args:
        params: 任务参数

    Returns:
        执行结果字典
    """
    logger.info(f"Starting task with params: {params}")

    try:
        # 实现任务逻辑
        result = {
            'status': 'success',
            'processed_records': 1000,
            'execution_time': datetime.now().isoformat()
        }

        logger.info(f"Task completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Task failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }
```

#### 步骤2: 添加到配置文件

在 `config/tasks.yaml` 中添加任务配置：

```yaml
- task_id: "my_data_process"
  task_name: "自定义数据处理"
  task_type: "manual"
  task_module: "app.tasks.my_tasks"
  task_function: "my_data_process_task"
  description: "处理自定义数据"
  priority: 500
  params:
    source: "database"
    batch_size: 1000
  timeout: 1800
  retry_count: 2
```

#### 步骤3: 注册和测试

```python
from app.services.task_manager import task_manager
from app.tasks.my_tasks import my_data_process_task

# 注册函数
task_manager.register_function("my_data_process_task", my_data_process_task)

# 导入配置
task_manager.import_config("config/tasks.yaml")

# 测试执行
await task_manager.start_task("my_data_process")
```

---

## API接口

### 任务管理接口

#### 1. 注册任务
```
POST /api/tasks/register
Content-Type: application/json

Request Body: TaskConfig对象
Response: TaskResponse对象
```

#### 2. 获取任务列表
```
GET /api/tasks/
Query Parameters:
  - task_type: 任务类型 (可选)
  - tags: 标签，逗号分隔 (可选)

Response: List[TaskConfig]
```

#### 3. 获取任务详情
```
GET /api/tasks/{task_id}

Response: TaskConfig对象
```

#### 4. 启动任务
```
POST /api/tasks/{task_id}/start
Content-Type: application/json

Request Body: {"params": {...}}  (可选)
Response: TaskResponse对象
```

#### 5. 停止任务
```
POST /api/tasks/{task_id}/stop

Response: TaskResponse对象
```

#### 6. 删除任务
```
DELETE /api/tasks/{task_id}

Response: TaskResponse对象
```

### 执行历史接口

#### 7. 获取执行历史
```
GET /api/tasks/executions/
Query Parameters:
  - task_id: 任务ID (可选)
  - limit: 返回数量限制 (默认100)

Response: List[TaskExecution]
```

#### 8. 获取执行详情
```
GET /api/tasks/executions/{execution_id}

Response: TaskExecution对象
```

#### 9. 清理执行历史
```
DELETE /api/tasks/executions/cleanup
Query Parameters:
  - days: 保留天数 (默认7)

Response: {success: true, count: N}
```

### 统计接口

#### 10. 获取统计信息
```
GET /api/tasks/statistics/
Query Parameters:
  - task_id: 任务ID (可选)

Response: Dict[str, TaskStatistics]
```

### 配置管理接口

#### 11. 导入配置
```
POST /api/tasks/import
Content-Type: application/json

Request Body: {"config_path": "/path/to/config.yaml"}
Response: TaskResponse对象
```

#### 12. 导出配置
```
POST /api/tasks/export
Content-Type: application/json

Request Body: {"output_path": "/path/to/output.json"}
Response: {success: true, path: "..."}
```

#### 13. 健康检查
```
GET /api/tasks/health

Response: {
  status: "healthy",
  total_tasks: N,
  running_tasks: M,
  total_executions: K
}
```

---

## 最佳实践

### 1. 任务设计原则

#### 幂等性
确保任务可以安全地重复执行：
```python
def sync_data_task(params):
    # 先删除旧数据，再插入新数据
    delete_old_data(date=params['date'])
    insert_new_data(date=params['date'])
```

#### 超时设置
根据任务复杂度设置合理的超时时间：
- 简单任务: 300秒
- 中等任务: 1800秒
- 复杂任务: 3600秒以上

#### 错误处理
始终捕获异常并返回有意义的错误信息：
```python
try:
    # 任务逻辑
    result = process_data()
    return {'status': 'success', 'data': result}
except SpecificException as e:
    logger.error(f"Specific error: {e}")
    return {'status': 'failed', 'error': str(e)}
```

### 2. 调度配置建议

#### 避免高峰期
```yaml
# 避开交易时段
cron_expression: "0 16 * * 1-5"  # 收盘后执行
```

#### 合理设置重试
```yaml
retry_count: 3
retry_delay: 300  # 5分钟后重试
```

#### 任务依赖管理
```yaml
# 确保依赖任务已完成
dependencies:
  - "sync_basic_data"
```

### 3. 监控和维护

#### 定期检查执行历史
```bash
# 查看失败任务
curl http://localhost:8888/api/tasks/executions/ | jq '.[] | select(.status == "failed")'
```

#### 清理旧记录
```bash
# 每周清理一次
curl -X DELETE "http://localhost:8888/api/tasks/executions/cleanup?days=7"
```

#### 导出配置备份
```bash
# 定期备份配置
curl -X POST http://localhost:8888/api/tasks/export \
  -H "Content-Type: application/json" \
  -d '{"output_path": "/backup/tasks_$(date +%Y%m%d).json"}'
```

### 4. 性能优化

#### 并行执行独立任务
使用任务组的parallel模式：
```yaml
task_groups:
  - group_id: "parallel_fetch"
    execution_mode: "parallel"
    tasks:
      - "fetch_lhb_data"
      - "fetch_capital_flow"
```

#### 批量处理数据
```python
def batch_process_task(params):
    batch_size = params.get('batch_size', 1000)
    for batch in get_batches(batch_size):
        process_batch(batch)
```

---

## 故障排查

### 常见问题

#### 1. 任务执行失败

**症状**: 任务状态显示为"failed"

**排查步骤**:
1. 查看执行历史中的错误信息
2. 检查任务日志文件
3. 验证任务参数是否正确
4. 确认依赖服务是否正常

**解决方案**:
```bash
# 查看详细错误
curl http://localhost:8888/api/tasks/executions/{execution_id}

# 手动重新执行
curl -X POST http://localhost:8888/api/tasks/{task_id}/start
```

#### 2. 任务超时

**症状**: 任务执行时间过长，被强制终止

**排查步骤**:
1. 检查timeout配置是否合理
2. 分析任务是否存在性能瓶颈
3. 查看数据库连接状态

**解决方案**:
```yaml
# 增加超时时间
timeout: 7200  # 改为2小时

# 或优化任务逻辑，减少执行时间
```

#### 3. 调度器不工作

**症状**: 定时任务没有按时执行

**排查步骤**:
1. 检查调度器是否启动
2. 验证Cron表达式是否正确
3. 查看系统时间是否准确

**解决方案**:
```bash
# 检查健康状态
curl http://localhost:8888/api/tasks/health

# 重启调度器
# (在应用启动时自动启动)
```

#### 4. 内存泄漏

**症状**: 长时间运行后内存占用持续增长

**排查步骤**:
1. 检查执行历史记录数量
2. 查看是否有大量未清理的临时数据

**解决方案**:
```bash
# 定期清理执行历史
curl -X DELETE "http://localhost:8888/api/tasks/executions/cleanup?days=7"
```

### 日志分析

#### 查看任务日志
```bash
# 后端日志
tail -f /tmp/mystocks_tasks/*.log

# 应用日志
tail -f /tmp/backend.log | grep "task"
```

#### 日志级别
```python
# 调整日志级别
import logging
logging.getLogger('app.tasks').setLevel(logging.DEBUG)
```

---

## 附录

### A. 完整配置示例

参见: `/opt/claude/mystocks_spec/web/backend/config/tasks.yaml`

### B. API数据模型

详见后端代码: `/opt/claude/mystocks_spec/web/backend/app/models/task.py`

### C. 相关文件路径

```
web/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── tasks.py              # API路由
│   │   ├── models/
│   │   │   └── task.py               # 数据模型
│   │   ├── services/
│   │   │   ├── task_manager.py       # 任务管理器
│   │   │   └── task_scheduler.py     # 任务调度器
│   │   └── tasks/
│   │       ├── data_sync.py          # 数据同步任务
│   │       └── market_data.py        # 市场数据任务
│   └── config/
│       └── tasks.yaml                # 任务配置文件
└── frontend/
    ├── src/
    │   ├── views/
    │   │   └── TaskManagement.vue    # 任务管理页面
    │   └── components/
    │       └── task/
    │           ├── TaskTable.vue     # 任务表格组件
    │           ├── TaskForm.vue      # 任务表单组件
    │           └── ExecutionHistory.vue  # 执行历史组件
    └── router/
        └── index.js                  # 路由配置
```

### D. 技术栈

- **后端框架**: FastAPI
- **任务调度**: APScheduler
- **数据验证**: Pydantic
- **前端框架**: Vue 3 + Element Plus
- **状态管理**: Pinia
- **HTTP客户端**: Axios

---

## 更新日志

### v1.0.0 (2025-10-16)
- ✅ 初始版本发布
- ✅ 完整的任务管理功能
- ✅ Web管理界面
- ✅ RESTful API
- ✅ 任务调度器集成
- ✅ 示例任务实现

---

**文档维护**: MyStocks开发团队
**最后更新**: 2025-10-16
**版本**: 1.0.0
