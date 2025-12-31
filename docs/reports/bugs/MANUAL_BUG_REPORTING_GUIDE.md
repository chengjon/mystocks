# BUGer 手工BUG登记使用指南

**更新日期**: 2025-12-30
**版本**: 1.1

---

## 概述

本文档介绍如何在网络不畅时手工登记BUG，并在网络恢复后将其导入BUGer系统。

## 目录结构

```
/opt/iflow/buger/
├── incoming/                    # BUG接收目录（手工登记文件存放处）
│   └── (将 .json 文件放入此目录)
├── processed/
│   ├── success/                 # 成功导入的文件备份
│   └── failed/                  # 导入失败的文件备份
└── tools/maintenance/
    ├── manual-bug-template.json # BUG登记模板（含批量示例）
    ├── import-manual-bugs.js    # 导入脚本
    └── MANUAL_BUG_REPORTING_GUIDE.md  # 本文档
```

---

## 快速开始

```bash
# 1. 复制模板到接收目录
cp tools/maintenance/manual-bug-template.json incoming/today-bugs.json

# 2. 编辑模板（填写你的BUG信息）
vim incoming/today-bugs.json

# 3. 网络恢复后导入
cd /opt/iflow/buger
node tools/maintenance/import-manual-bugs.js -k sk_your_api_key

# 4. 查看结果
ls -la processed/success/   # 成功导入
ls -la processed/failed/    # 失败文件
```

---

## 模板格式说明

### 支持两种格式

| 格式 | 使用场景 | 字段名 | 数量限制 |
|------|----------|--------|----------|
| **单个BUG** | 只有一个BUG需要登记 | `bug` 对象 | 1个 |
| **批量BUG** | 多个BUG一起登记 | `bugs` 数组 | 最多20个 |

### metadata 元数据（建议填写）

| 字段 | 必填 | 说明 |
|------|------|------|
| `version` | 是 | 固定为 `"1.0"` |
| `format` | 是 | 固定为 `"buger-manual-report"` |
| `reportedAt` | 是 | 登记时间，ISO 8601格式，如 `2025-12-30T10:30:00Z` |
| `reporter` | 是 | 登记人姓名或工号 |
| `contact` | 否 | 联系方式（邮箱/电话） |
| `description` | 否 | 备注描述 |

### BUG 字段说明

| 字段 | 必填 | 最大长度 | 说明 |
|------|------|----------|------|
| `errorCode` | 是 | 100 | 错误代码，**必须大写字母、数字、下划线** |
| `title` | 是 | 200 | BUG标题，简明扼要 |
| `message` | 是 | 1000 | 错误详细描述 |
| `stackTrace` | 否 | 5000 | 堆栈跟踪信息 |
| `severity` | 是 | - | 严重程度 |
| `context` | 否 | - | 上下文信息 |

### context 上下文字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `projectName` | 是 | 项目/服务名称 |
| `projectRoot` | 否 | 项目根目录路径 |
| `component` | 否 | 所属模块/组件 |
| `environment` | 否 | 环境：development/staging/production |
| `operatingSystem` | 否 | 操作系统 |
| `nodeVersion` | 否 | Node.js 版本 |
| `browser` | 否 | 浏览器（前端问题填写） |

---

## 严重程度分级

| 级别 | 标识 | 影响范围 | 响应时间 | 示例 |
|------|------|----------|----------|------|
| **critical** | 🔴 崩溃 | 系统不可用 | 立即修复 | 服务启动失败、数据丢失、支付中断 |
| **high** | 🟠 严重 | 核心功能受损 | 4小时内 | 重要功能不可用、性能严重下降 |
| **medium** | 🟡 中等 | 功能异常 | 24小时内 | 非核心功能异常、有 workaround |
| **low** | 🟢 轻微 | 轻微问题 | 下一迭代 | UI显示问题、拼写错误、提示信息不当 |

---

## 填写示例

### 示例1：单个BUG（网络不通时）

```json
{
  "metadata": {
    "version": "1.0",
    "format": "buger-manual-report",
    "reportedAt": "2025-12-30T10:30:00Z",
    "reporter": "张三",
    "contact": "zhangsan@example.com"
  },
  "bug": {
    "errorCode": "ERR_DB_CONNECTION_001",
    "title": "数据库连接超时",
    "message": "尝试连接MySQL数据库时超时，连接池已满，当前连接数: 100",
    "stackTrace": "Error: connect ETIMEDOUT\n    at Connection._handleTimeout (/app/node_modules/mysql2/lib/connection.js:123:15)",
    "severity": "high",
    "context": {
      "projectName": "PaymentService",
      "projectRoot": "/app/payment-service",
      "component": "database",
      "environment": "production",
      "operatingSystem": "Linux",
      "nodeVersion": "v18.19.0"
    }
  }
}
```

### 示例2：批量BUG（每日汇总，推荐）

```json
{
  "metadata": {
    "version": "1.0",
    "format": "buger-manual-report",
    "reportedAt": "2025-12-30T18:00:00Z",
    "reporter": "李四",
    "contact": "lisi@example.com",
    "description": "12月30日测试环境发现的问题汇总"
  },
  "bugs": [
    {
      "errorCode": "ERR_API_TIMEOUT_001",
      "title": "订单服务API超时",
      "message": "查询订单详情接口响应时间超过30秒",
      "severity": "high",
      "context": {
        "projectName": "OrderService",
        "projectRoot": "/app/order-service",
        "component": "api",
        "environment": "staging"
      }
    },
    {
      "errorCode": "ERR_UI_BUTTON_002",
      "title": "提交按钮点击无响应",
      "message": "用户点击提交按钮后无任何反应，控制台无错误",
      "severity": "medium",
      "context": {
        "projectName": "WebAdmin",
        "projectRoot": "/app/web-admin",
        "component": "frontend",
        "environment": "staging",
        "browser": "Firefox 120"
      }
    },
    {
      "errorCode": "ERR_LOG_ROTATE_003",
      "title": "日志轮转配置错误",
      "message": "日志文件超过1GB未进行轮转",
      "severity": "low",
      "context": {
        "projectName": "PaymentService",
        "projectRoot": "/app/payment-service",
        "component": "logging",
        "environment": "production"
      }
    }
  ]
}
```

### 示例3：前端问题

```json
{
  "metadata": {
    "version": "1.0",
    "format": "buger-manual-report",
    "reportedAt": "2025-12-30T14:00:00Z",
    "reporter": "王五",
    "contact": "wangwu@example.com"
  },
  "bug": {
    "errorCode": "ERR_CHART_RENDER_001",
    "title": "ECharts图表在Safari中渲染异常",
    "message": "折线图在Safari 17.0中显示为空白，其他浏览器正常",
    "severity": "medium",
    "context": {
      "projectName": "DataDashboard",
      "projectRoot": "/app/dashboard",
      "component": "charts",
      "environment": "staging",
      "operatingSystem": "macOS",
      "browser": "Safari 17.0"
    }
  }
}
```

### 示例4：移动端问题

```json
{
  "metadata": {
    "version": "1.0",
    "format": "buger-manual-report",
    "reportedAt": "2025-12-30T16:30:00Z",
    "reporter": "赵六",
    "contact": "zhaoliu@example.com"
  },
  "bug": {
    "errorCode": "ERR_MOBILE_SENSOR_001",
    "title": "iOS端陀螺仪数据获取失败",
    "message": "iOS 17.0+ 系统需要用户授权后才能获取陀螺仪数据，当前未做权限请求",
    "severity": "medium",
    "context": {
      "projectName": "ARApp",
      "projectRoot": "/app/ar-app",
      "component": "sensors",
      "environment": "staging",
      "operatingSystem": "iOS 17.2",
      "deviceModel": "iPhone 15 Pro"
    }
  }
}
```

---

## 批量登记最佳实践

### 按项目批量

```json
{
  "metadata": {
    "version": "1.0",
    "reportedAt": "2025-12-30T18:00:00Z",
    "reporter": "测试组",
    "description": "PaymentService 项目回归测试问题汇总"
  },
  "bugs": [
    { "errorCode": "ERR_PAY_001", "title": "支付成功页显示延迟", "message": "...", "severity": "high", "context": { "projectName": "PaymentService", "component": "payment", "environment": "staging" } },
    { "errorCode": "ERR_PAY_002", "title": "退款到账时间超时", "message": "...", "severity": "high", "context": { "projectName": "PaymentService", "component": "refund", "environment": "staging" } },
    { "errorCode": "ERR_PAY_003", "title": "订单号复制按钮失效", "message": "...", "severity": "low", "context": { "projectName": "PaymentService", "component": "ui", "environment": "staging" } },
    { "errorCode": "ERR_PAY_004", "title": "汇率显示精度不足", "message": "...", "severity": "low", "context": { "projectName": "PaymentService", "component": "exchange", "environment": "staging" } }
  ]
}
```

### 按严重程度批量

```json
{
  "metadata": {
    "version": "1.0",
    "reportedAt": "2025-12-30T18:00:00Z",
    "reporter": "开发组",
    "description": "本周高优先级BUG修复清单"
  },
  "bugs": [
    { "errorCode": "ERR_CRIT_001", "title": "服务启动失败", "message": "...", "severity": "critical", "context": { "projectName": "AuthService" } },
    { "errorCode": "ERR_CRIT_002", "title": "用户密码泄露风险", "message": "...", "severity": "critical", "context": { "projectName": "UserService" } },
    { "errorCode": "ERR_HIGH_001", "title": "核心业务流程中断", "message": "...", "severity": "high", "context": { "projectName": "OrderService" } },
    { "errorCode": "ERR_HIGH_002", "title": "第三方支付集成异常", "message": "...", "severity": "high", "context": { "projectName": "PaymentService" } }
  ]
}
```

### 按发现时间批量

```json
{
  "metadata": {
    "version": "1.0",
    "reportedAt": "2025-12-30T22:00:00Z",
    "reporter": "值班工程师",
    "description": "今日值班期间发现的所有问题"
  },
  "bugs": [
    { "errorCode": "ERR_NIGHT_001", "title": "CPU使用率飙升", "message": "...", "severity": "high", "context": { "projectName": "APIGateway" } },
    { "errorCode": "ERR_NIGHT_002", "title": "内存泄漏告警", "message": "...", "severity": "high", "context": { "projectName": "CacheService" } },
    { "errorCode": "ERR_NIGHT_003", "title": "CDN配置更新延迟", "message": "...", "severity": "medium", "context": { "projectName": "CDNManager" } },
    { "errorCode": "ERR_NIGHT_004", "title": "监控面板数据延迟", "message": "...", "severity": "low", "context": { "projectName": "MonitorDashboard" } }
  ]
}
```

---

## 保存文件

将填写完成的JSON文件保存到接收目录：

```bash
# 创建接收目录（如果不存在）
mkdir -p /opt/iflow/buger/incoming

# 命名建议：日期_登记人_数量.json
cp incoming/today-bugs.json incoming/2025-12-30-zhangsan-5bugs.json

# 复制到接收目录
cp incoming/2025-12-30-zhangsan-5bugs.json /opt/iflow/buger/incoming/
```

---

## 导入到系统

### 方式一：命令行参数

```bash
cd /opt/iflow/buger
node tools/maintenance/import-manual-bugs.js \
  --api-key sk_your_api_key \
  --directory /opt/iflow/buger/incoming
```

### 方式二：环境变量

```bash
export BUGER_API_KEY=sk_your_api_key
export INCOMING_DIR=/opt/iflow/buger/incoming
cd /opt/iflow/buger
node tools/maintenance/import-manual-bugs.js
```

### 方式三：指定端口

```bash
node tools/maintenance/import-manual-bugs.js \
  --api-key sk_your_api_key \
  --url http://localhost:3031 \
  --directory /opt/iflow/buger/incoming
```

---

## 查看结果

```bash
# 成功导入的文件
ls -la /opt/iflow/buger/processed/success/

# 导入失败的文件
ls -la /opt/iflow/buger/processed/failed/

# 查看失败原因
cat /opt/iflow/buger/processed/failed/*.json
```

---

## 错误处理

### 常见错误

| 错误信息 | 原因 | 解决方法 |
|----------|------|----------|
| `缺少必需字段` | 缺少 errorCode/title/message/severity | 检查JSON文件完整性 |
| `errorCode 格式无效` | 使用了小写字母或特殊字符 | 改用大写字母、数字、下划线 |
| `severity 无效` | 值不在允许范围内 | 使用 critical/high/medium/low |
| `字段长度超限` | 内容超过最大长度限制 | 缩短相应字段内容 |
| `API 请求失败` | BUGer服务未运行或API Key错误 | 检查服务状态和API Key |
| `Maximum 20 bugs per batch` | 批量超过20个 | 拆分成多个文件 |

### JSON 格式验证

```bash
# 使用 node 验证 JSON 格式
node -e "JSON.parse(require('fs').readFileSync('incoming/my-bugs.json', 'utf8')); console.log('✅ JSON 格式正确')"
```

---

## errorCode 命名规范

推荐使用以下命名格式：

```
ERR_{模块}_{序号}
ERR_{错误类型}_{序号}
```

### 示例

| 错误类型 | 前缀 | 示例 |
|----------|------|------|
| 数据库 | `ERR_DB_` | `ERR_DB_CONNECTION_001` |
| API | `ERR_API_` | `ERR_API_TIMEOUT_001` |
| 认证 | `ERR_AUTH_` | `ERR_AUTH_TOKEN_001` |
| 权限 | `ERR_PERM_` | `ERR_PERM_DENIED_001` |
| UI | `ERR_UI_` | `ERR_UI_RENDER_001` |
| 性能 | `ERR_PERF_` | `ERR_PERF_MEMORY_001` |
| 安全 | `ERR_SEC_` | `ERR_SEC_SQL_INJECT_001` |

---

## 最佳实践

1. **及时登记** - 遇到BUG后立即登记，避免遗忘关键信息
2. **信息完整** - 尽量提供详细的错误信息、复现步骤和上下文
3. **准确分级** - 根据实际影响选择正确的严重程度
4. **批量处理** - 将多个BUG合并到一个文件，减少导入次数
5. **规范命名** - 使用统一的 errorCode 命名规范
6. **描述清晰** - title 一句话说清问题，message 详细描述
7. **包含复现步骤** - 如果有复现步骤，添加到 message 中
8. **定期清理** - 定期清理 processed 目录中的旧文件

---

## 快速参考

```bash
# 查看模板
cat tools/maintenance/manual-bug-template.json

# 验证 JSON 格式
node -e "JSON.parse(require('fs').readFileSync('incoming/my-bugs.json')); console.log('OK')"

# 导入所有文件
node tools/maintenance/import-manual-bugs.js -k sk_your_api_key

# 查看帮助
node tools/maintenance/import-manual-bugs.js --help

# 查看监控
buger -m1    # 基础监控
buger -m2    # Tmux监控
```

---

## 获取 API Key

如果还没有 API Key：

1. 登录 BUGer 管理界面
2. 进入"设置" → "API Keys"
3. 创建新的 API Key（格式：`sk_xxxxx`）

---

## 联系

如有疑问，请联系系统管理员或提交 Issue。
