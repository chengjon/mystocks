<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# MyStocks 项目开发指南

本指南帮助 Claude Code 实例高效地工作在 MyStocks 量化交易平台。

## 快速开始命令

### 前端开发
```bash
# 启动 Vue.js 前端（端口 3000-3009）
cd web/frontend
npm install
npm run dev -- --port 3000

# 生产环境构建
npm run build

# 运行代码检查
npm run lint

# 运行 E2E 测试
npx playwright test
```

### 后端开发
```bash
# 启动 FastAPI 后端（端口 8000-8009）
cd web/backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 运行测试
pytest

# 查看 API 文档
# http://localhost:8000/docs
```

### 全栈开发
```bash
# 同时启动两个服务
终端 1: cd web/backend && python -m uvicorn main:app --port 8000
终端 2: cd web/frontend && npm run dev -- --port 3000
```

## 项目架构

### 高层结构
```
mystocks_spec/
├── web/                    # Web 应用
│   ├── frontend/          # Vue.js 3 + TypeScript 前端
│   │   ├── src/
│   │   │   ├── components/  # Vue 组件
│   │   │   ├── views/      # 页面组件
│   │   │   ├── utils/      # 工具模块（适配器、缓存、SSE 等）
│   │   │   ├── stores/     # Pinia 状态管理
│   │   │   └── api/        # API 服务层
│   │   ├── tests/          # E2E 测试（Playwright）
│   │   └── package.json
│   └── backend/           # FastAPI Python 后端
│       ├── app/           # 应用代码
│       ├── main.py        # 应用入口
│       └── requirements.txt
├── src/                   # 核心 Python 后端（Motia/量化系统）
│   ├── core/            # 核心业务逻辑
│   ├── adapters/        # 数据源适配器
│   ├── data_access/     # 数据库访问层
│   ├── monitoring/      # 监控和告警
│   └── steps/           # Motia 工作流步骤
├── docs/                # 文档
│   ├── api/            # API 文档
│   ├── guides/         # 用户指南
│   └── reports/        # 项目报告
└── scripts/            # 工具脚本
    ├── runtime/        # 生产脚本
    └── tests/          # 测试脚本
```

### 核心架构模式

1. **双数据库架构**：
   - **PostgreSQL**: 日线数据、参考数据、交易数据
   - **TDengine**: 高频时序数据（tick/分钟）
   - 通过 `table_config.yaml` 进行配置驱动的表管理

2. **适配器模式**: 统一多个数据源的访问（akshare、baostock、tushare 等）

3. **模式优先开发**: Pydantic 模型作为单一数据源

4. **API-Web 组件对齐**: 前端适配器将 API 响应转换为视图模型

## 重要实现模式

### 前端工具架构 (src/utils/)

前端使用复杂的工具架构：

1. **HTTP 客户端** (`request.ts`):
   - 统一的 Axios 实例，支持 CSRF 保护
   - 请求/响应拦截器
   - 自动令牌管理

2. **数据适配器** (`*-adapters.ts`):
   - 将 API 响应转换为 UI 友好的视图模型
   - 处理数据格式化和验证
   - 模块：`adapters.ts`、`strategy-adapters.ts`、`trade-adapters.ts`、`monitoring-adapters.ts`、`user-adapters.ts`

3. **智能缓存** (`cache.ts`):
   - 支持 TTL 的 LRU 缓存
   - localStorage 持久化
   - 依赖管理

4. **实时更新** (`sse.ts`):
   - 服务器推送事件，支持自动重连
   - 事件过滤和多路复用
   - 连接健康监控

5. **性能优化** (`performance.ts`):
   - 懒加载和代码分割
   - 图片优化
   - 节流和防抖

6. **错误边界** (`error-boundary.ts`):
   - Vue 错误捕获和报告
   - 全局错误处理
   - 恢复策略

### 类型生成管道

```bash
# 从 Python Pydantic 模型生成 TypeScript 类型
python scripts/generate_frontend_types.py
```

这会创建 `web/frontend/src/types/api.ts`，包含与后端模型匹配的 TypeScript 接口。

### Mock 数据使用

**重要**: 绝不在组件中硬编码 mock 数据。始终使用 mock 数据模块：

```python
# ✅ 正确：使用工厂模式
from src.data_sources.factory import get_timeseries_source
source = get_timeseries_source(source_type="mock")
data = source.get_kline_data(symbol, start_time, end_time)

# ❌ 错误：硬编码数据
historical_data = [{"date": "2025-01-01", "close": 10.5}]  # 禁止！
```

## 测试策略

### E2E 测试 (Playwright)
```bash
# 运行 E2E 测试
cd web/frontend
npx playwright test

# 运行特定测试文件
npx playwright test tests/realtime-monitor.spec.ts

# 以有头模式运行测试
npx playwright test --headed
```

### 后端测试
```bash
# 运行所有测试
pytest

# 运行覆盖率测试
pytest --cov=app

# 运行特定测试
pytest tests/test_api.py
```

## 端口分配规则

**强制要求**: 仅使用分配的端口范围：

- **前端**: 3000-3009（Vite 开发服务器）
- **后端**: 8000-8009（FastAPI）
- **E2E 测试**: 必须连接到允许范围内的前端

### 端口验证
测试会自动验证端口是否在允许范围内：
```javascript
// 如果端口超出允许范围，E2E 测试将失败
if (!['3000','3001','3002','3003','3004','3005','3006','3007','3008','3009'].includes(frontendPort)) {
  throw new Error(`前端端口 ${frontendPort} 不在允许范围内 (3000-3009)`);
}
```

## API 文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Apifox 项目**: https://app.apifox.com/project/7376246

## 关键配置文件

1. **前端**:
   - `vite.config.js`: Vite 配置和代理设置
   - `playwright.config.ts`: E2E 测试配置
   - `package.json`: 依赖和脚本

2. **后端**:
   - `requirements.txt`: Python 依赖
   - `main.py`: FastAPI 应用入口
   - `.env`: 环境变量（不在 git 中）

3. **项目**:
   - `table_config.yaml`: 数据库模式定义
   - `.mcp.json`: MCP 服务器配置
   - `.claude/settings.json`: Claude Code 设置

## 开发工作流

### 1. 功能开发
1. 为重大变更创建 OpenSpec 提案：
   ```bash
   /openspec:proposal add-new-feature
   ```
2. 首先实现后端 API 端点
3. 从 Pydantic 模型生成 TypeScript 类型
4. 创建/更新前端适配器
5. 实现 Vue 组件
6. 添加 E2E 测试

### 2. API-Web 对齐
遵循 3 阶段方法：
- **阶段 1**: 基础设施和类型生成
- **阶段 2**: 核心模块适配器（市场、策略、交易、监控、用户）
- **阶段 3**: 高级功能（缓存、SSE、性能、错误边界）

### 3. 代码质量
- 前端：ESLint + Prettier
- 后端：Pylint（在 `.pylintrc` 中配置）
- 在 `.pre-commit-config.yaml` 中配置预提交钩子
- 测试：pytest（后端）、Playwright（E2E）

## 常见任务

### 添加新 API 端点
1. 在后端定义 Pydantic 模型
2. 创建 FastAPI 路由
3. 更新 OpenAPI 文档
4. 生成 TypeScript 类型
5. 创建前端适配器
6. 在 Vue 组件中实现

### 修复 E2E 测试失败
1. 检查选择器变化
2. 验证 API 响应
3. 更新测试断言
4. 提交前在本地运行测试

### 数据库模式变更
1. 更新 `table_config.yaml`
2. 使用 `ConfigDrivenTableManager` 应用更改
3. 更新相关的 Pydantic 模型
4. 重新生成 TypeScript 类型

## 故障排除

### 常见问题

1. **端口冲突**:
   ```bash
   # 检查端口使用情况
   lsof -i :3000
   lsof -i :8000

   # 终止进程
   kill -9 <PID>
   ```

2. **导入错误**:
   - 检查脚本中的 Python 路径：`os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))`
   - 验证虚拟环境激活

3. **类型不匹配**:
   - 重新生成类型：`python scripts/generate_frontend_types.py`
   - 检查适配器转换

4. **测试失败**:
   - 后端：检查数据库连接
   - 前端：验证 API 端点是否可访问
   - E2E：确保两个服务都在正确的端口上运行

## OpenSpec 集成

本项目使用 OpenSpec 进行规范驱动的开发：

- **创建提案**: `/openspec:proposal` 用于新功能
- **应用更改**: `/openspec:apply <change-id>` 进行实现
- **列出更改**: `/openspec list` 查看活动提案
- **验证**: 提交前运行 `openspec validate --strict`

查看 `@/openspec/AGENTS.md` 了解详细的 OpenSpec 工作流。

## Task Master 集成

用于任务管理和开发跟踪：

- **初始化**: `task-master init`
- **解析 PRD**: `task-master parse-prd .taskmaster/docs/prd.txt`
- **列出任务**: `task-master list`
- **下一个任务**: `task-master next`

查看 `@/.taskmaster/CLAUDE.md` 了解 Task Master 命令和工作流。

## 其他资源

- **项目路线图**: 查看 `docs/api/README.md` 了解已完成的阶段
- **阶段文档**: `docs/api/PHASE*_*.md` 了解实现细节
- **架构指南**: `docs/api/API与Web组件最终对齐方案.md`
- **错误处理**: `web/frontend/src/utils/error-boundary.ts`
- **性能指南**: `docs/api/PHASE3_IMPLEMENTATION_GUIDE.md`

## BUG上报规则和方法

### BUGer服务配置

MyStocks项目使用BUGer服务进行BUG管理和跟踪。

#### 环境配置
```bash
# 在 .env 文件中配置
BUGER_API_URL=http://localhost:3030/api
BUGER_API_KEY=sk_test_xyz123  # 开发环境
PROJECT_ID=mystocks
PROJECT_NAME=MyStocks
PROJECT_ROOT=/opt/claude/mystocks_spec
```

#### BUG上报方法

**1. 使用curl命令上报**
```bash
curl -X POST http://localhost:3030/api/bugs \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk_test_xyz123" \
  -d '{
    "errorCode": "ERROR_001",
    "title": "错误标题",
    "message": "详细错误描述",
    "severity": "high",
    "context": {
      "project_name": "MyStocks",
      "project_root": "/opt/claude/mystocks_spec",
      "component": "backend",
      "module": "模块名称",
      "file": "文件路径",
      "function": "函数名称"
    }
  }'
```

**2. Python客户端上报**
```python
import requests
import json
import os
from datetime import datetime

# 上报BUG
def report_bug(error_code, title, message, severity="medium", context=None):
    payload = {
        "errorCode": error_code,
        "title": title,
        "message": message,
        "severity": severity,
        "stackTrace": traceback.format_exc(),
        "context": {
            "timestamp": datetime.utcnow().isoformat(),
            "project": os.getenv("PROJECT_ID", "mystocks"),
            "project_name": os.getenv("PROJECT_NAME", "MyStocks"),
            "project_root": os.getenv("PROJECT_ROOT", "/opt/claude/mystocks_spec"),
            **(context or {})
        }
    }

    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': os.getenv('BUGER_API_KEY', 'sk_test_xyz123')
    }

    try:
        response = requests.post(
            f'{os.getenv("BUGER_API_URL", "http://localhost:3030/api")}/bugs',
            json=payload,
            headers=headers,
            timeout=10
        )
        print(f"✓ BUG 已上报: {response.json()['data']['bugId']}")
    except Exception as e:
        print(f"✗ BUG 上报失败: {e}")
        # 记录到本地备份文件
        with open('bug-reports-backup.jsonl', 'a') as f:
            f.write(json.dumps(payload) + '\n')
```

**3. JavaScript客户端上报**
```javascript
import axios from 'axios';
import dotenv from 'dotenv';
dotenv.config();

async function reportBug(errorCode, title, message, severity = 'medium', context = {}) {
  const payload = {
    errorCode,
    title,
    message,
    severity,
    stackTrace: error.stack || '',
    context: {
      timestamp: new Date().toISOString(),
      project: process.env.PROJECT_ID || 'mystocks',
      project_name: process.env.PROJECT_NAME || 'MyStocks',
      project_root: process.env.PROJECT_ROOT || '/opt/claude/mystocks_spec',
      ...context
    }
  };

  try {
    const response = await axios.post(
      `${process.env.BUGER_API_URL}/bugs`,
      payload,
      {
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': process.env.BUGER_API_KEY
        },
        timeout: 10000
      }
    );
    console.log(`✓ BUG 已上报: ${response.data.data.bugId}`);
  } catch (error) {
    console.error('✗ BUG 上报失败:', error.message);
    // 降级到本地日志
    logToFile(payload);
  }
}
```

#### BUG格式规范

**必需字段**:
- `errorCode`: 错误代码（大写字母、数字、下划线）
- `title`: 错误标题（≤50字符）
- `message`: 详细错误描述
- `severity`: 严重级别（critical/high/medium/low）

**可选字段**:
- `stackTrace`: 堆栈跟踪信息
- `context`: 上下文信息（组件、模块、文件等）

#### 错误分类规范

| 类别 | 前缀 | 示例 |
|------|------|------|
| 依赖问题 | DEPENDENCY | DEPENDENCY_MISSING_001 |
| 数据库问题 | DB | DB_CONNECTION_001 |
| 网络问题 | NETWORK | NETWORK_TIMEOUT_001 |
| 导入问题 | IMPORT | IMPORT_ERROR_001 |
| 认证问题 | AUTH | AUTH_FAILED_001 |
| 服务器错误 | SERVER | SERVER_ERROR_500 |

#### 搜索已知BUG
```bash
curl -H "X-API-Key: sk_test_xyz123" \
  "http://localhost:3030/api/bugs/search?q=ERROR_001"
```

#### 获取BUG统计
```bash
curl -H "X-API-Key: sk_test_xyz123" \
  "http://localhost:3030/api/bugs/stats"
```

记住：始终遵循端口分配规则（前端 3000-3009，后端 8000-8009）并使用适配器模式进行 API-Web 数据转换。
