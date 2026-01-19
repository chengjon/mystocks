# BUGer 服务接入指南

> **完整的项目集成指南** - 如何将您的项目接入 BUGer 服务进行 BUG 管理

## 目录

- [1. 概述](#1-概述)
- [2. 架构说明](#2-架构说明)
- [3. 前置条件](#3-前置条件)
- [4. 快速开始](#4-快速开始)
- [5. 详细集成步骤](#5-详细集成步骤)
- [6. 代码示例](#6-代码示例)
- [7. API 参考](#7-api-参考)
- [8. 故障排除](#8-故障排除)
- [9. 常见问题](#9-常见问题)

---

## 1. 概述

BUGer 是一个 BUG 管理知识库系统，帮助团队：

- 📝 统一收集和管理运行时 BUG
- 🔍 快速搜索已知问题和解决方案
- 📊 分析 BUG 趋势和统计数据
- 🤝 跨项目共享调试经验

### 1.1 适用场景

- Web 应用程序 (Node.js, Python, Java 等)
- 移动应用程序
- 后台服务和 API
- 数据处理管道
- 任何需要集中 BUG 管理的系统

---

## 2. 架构说明

### 2.1 系统架构

```
┌─────────────────┐
│   您的项目       │
│  (任何语言)      │
└────────┬────────┘
         │ HTTP API
         ↓
┌─────────────────┐
│  BUGer API      │
│  (Node.js)      │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   MongoDB       │
│  (存储层)        │
└─────────────────┘
```

### 2.2 技术栈

- **BUGer 后端**: Node.js 18+ / Express.js 5.x
- **数据库**: MongoDB 6.0+
- **通信协议**: RESTful API (JSON)
- **认证方式**: API Key (X-API-Key header)

**注意**: BUGer 已采用 MongoDB-only 架构，无需 Redis 依赖。

---

## 3. 前置条件

### 3.1 服务端要求

确保 BUGer 服务已启动：

```bash
# 检查服务状态
curl http://localhost:3003/health

# 预期输出
{
  "status": "ok",
  "server": {
    "name": "BUGer API",
    "port": 3003,
    "baseUrl": "http://localhost:3003/api"
  }
}
```

**端口说明**: BUGer 支持自动端口选择 (3003-3013)，实际端口请查看服务启动日志。

### 3.2 客户端要求

- HTTP 客户端库 (axios, requests, fetch 等)
- 能够发送 JSON 格式的 POST 请求
- 支持设置自定义 HTTP 头 (X-API-Key)

---

## 4. 快速开始

### 4.1 获取 API Key

1. 联系 BUGer 管理员获取 API Key
2. API Key 格式: `sk_xxx...` (以 `sk_` 开头)
3. 每个项目使用独立的 API Key

### 4.2 测试连接

```bash
# 使用 curl 测试
curl -X POST http://localhost:3003/api/bugs \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "errorCode": "TEST_001",
    "title": "测试连接",
    "message": "验证 BUGer 服务连接",
    "severity": "low"
  }'

# 预期输出
{
  "success": true,
  "data": {
    "bugId": "...",
    "status": "OPEN"
  }
}
```

---

## 5. 详细集成步骤

### 步骤 1: 环境配置

在项目的 `.env` 文件中添加：

```bash
# BUGer 服务配置
BUGER_API_URL=http://localhost:3003/api
BUGER_API_KEY=sk_your_api_key_here
PROJECT_ID=your-project-id
PROJECT_NAME=YourProjectName
PROJECT_ROOT=/path/to/your/project
```

### 步骤 2: 安装依赖

**Node.js / JavaScript:**
```bash
npm install axios dotenv
```

**Python:**
```bash
pip install requests python-dotenv
```

**其他语言**: 安装对应的 HTTP 客户端库

### 步骤 3: 创建 BUG 上报模块

见 [代码示例](#6-代码示例) 章节

### 步骤 4: 集成到错误处理

在您的全局错误处理器中调用 BUG 上报：

**Express.js 示例:**
```javascript
app.use((err, req, res, next) => {
  // 上报 BUG 到 BUGer
  bugReporter.report({
    errorCode: err.code || 'UNKNOWN_ERROR',
    title: err.message,
    message: err.stack,
    severity: 'high',
    context: {
      component: 'backend',
      module: req.path,
      file: err.fileName
    }
  });

  // 返回错误响应
  res.status(500).json({ error: err.message });
});
```

### 步骤 5: 验证集成

```bash
# 1. 触发一个错误
# 2. 检查 BUGer 是否收到上报
curl -H "X-API-Key: YOUR_API_KEY" \
  http://localhost:3003/api/bugs/stats

# 3. 搜索您刚上报的 BUG
curl -H "X-API-Key: YOUR_API_KEY" \
  "http://localhost:3003/api/bugs/search?q=YOUR_ERROR_CODE"
```

---

## 6. 代码示例

### 6.1 Node.js / JavaScript

```javascript
// buger-client.js
const axios = require('axios');
require('dotenv').config();

class BUGerClient {
  constructor() {
    this.apiUrl = process.env.BUGER_API_URL;
    this.apiKey = process.env.BUGER_API_KEY;
    this.projectId = process.env.PROJECT_ID;
    this.projectName = process.env.PROJECT_NAME;
    this.projectRoot = process.env.PROJECT_ROOT;
  }

  async reportBug(bugData) {
    try {
      const response = await axios.post(
        `${this.apiUrl}/bugs`,
        {
          errorCode: bugData.errorCode,
          title: bugData.title,
          message: bugData.message,
          severity: bugData.severity || 'medium',
          stackTrace: bugData.stackTrace || '',
          context: {
            timestamp: new Date().toISOString(),
            project: this.projectId,
            project_name: this.projectName,
            project_root: this.projectRoot,
            component: bugData.context?.component || 'unknown',
            module: bugData.context?.module || '',
            file: bugData.context?.file || '',
            status: 'OPEN'
          }
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': this.apiKey
          }
        }
      );

      console.log('✓ BUG 已上报到 BUGer:', response.data.data.bugId);
      return response.data;
    } catch (error) {
      console.error('✗ BUG 上报失败:', error.message);
      // 降级处理: 记录到本地日志
      this.logToFile(bugData);
      throw error;
    }
  }

  async reportBugsBatch(bugs) {
    try {
      const response = await axios.post(
        `${this.apiUrl}/bugs/batch`,
        { bugs },
        {
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': this.apiKey
          }
        }
      );

      console.log('✓ 批量上报成功:', response.data.data.summary);
      return response.data;
    } catch (error) {
      console.error('✗ 批量上报失败:', error.message);
      throw error;
    }
  }

  async searchBugs(query) {
    try {
      const response = await axios.get(
        `${this.apiUrl}/bugs/search?q=${encodeURIComponent(query)}`,
        {
          headers: {
            'X-API-Key': this.apiKey
          }
        }
      );

      return response.data.data.bugs;
    } catch (error) {
      console.error('✗ 搜索失败:', error.message);
      throw error;
    }
  }

  logToFile(bugData) {
    // 本地日志备份 (当 BUGer 服务不可用时)
    const fs = require('fs');
    const logFile = './bug-reports-backup.jsonl';
    fs.appendFileSync(logFile, JSON.stringify(bugData) + '\n');
  }
}

module.exports = new BUGerClient();
```

**使用示例:**
```javascript
const bugReporter = require('./buger-client');

// 上报单个 BUG
try {
  await bugReporter.reportBug({
    errorCode: 'DB_CONNECTION_FAILED',
    title: '数据库连接失败',
    message: 'MongoDB connection timeout after 30s',
    severity: 'critical',
    stackTrace: error.stack,
    context: {
      component: 'backend',
      module: 'database',
      file: 'src/db/connection.js'
    }
  });
} catch (err) {
  console.error('上报失败:', err);
}

// 搜索已知 BUG
const knownBugs = await bugReporter.searchBugs('DB_CONNECTION_FAILED');
if (knownBugs.length > 0) {
  console.log('找到已知解决方案:', knownBugs[0].context.fix);
}
```

### 6.2 Python

```python
# buger_client.py
import os
import requests
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class BUGerClient:
    def __init__(self):
        self.api_url = os.getenv('BUGER_API_URL')
        self.api_key = os.getenv('BUGER_API_KEY')
        self.project_id = os.getenv('PROJECT_ID')
        self.project_name = os.getenv('PROJECT_NAME')
        self.project_root = os.getenv('PROJECT_ROOT')

        if not all([self.api_url, self.api_key, self.project_id]):
            raise ValueError("Missing required environment variables")

    def report_bug(self, bug_data: Dict) -> Dict:
        """上报单个 BUG"""
        payload = {
            "errorCode": bug_data['errorCode'],
            "title": bug_data['title'],
            "message": bug_data['message'],
            "severity": bug_data.get('severity', 'medium'),
            "stackTrace": bug_data.get('stackTrace', ''),
            "context": {
                "timestamp": datetime.utcnow().isoformat(),
                "project": self.project_id,
                "project_name": self.project_name,
                "project_root": self.project_root,
                "component": bug_data.get('context', {}).get('component', 'unknown'),
                "module": bug_data.get('context', {}).get('module', ''),
                "file": bug_data.get('context', {}).get('file', ''),
                "status": "OPEN"
            }
        }

        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        }

        try:
            response = requests.post(
                f'{self.api_url}/bugs',
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()

            result = response.json()
            print(f"✓ BUG 已上报: {result['data']['bugId']}")
            return result

        except requests.exceptions.RequestException as e:
            print(f"✗ BUG 上报失败: {e}")
            self._log_to_file(bug_data)
            raise

    def report_bugs_batch(self, bugs: List[Dict]) -> Dict:
        """批量上报 BUG"""
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        }

        try:
            response = requests.post(
                f'{self.api_url}/bugs/batch',
                json={'bugs': bugs},
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            print(f"✓ 批量上报成功: {result['data']['summary']}")
            return result

        except requests.exceptions.RequestException as e:
            print(f"✗ 批量上报失败: {e}")
            raise

    def search_bugs(self, query: str) -> List[Dict]:
        """搜索 BUG"""
        headers = {'X-API-Key': self.api_key}

        try:
            response = requests.get(
                f'{self.api_url}/bugs/search',
                params={'q': query},
                headers=headers,
                timeout=10
            )
            response.raise_for_status()

            return response.json()['data']['bugs']

        except requests.exceptions.RequestException as e:
            print(f"✗ 搜索失败: {e}")
            raise

    def _log_to_file(self, bug_data: Dict):
        """本地备份"""
        import json
        with open('bug-reports-backup.jsonl', 'a') as f:
            f.write(json.dumps(bug_data) + '\n')

# 创建全局实例
buger_client = BUGerClient()
```

**使用示例:**
```python
from buger_client import buger_client
import traceback

# 上报 BUG
try:
    buger_client.report_bug({
        'errorCode': 'IMPORT_ERROR_001',
        'title': '模块导入失败',
        'message': 'Cannot import name "calculate_metrics"',
        'severity': 'high',
        'stackTrace': traceback.format_exc(),
        'context': {
            'component': 'backend',
            'module': 'analytics',
            'file': 'src/analytics/metrics.py'
        }
    })
except Exception as e:
    print(f'上报失败: {e}')

# 搜索已知 BUG
known_bugs = buger_client.search_bugs('IMPORT_ERROR_001')
if known_bugs:
    print(f'找到解决方案: {known_bugs[0]["context"]["fix"]}')
```

---

## 7. API 参考

### 7.1 基础信息

- **Base URL**: `http://localhost:3003/api` (或其他端口)
- **认证方式**: `X-API-Key` 请求头
- **数据格式**: JSON

### 7.2 主要端点

#### 上报单个 BUG

```http
POST /api/bugs
Content-Type: application/json
X-API-Key: YOUR_API_KEY

{
  "errorCode": "string (必填)",
  "title": "string (必填, ≤50字符)",
  "message": "string (必填)",
  "severity": "critical|high|medium|low (必填)",
  "stackTrace": "string (可选)",
  "context": {
    "project": "string (自动填充)",
    "project_name": "string (必填)",
    "project_root": "string (必填)",
    "component": "frontend|backend|database (可选)",
    "module": "string (可选)",
    "file": "string (可选)",
    "fix": "string (可选)",
    "status": "OPEN|IN_PROGRESS|FIXED|CLOSED (可选)"
  }
}
```

**响应:**
```json
{
  "success": true,
  "statusCode": 201,
  "data": {
    "bugId": "507f1f77bcf86cd799439011",
    "status": "OPEN",
    "createdAt": "2025-11-17T00:00:00.000Z"
  }
}
```

#### 批量上报 BUG

```http
POST /api/bugs/batch
Content-Type: application/json
X-API-Key: YOUR_API_KEY

{
  "bugs": [
    { /* BUG 对象 1 */ },
    { /* BUG 对象 2 */ }
  ]
}
```

**限制**: 单次最多 20 个 BUG

#### 搜索 BUG

```http
GET /api/bugs/search?q=KEYWORD&project=PROJECT_ID
X-API-Key: YOUR_API_KEY
```

**查询参数:**
- `q` (可选): 搜索关键词
- `project` (可选): 项目 ID
- `severity` (可选): 严重程度
- `status` (可选): 状态
- `page` (可选): 页码 (默认 1)
- `limit` (可选): 每页数量 (默认 20)

#### 获取统计信息

```http
GET /api/bugs/stats
X-API-Key: YOUR_API_KEY
```

**响应:**
```json
{
  "success": true,
  "data": {
    "total": 150,
    "bySeverity": {
      "critical": 5,
      "high": 20,
      "medium": 75,
      "low": 50
    },
    "byStatus": {
      "OPEN": 80,
      "IN_PROGRESS": 30,
      "FIXED": 35,
      "CLOSED": 5
    }
  }
}
```

### 7.3 健康检查

```http
GET /health
```

无需认证，返回服务状态。

---

## 8. 故障排除

### 8.1 常见问题

#### 问题 1: 连接被拒绝

**症状**: `ECONNREFUSED` 或 `Connection refused`

**解决方法**:
```bash
# 1. 检查服务是否运行
curl http://localhost:3003/health

# 2. 检查端口是否正确 (可能自动选择了 3004-3013)
# 查看 BUGer 启动日志确认实际端口

# 3. 更新 .env 文件
BUGER_API_URL=http://localhost:3004/api  # 使用实际端口
```

#### 问题 2: 认证失败 (401)

**症状**: `{"error": "Unauthorized"}`

**解决方法**:
```bash
# 1. 检查 API Key 是否正确
echo $BUGER_API_KEY

# 2. 确认请求头格式
curl -v -H "X-API-Key: sk_xxx" http://localhost:3003/api/bugs/stats

# 3. API Key 必须以 sk_ 开头且长度 ≥ 10
```

#### 问题 3: 请求格式错误 (400)

**症状**: `{"error": "Validation failed"}`

**解决方法**:
- 检查必填字段: `errorCode`, `title`, `message`, `severity`
- 检查 `severity` 值: 必须是 `critical|high|medium|low`
- 检查 `context.project_name` 和 `context.project_root` 是否填写

#### 问题 4: 服务器错误 (500)

**症状**: `{"error": "Internal Server Error"}`

**解决方法**:
```bash
# 1. 检查 BUGer 服务日志
cd /opt/iflow/buger/backend
tail -f logs/error.log

# 2. 检查 MongoDB 连接
curl http://localhost:3003/health/deep

# 3. 联系管理员
```

### 8.2 调试技巧

#### 开启详细日志

在您的客户端代码中:

**Node.js:**
```javascript
axios.interceptors.request.use(req => {
  console.log('→ Request:', req.method, req.url, req.data);
  return req;
});

axios.interceptors.response.use(res => {
  console.log('← Response:', res.status, res.data);
  return res;
}, err => {
  console.error('✗ Error:', err.response?.data || err.message);
  throw err;
});
```

**Python:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 使用健康检查验证配置

```bash
# 验证连接
curl -X POST http://localhost:3003/health/verify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"apiUrl": "http://localhost:3003/api", "port": 3003}'
```

---

## 9. 常见问题

### 9.1 集成相关

**Q: 是否支持异步上报？**

A: 是的，建议使用异步上报以避免阻塞主流程：

```javascript
// Node.js 异步上报
bugReporter.reportBug(bugData).catch(err => {
  console.error('BUG 上报失败，已记录到本地:', err);
});
```

**Q: 上报失败会影响我的应用吗？**

A: 不会。上报失败时客户端应降级到本地日志，不应中断主流程。

**Q: 是否支持批量上报？**

A: 是的，使用 `POST /api/bugs/batch`，单次最多 20 个 BUG。

### 9.2 性能相关

**Q: 每次请求的延迟是多少？**

A: 通常 < 100ms (本地网络)。建议异步上报避免影响用户体验。

**Q: 是否有速率限制？**

A: 默认限制：每个项目每分钟 200 次请求。如需提高请联系管理员。

### 9.3 架构相关

**Q: BUGer 是否依赖 Redis？**

A: **不依赖**。BUGer 已采用 MongoDB-only 架构，简化了部署。

**Q: 数据如何存储？**

A: 所有数据存储在 MongoDB 中，支持全文搜索和复杂查询。

---

## 附录

### A. 环境变量完整列表

```bash
# BUGer 服务地址
BUGER_API_URL=http://localhost:3003/api

# API 认证密钥
BUGER_API_KEY=sk_your_api_key_here

# 项目标识
PROJECT_ID=your-project-id
PROJECT_NAME=YourProjectName  # 必填，用于同名项目优先搜索
PROJECT_ROOT=/path/to/project  # 必填，项目根目录

# 可选配置
BUGER_TIMEOUT=10000            # 请求超时时间 (毫秒)
BUGER_RETRY_COUNT=3            # 失败重试次数
```

### B. 相关文档

- **[BUG修复AI协作规范.md](./BUG修复AI协作规范.md)** - AI 协作开发规范
- **[命令行监控工具使用指南.md](./命令行监控工具使用指南.md)** - 监控工具使用
- **[CLIENT_CONNECTION_GUIDE.md](./CLIENT_CONNECTION_GUIDE.md)** - 连接配置详解

---

**文档版本**: v2.0
**更新时间**: 2025-11-17
**架构版本**: MongoDB-only (Redis removed)
**联系方式**: 如有问题请提交 Issue 或联系管理员
