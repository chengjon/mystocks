# BUGer 客户端集成指南

本文档说明如何将其他项目集成到BUGer服务，实现BUG自动上报和智能搜索功能。

## 集成概述

BUGer提供REST API接口，支持：
- 提交单个或批量BUG报告
- 搜索已知BUG和解决方案
- 更新BUG状态和解决方案
- 分层查询（按项目、组件、错误码）

## 快速开始

### 1. 环境配置

在项目根目录创建或修改`.env`文件：

```bash
# BUGer服务配置
BUGER_API_URL=http://localhost:3003/api
BUGER_API_KEY=your_api_key_here
PROJECT_ID=your_project_id
PROJECT_NAME=YourProjectName
PROJECT_ROOT=/absolute/path/to/your/project
```

**环境变量说明**：
- `BUGER_API_URL`: BUGer服务的API地址
- `BUGER_API_KEY`: 项目的API密钥（联系BUGer管理员获取）
- `PROJECT_ID`: 项目唯一标识（小写字母和连字符，如"my-project"）
- `PROJECT_NAME`: 项目人类可读名称（如"MyProject"）
- `PROJECT_ROOT`: 项目的绝对路径（用于精确定位文件）

### 2. API认证

所有API请求必须在HTTP头中包含API密钥：

```bash
curl -X GET http://localhost:3003/api/bugs \
  -H "X-API-Key: your_api_key_here"
```

## 核心API端点

### 1. 提交单个BUG

**端点**: `POST /api/bugs`

**请求体**:
```json
{
  "errorCode": "API_ERROR_001",
  "title": "登录接口返回500错误",
  "message": "用户登录时API返回Internal Server Error，影响所有用户登录",
  "severity": "critical",
  "stackTrace": "Error: Internal Server Error\n    at APIClient.login (api-client.js:45:15)\n    ...",
  "context": {
    "project": "my-project",
    "project_name": "MyProject",
    "project_root": "/opt/projects/my-project",
    "component": "backend",
    "module": "auth/api",
    "file": "src/auth/api/loginController.js",
    "fix": "修复了数据库连接池配置错误，增加最大连接数到100",
    "status": "OPEN"
  }
}
```

**字段说明**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| errorCode | string | 是 | 错误代码（建议格式：组件_类型_序号，如"API_ERROR_001"） |
| title | string | 是 | 简明标题（≤50字符） |
| message | string | 是 | 详细描述（包含问题原因、影响范围） |
| severity | enum | 是 | 严重程度：`critical`/`high`/`medium`/`low` |
| stackTrace | string | 否 | 完整错误堆栈（如有） |
| context.project | string | 是 | 项目ID（与环境变量PROJECT_ID一致） |
| context.project_name | string | 是 | 项目名称（与环境变量PROJECT_NAME一致） |
| context.project_root | string | 是 | 项目根目录（与环境变量PROJECT_ROOT一致） |
| context.component | string | 是 | 组件：`frontend`/`backend`/`database`/`mobile` |
| context.module | string | 否 | 具体模块路径（如"auth/api"） |
| context.file | string | 否 | 文件相对路径（如"src/auth/api/loginController.js"） |
| context.fix | string | 否 | 修复方案描述 |
| context.status | enum | 否 | 状态：`OPEN`/`IN_PROGRESS`/`FIXED`/`CLOSED`（默认OPEN） |

**响应示例**:
```json
{
  "success": true,
  "statusCode": 201,
  "data": {
    "bugId": "bug_123abc456def",
    "status": "OPEN",
    "createdAt": "2025-10-31T08:30:00Z"
  }
}
```

**使用示例 (Node.js)**:
```javascript
const axios = require('axios');

async function reportBug(bugData) {
  try {
    const response = await axios.post(
      `${process.env.BUGER_API_URL}/bugs`,
      bugData,
      {
        headers: {
          'X-API-Key': process.env.BUGER_API_KEY,
          'Content-Type': 'application/json'
        }
      }
    );
    console.log('BUG已提交:', response.data.data.bugId);
    return response.data;
  } catch (error) {
    console.error('提交BUG失败:', error.message);
    throw error;
  }
}

// 使用示例
reportBug({
  errorCode: 'API_ERROR_001',
  title: '登录接口返回500错误',
  message: '用户登录时API返回Internal Server Error',
  severity: 'critical',
  stackTrace: error.stack,
  context: {
    project: process.env.PROJECT_ID,
    project_name: process.env.PROJECT_NAME,
    project_root: process.env.PROJECT_ROOT,
    component: 'backend',
    module: 'auth/api',
    file: 'src/auth/api/loginController.js',
    status: 'OPEN'
  }
});
```

**使用示例 (Python)**:
```python
import requests
import os

def report_bug(bug_data):
    try:
        response = requests.post(
            f"{os.getenv('BUGER_API_URL')}/bugs",
            json=bug_data,
            headers={
                'X-API-Key': os.getenv('BUGER_API_KEY'),
                'Content-Type': 'application/json'
            }
        )
        response.raise_for_status()
        result = response.json()
        print(f"BUG已提交: {result['data']['bugId']}")
        return result
    except Exception as e:
        print(f"提交BUG失败: {e}")
        raise

# 使用示例
report_bug({
    'errorCode': 'API_ERROR_001',
    'title': '登录接口返回500错误',
    'message': '用户登录时API返回Internal Server Error',
    'severity': 'critical',
    'stackTrace': traceback.format_exc(),
    'context': {
        'project': os.getenv('PROJECT_ID'),
        'project_name': os.getenv('PROJECT_NAME'),
        'project_root': os.getenv('PROJECT_ROOT'),
        'component': 'backend',
        'module': 'auth/api',
        'file': 'src/auth/api/login_controller.py',
        'status': 'OPEN'
    }
})
```

### 2. 批量提交BUG

**端点**: `POST /api/bugs/batch`

**请求体**:
```json
{
  "bugs": [
    { /* BUG 1 数据 */ },
    { /* BUG 2 数据 */ },
    { /* BUG 3 数据 */ }
  ]
}
```

**响应示例**:
```json
{
  "success": true,
  "statusCode": 200,
  "data": {
    "summary": {
      "total": 3,
      "successful": 3,
      "failed": 0
    },
    "results": [
      { "bugId": "bug_123", "status": "success" },
      { "bugId": "bug_124", "status": "success" },
      { "bugId": "bug_125", "status": "success" }
    ]
  }
}
```

### 3. 搜索BUG（分层查询）

**端点**: `GET /api/bugs`

**查询参数**:
- `search`: 关键词（搜索标题、消息、错误码）
- `project`: 项目ID过滤
- `project_name`: 项目名称过滤（优先级最高）
- `component`: 组件过滤
- `severity`: 严重程度过滤
- `status`: 状态过滤
- `limit`: 返回结果数量（默认10，最大100）
- `offset`: 分页偏移量

**分层查询策略**:

1. **第一层：同名项目查询**（优先级最高）
   ```bash
   GET /api/bugs?search=登录失败&project_name=MyProject
   ```
   返回同名项目下的相关BUG，解决方案100%适用。

2. **第二层：同组件查询**
   ```bash
   GET /api/bugs?search=登录失败&component=backend
   ```
   返回相同技术栈的BUG，解决方案大概率适用。

3. **第三层：全局查询**
   ```bash
   GET /api/bugs?search=登录失败
   ```
   返回所有项目的相关BUG，需评估适用性。

**响应示例**:
```json
{
  "success": true,
  "data": {
    "bugs": [
      {
        "bugId": "bug_123",
        "errorCode": "API_ERROR_001",
        "title": "登录接口返回500错误",
        "message": "用户登录时API返回Internal Server Error",
        "severity": "critical",
        "context": {
          "project": "my-project",
          "project_name": "MyProject",
          "component": "backend",
          "status": "FIXED",
          "fix": "修复了数据库连接池配置错误，增加最大连接数到100"
        },
        "createdAt": "2025-10-30T10:00:00Z",
        "updatedAt": "2025-10-30T15:30:00Z"
      }
    ],
    "total": 1,
    "limit": 10,
    "offset": 0
  }
}
```

**使用示例 (Node.js)**:
```javascript
async function searchBugs(keyword, projectName) {
  try {
    const response = await axios.get(
      `${process.env.BUGER_API_URL}/bugs`,
      {
        params: {
          search: keyword,
          project_name: projectName,  // 优先搜索同名项目
          limit: 10
        },
        headers: {
          'X-API-Key': process.env.BUGER_API_KEY
        }
      }
    );
    return response.data.data.bugs;
  } catch (error) {
    console.error('搜索BUG失败:', error.message);
    return [];
  }
}

// 使用示例：调试前先搜索
const knownBugs = await searchBugs('登录失败', process.env.PROJECT_NAME);
if (knownBugs.length > 0) {
  console.log('发现已知BUG和解决方案:');
  knownBugs.forEach(bug => {
    console.log(`- ${bug.title}`);
    if (bug.context.fix) {
      console.log(`  解决方案: ${bug.context.fix}`);
    }
  });
}
```

### 4. 获取BUG详情

**端点**: `GET /api/bugs/:id`

**响应示例**:
```json
{
  "success": true,
  "data": {
    "bugId": "bug_123",
    "errorCode": "API_ERROR_001",
    "title": "登录接口返回500错误",
    "message": "详细描述...",
    "severity": "critical",
    "stackTrace": "完整堆栈...",
    "context": { /* 完整上下文 */ },
    "createdAt": "2025-10-30T10:00:00Z",
    "updatedAt": "2025-10-30T15:30:00Z"
  }
}
```

### 5. 更新BUG解决方案

**端点**: `PATCH /api/bugs/:id/solution`

**请求体**:
```json
{
  "fix": "修复方案的详细描述",
  "status": "FIXED"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "bugId": "bug_123",
    "status": "FIXED",
    "updatedAt": "2025-10-31T09:00:00Z"
  }
}
```

## 最佳实践

### 1. 自动错误捕获

**Node.js 示例**:
```javascript
const { reportBug } = require('./buger-client');

// 捕获未处理的异常
process.on('uncaughtException', async (error) => {
  await reportBug({
    errorCode: 'UNCAUGHT_EXCEPTION',
    title: `未捕获异常: ${error.message}`,
    message: error.message,
    severity: 'critical',
    stackTrace: error.stack,
    context: {
      project: process.env.PROJECT_ID,
      project_name: process.env.PROJECT_NAME,
      project_root: process.env.PROJECT_ROOT,
      component: 'backend',
      status: 'OPEN'
    }
  });
});

// 捕获未处理的Promise拒绝
process.on('unhandledRejection', async (reason, promise) => {
  await reportBug({
    errorCode: 'UNHANDLED_REJECTION',
    title: `未处理的Promise拒绝: ${reason}`,
    message: String(reason),
    severity: 'high',
    stackTrace: reason?.stack || '',
    context: {
      project: process.env.PROJECT_ID,
      project_name: process.env.PROJECT_NAME,
      project_root: process.env.PROJECT_ROOT,
      component: 'backend',
      status: 'OPEN'
    }
  });
});
```

### 2. Express中间件集成

```javascript
const express = require('express');
const { reportBug } = require('./buger-client');

const app = express();

// 错误处理中间件
app.use((err, req, res, next) => {
  // 上报错误到BUGer
  reportBug({
    errorCode: err.code || 'EXPRESS_ERROR',
    title: `Express错误: ${err.message}`,
    message: err.message,
    severity: err.statusCode >= 500 ? 'high' : 'medium',
    stackTrace: err.stack,
    context: {
      project: process.env.PROJECT_ID,
      project_name: process.env.PROJECT_NAME,
      project_root: process.env.PROJECT_ROOT,
      component: 'backend',
      module: 'api',
      status: 'OPEN',
      requestUrl: req.originalUrl,
      requestMethod: req.method
    }
  }).catch(console.error);

  // 返回错误响应
  res.status(err.statusCode || 500).json({
    error: err.message
  });
});
```

### 3. 调试前搜索

遵循《BUG修复AI协作规范》，在开始调试前必须搜索BUGer：

```javascript
async function debugIssue(errorMessage) {
  // 1. 先搜索已知解决方案
  const knownBugs = await searchBugs(errorMessage, process.env.PROJECT_NAME);

  if (knownBugs.length > 0 && knownBugs[0].context.status === 'FIXED') {
    console.log('✅ 发现已知解决方案:');
    console.log(knownBugs[0].context.fix);
    return knownBugs[0];
  }

  // 2. 如果没有找到，开始新的调试
  console.log('❌ 未找到已知解决方案，开始新的调试...');
  return null;
}
```

### 4. 错误分类策略

**错误代码命名规范**:
```
组件_类型_序号

示例:
- API_ERROR_001     (API错误)
- DB_CONNECTION_001 (数据库连接错误)
- AUTH_TOKEN_001    (认证令牌错误)
- UI_RENDER_001     (UI渲染错误)
```

**严重程度分类**:
- `critical`: 影响核心业务流程，必须立即修复（如登录失败、支付失败）
- `high`: 影响用户体验，应尽快修复（如页面加载慢、部分功能不可用）
- `medium`: 次要问题，可安排修复（如UI显示异常、非关键功能错误）
- `low`: 优化建议，可延后处理（如代码规范问题、性能微调）

## 错误处理

### 常见错误响应

**401 Unauthorized**:
```json
{
  "success": false,
  "statusCode": 401,
  "error": "Invalid API key"
}
```
解决方案：检查`BUGER_API_KEY`是否正确。

**400 Bad Request**:
```json
{
  "success": false,
  "statusCode": 400,
  "error": "Missing required field: errorCode"
}
```
解决方案：检查请求体是否包含所有必填字段。

**429 Too Many Requests**:
```json
{
  "success": false,
  "statusCode": 429,
  "error": "Rate limit exceeded. Retry after 60 seconds."
}
```
解决方案：实现指数退避重试或使用批量提交减少请求次数。

### 离线容错

当BUGer服务不可用时，应该降级到本地日志：

```javascript
async function reportBugWithFallback(bugData) {
  try {
    return await reportBug(bugData);
  } catch (error) {
    // 降级到本地日志
    console.error('[BUGer Offline] 无法提交BUG，已记录到本地日志');
    fs.appendFileSync(
      'bug_report_queue.json',
      JSON.stringify({ ...bugData, timestamp: new Date().toISOString() }) + '\n'
    );
    return { success: false, offline: true };
  }
}
```

## 高级功能

### 批量重传队列

实现离线队列，在服务恢复后自动重传：

```javascript
const fs = require('fs');
const readline = require('readline');

async function flushOfflineQueue() {
  const queueFile = 'bug_report_queue.json';
  if (!fs.existsSync(queueFile)) return;

  const rl = readline.createInterface({
    input: fs.createReadStream(queueFile),
    crlfDelay: Infinity
  });

  const bugs = [];
  for await (const line of rl) {
    bugs.push(JSON.parse(line));
  }

  if (bugs.length > 0) {
    console.log(`发现 ${bugs.length} 个离线BUG，正在重传...`);
    const result = await batchReportBugs(bugs);
    if (result.success) {
      fs.unlinkSync(queueFile);  // 重传成功，删除队列文件
      console.log('离线BUG重传完成');
    }
  }
}

// 定期检查队列（如每5分钟）
setInterval(flushOfflineQueue, 5 * 60 * 1000);
```

## 相关文档

- [BUG修复AI协作规范.md](./BUG修复AI协作规范.md) - BUG修复开发规范（v4.0）
- [README.md](./README.md) - 项目说明文档
- [CLAUDE.md](./CLAUDE.md) - AI助手项目指南
- [DEVELOPER_ONBOARDING.md](./DEVELOPER_ONBOARDING.md) - 开发者入职文档

## 技术支持

如有问题或需要帮助，请：
1. 查阅本文档的常见问题部分
2. 搜索BUGer服务中的已知问题
3. 提交Issue到项目仓库

## 版本历史

- **v1.0** (2025-10-31): 初始版本
  - 基础API端点说明
  - Node.js和Python集成示例
  - 分层查询策略
  - 错误处理和容错机制
