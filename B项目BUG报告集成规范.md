# B项目BUG报告集成规范

## 1. 概述

本文档定义了B项目如何与BUGer系统集成，以确保错误报告能够正确、规范地传递到BUGer知识库中。

## 2. 环境配置

### 2.1 环境变量设置

在B项目的 `.env` 文件中配置以下环境变量：

```bash
BUGER_API_URL=http://localhost:3003/api
BUGER_API_KEY=sk_test_xyz123
PROJECT_ID=test-project
```

### 2.2 依赖安装

```bash
npm install axios dotenv
```

## 3. BUG报告格式规范

### 3.1 必需字段

每个BUG报告必须包含以下字段：

| 字段名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| errorCode | string | 是 | 错误代码，大写字母、数字和下划线组成 |
| title | string | 是 | 错误标题，简洁描述问题 |
| message | string | 是 | 详细错误信息 |
| severity | string | 是 | 严重级别：critical, high, medium, low |

### 3.2 可选字段

| 字段名 | 类型 | 描述 |
|--------|------|------|
| stackTrace | string | 堆栈跟踪信息 |
| context | object | 上下文信息 |

### 3.3 context字段规范

context字段应包含以下信息：

```javascript
{
  "timestamp": "2025-10-30T15:59:02.552Z",  // 时间戳
  "project": "项目名称",                    // 项目名称
  "component": "backend/frontend/other",   // 组件
  "module": "模块名称",                     // 模块
  "file": "文件路径",                       // 文件路径
  "function": "函数名称",                   // 函数名
  "line": 20,                              // 行号
  "environment": {                         // 环境信息
    "os": "Linux",
    "version": "1.0.0"
  }
}
```

## 4. 错误分类规范

### 4.1 主要错误类别

| 大类 | 小类 | 描述 |
|------|------|------|
| 依赖问题 | 缺失依赖包 | 缺少必要的第三方库 |
| 依赖问题 | 版本冲突 | 依赖库版本不兼容 |
| 导入问题 | 模块导入失败 | 无法导入模块或函数 |
| 导入问题 | 路径错误 | 模块路径配置错误 |
| 服务器错误 | 内部服务器错误 | 500系列错误 |
| 数据库问题 | 连接失败 | 数据库连接问题 |
| 数据库问题 | 查询错误 | SQL或查询语句错误 |
| 网络问题 | 超时 | 请求超时 |
| 网络问题 | 连接失败 | 网络连接问题 |
| 权限问题 | 访问拒绝 | 权限不足 |
| 权限问题 | 认证失败 | 身份验证失败 |

### 4.2 严重级别定义

| 级别 | 定义 | 影响 |
|------|------|------|
| critical | 致命错误 | 系统无法运行或核心功能失效 |
| high | 高级错误 | 重要功能受影响，用户无法正常使用 |
| medium | 中级错误 | 部分功能受影响，但不影响主要使用 |
| low | 低级错误 | 轻微问题，不影响正常使用 |

## 5. API调用规范

### 5.1 单个BUG上报

```javascript
// 请求URL
POST /api/bugs

// 请求头
{
  "X-API-Key": "sk_test_xyz123",
  "Content-Type": "application/json"
}

// 请求体
{
  "errorCode": "MODULE_NOT_FOUND_001",
  "title": "缺少apscheduler依赖导致后端ImportError",
  "message": "scheduled_data_update.py需要apscheduler库，但环境中未安装该依赖",
  "severity": "critical",
  "stackTrace": "ModuleNotFoundError: No module named 'apscheduler'...",
  "context": {
    "timestamp": "2025-10-30T15:59:02.552Z",
    "project": "mystocks",
    "component": "backend",
    "module": "app.services.scheduled_data_update",
    "file": "web/backend/app/services/scheduled_data_update.py"
  }
}
```

### 5.2 批量BUG上报

```javascript
// 请求URL
POST /api/bugs/batch

// 请求头
{
  "X-API-Key": "sk_test_xyz123",
  "Content-Type": "application/json"
}

// 请求体
{
  "bugs": [
    {
      // BUG 1 数据
    },
    {
      // BUG 2 数据
    }
  ]
}
```

## 6. 集成实现示例

### 6.1 BUG报告客户端

```javascript
// src/utils/bug-reporter.js
const axios = require('axios');
require('dotenv').config();

class BugReporter {
  constructor() {
    this.apiURL = process.env.BUGER_API_URL || 'http://localhost:3003/api';
    this.apiKey = process.env.BUGER_API_KEY || 'sk_test_xyz123';
    this.projectId = process.env.PROJECT_ID || 'test-project';
  }

  // 上报单个BUG
  async reportBug(bugData) {
    try {
      const response = await axios.post(`${this.apiURL}/bugs`, bugData, {
        headers: {
          'X-API-Key': this.apiKey,
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    } catch (error) {
      console.error('BUG上报失败:', error.message);
      throw error;
    }
  }

  // 格式化错误
  formatError(error, context = {}) {
    return {
      errorCode: error.code || error.name || 'UNKNOWN_ERROR',
      title: error.message || '未知错误',
      message: error.stack || error.message || '无详细信息',
      severity: this.getSeverity(error),
      stackTrace: error.stack || '',
      context: {
        timestamp: new Date().toISOString(),
        ...context
      }
    };
  }

  // 确定严重级别
  getSeverity(error) {
    if (error.code && error.code.includes('MODULE_NOT_FOUND')) {
      return 'critical';
    }
    if (error.statusCode && error.statusCode >= 500) {
      return 'critical';
    }
    if (error.statusCode && error.statusCode >= 400) {
      return 'high';
    }
    return 'medium';
  }
}

module.exports = { BugReporter };
```

### 6.2 全局错误处理

```javascript
// src/app.js
const { BugReporter } = require('./utils/bug-reporter');
const bugReporter = new BugReporter();

// 捕获未处理异常
process.on('uncaughtException', async (error) => {
  await bugReporter.reportBug(bugReporter.formatError(error, {
    process: 'main',
    type: 'uncaughtException'
  }));
  process.exit(1);
});

// 捕获未处理的Promise拒绝
process.on('unhandledRejection', async (reason, promise) => {
  await bugReporter.reportBug(bugReporter.formatError(reason, {
    process: 'main',
    type: 'unhandledRejection'
  }));
});
```

## 7. 最佳实践

### 7.1 错误收集策略

1. **实时上报**: 致命错误立即上报
2. **批量上报**: 非致命错误收集后批量上报
3. **去重机制**: 避免重复上报相同错误
4. **本地缓存**: 网络异常时缓存错误信息

### 7.2 性能考虑

1. **异步上报**: 不阻塞主业务流程
2. **超时设置**: API调用设置合理超时时间
3. **重试机制**: 失败时进行适当重试
4. **日志记录**: 记录上报结果便于调试

### 7.3 安全考虑

1. **API密钥保护**: 不在代码中硬编码密钥
2. **数据脱敏**: 敏感信息不包含在错误报告中
3. **访问控制**: 确保只有授权服务可以上报错误

## 8. 故障排除

### 8.1 常见问题

1. **认证失败**: 检查API密钥是否正确
2. **连接失败**: 检查BUGer服务是否运行正常
3. **验证错误**: 检查必填字段是否完整
4. **格式错误**: 检查数据格式是否符合规范

### 8.2 调试方法

```bash
# 测试连接
curl -X GET http://localhost:3003/api/bugs/stats \
  -H "X-API-Key: sk_test_xyz123"

# 测试上报
curl -X POST http://localhost:3003/api/bugs \
  -H "X-API-Key: sk_test_xyz123" \
  -H "Content-Type: application/json" \
  -d '{"errorCode":"TEST_001","title":"测试错误","message":"测试消息","severity":"medium"}'
```

## 9. 维护和更新

1. **定期检查**: 定期验证集成是否正常工作
2. **版本兼容**: 关注BUGer API变更
3. **文档更新**: 随着需求变化更新本文档
4. **团队培训**: 确保团队成员了解集成规范

---

*本文档最后更新时间：2025年10月30日*