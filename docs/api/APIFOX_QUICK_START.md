# Apifox 快速开始指南

> **使用说明**:
> 本文件是 Apifox 工具快速上手指南，不是当前 API 契约、当前测试门禁或仓库共享规则的唯一事实来源。
> 当前 API 单一事实来源请优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md`，以及实际导出的 `/openapi.json`。
>
> 文内 Apifox 项目地址、已导入数量、环境变量和认证脚本应视为工具接入快照；若与当前 Apifox 项目或真实接口不一致，应以后者为准。

## 🚀 5分钟快速上手

### 1. 访问项目

**项目地址**: https://app.apifox.com/project/7376246

已导入内容：
- ✅ 218 个 API 端点
- ✅ 96 个数据模型
- ✅ 25 个接口目录
- ✅ 完整的请求/响应示例

---

## 📝 第一次使用

### 步骤1: 配置环境

1. 点击顶部的 **环境选择器**
2. 新建环境 "本地开发"
3. 添加环境变量：

```json
{
  "base_url": "http://localhost:8020",
  "auth_token": "",
  "csrf_token": ""
}
```

### 步骤2: 测试第一个 API

1. 在左侧选择 **系统管理** → **健康检查**
2. 点击 **发送**
3. 查看响应结果

### 步骤3: 配置认证

#### 自动获取 Token（推荐）

在 **环境设置** → **前置脚本** 中添加：

```javascript
// 自动获取 CSRF Token 和 JWT Token
pm.sendRequest({
  url: pm.environment.get('base_url') + '/api/auth/csrf-token',
  method: 'GET'
}, (err, res) => {
  if (!err) {
    const csrf = res.json().data.token;
    pm.environment.set('csrf_token', csrf);

    // 使用 CSRF Token 登录
    pm.sendRequest({
      url: pm.environment.get('base_url') + '/api/auth/login',
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrf
      },
      body: {
        mode: 'raw',
        raw: JSON.stringify({
          username: 'admin',
          password: 'your_password'
        })
      }
    }, (err, res) => {
      if (!err) {
        const token = res.json().data.access_token;
        pm.environment.set('auth_token', token);
      }
    });
  }
});
```

#### 手动获取 Token

**步骤 A: 获取 CSRF Token**
```http
GET {{base_url}}/api/auth/csrf-token
```

复制响应中的 `data.token`，保存到环境变量 `csrf_token`

**步骤 B: 登录获取 JWT Token**
```http
POST {{base_url}}/api/auth/login
Content-Type: application/json
X-CSRF-Token: {{csrf_token}}

{
  "username": "admin",
  "password": "your_password"
}
```

复制响应中的 `data.access_token`，保存到环境变量 `auth_token`

---

## 🧪 常用功能

### 1. 测试单个 API

1. 在左侧目录中选择 API
2. 查看 **请求参数** 和 **响应示例**
3. 填写参数（使用环境变量如 `{{base_url}}`）
4. 点击 **发送**
5. 查看响应结果

### 2. 批量测试

1. 点击 **测试管理**
2. 新建测试套件
3. 添加测试用例
4. 设置断言条件
5. 运行测试套件

### 3. 使用 Mock 数据

1. 选择任意 API
2. 点击 **Mock**
3. 复制 Mock URL
4. 在前端代码中使用 Mock URL

### 4. 生成代码

1. 选择 API
2. 点击 **代码生成**
3. 选择语言（Python, JavaScript, Java, Go...）
4. 复制代码到项目中

### 5. 导出文档

1. 点击右上角 **⋯** → **导出**
2. 选择格式（Markdown, HTML, PDF）
3. 下载文档

---

## 📚 核心 API 示例

### 1. 获取实时行情

```http
GET {{base_url}}/api/market/realtime/000001
Authorization: Bearer {{auth_token}}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "symbol": "000001",
    "name": "平安银行",
    "price": 12.34,
    "change": 0.12,
    "change_pct": 0.98,
    "volume": 1234567,
    "timestamp": "2025-11-10 14:30:00"
  }
}
```

### 2. 获取K线数据

```http
GET {{base_url}}/api/market/kline?symbol=000001&period=daily&limit=100
Authorization: Bearer {{auth_token}}
```

### 3. 批量实时行情

```http
GET {{base_url}}/api/market/v2/realtime-batch?symbols=000001,000002,600000
Authorization: Bearer {{auth_token}}
```

### 4. 行业资金流向

```http
GET {{base_url}}/api/market/v3/fund-flow?industry_type=sw_l1&limit=10
Authorization: Bearer {{auth_token}}
```

---

## 🔧 进阶技巧

### 1. 自定义请求头

在环境中添加全局请求头：

```json
{
  "headers": {
    "User-Agent": "MyStocks-Client/1.0",
    "X-Request-ID": "{{$guid}}"
  }
}
```

### 2. 数据驱动测试

连接数据库进行参数化测试：

1. 在 **数据库** 中添加 PostgreSQL 连接
2. 在测试用例中使用 SQL 查询
3. 使用查询结果作为测试参数

### 3. 性能测试

1. 点击 **性能测试**
2. 配置并发用户数、持续时间
3. 设置性能目标（如 95% 响应时间 < 200ms）
4. 运行压力测试

### 4. 自动化 CI/CD

使用 Apifox CLI 集成到 CI/CD：

```bash
# 安装 Apifox CLI
npm install -g apifox-cli

# 运行测试套件
apifox run \
  --project-id 7376246 \
  --token APS-kN74RMte5panv5lPUjutEmulUiZEvyRh \
  --env local \
  --test-suite "MyStocks核心功能测试"
```

---

## 📖 API 分组结构

```
MyStocks API
├── 🏥 系统管理
│   ├── GET /health - 健康检查
│   ├── GET /api/system/info - 系统信息
│   └── GET /api/socketio-status - Socket.IO状态
│
├── 🔐 认证授权
│   ├── POST /api/auth/login - 登录
│   ├── POST /api/auth/logout - 登出
│   ├── POST /api/auth/refresh - 刷新Token
│   └── GET /api/auth/csrf-token - 获取CSRF Token
│
├── 📊 市场数据
│   ├── 实时行情 (GET /api/market/realtime/{symbol})
│   ├── K线数据 (GET /api/market/kline)
│   ├── 资金流向 (GET /api/market/fund-flow)
│   ├── 筹码分布 (GET /api/market/chip-distribution)
│   └── ETF分析 (GET /api/market/etf-analysis)
│
├── 📈 市场数据 V2
│   ├── 批量实时行情 (GET /api/market/v2/realtime-batch)
│   ├── 板块资金流向 (GET /api/market/v2/sector-flow)
│   └── 市场概览 (GET /api/market/v2/market-overview)
│
├── 🏭 市场数据 V3
│   └── 行业资金流向 (GET /api/market/v3/fund-flow)
│
├── 🔍 股票搜索
│   ├── 搜索股票 (GET /api/stocks/search)
│   └── 股票详情 (GET /api/stocks/info/{symbol})
│
├── 📋 自选股
│   ├── 获取自选股 (GET /api/watchlist)
│   ├── 添加自选股 (POST /api/watchlist/add)
│   └── 删除自选股 (DELETE /api/watchlist/remove/{symbol})
│
└── ... 更多模块
```

---

## 🆘 常见问题

### Q1: 为什么返回 401 未授权？

**A**: 需要先登录获取 JWT Token，然后在请求头中添加：
```
Authorization: Bearer {{auth_token}}
```

### Q2: CSRF Token 如何使用？

**A**: 对于所有 POST/PUT/DELETE 请求，需要：
1. 先调用 `/api/auth/csrf-token` 获取 token
2. 在请求头中添加 `X-CSRF-Token: {{csrf_token}}`

### Q3: Mock 数据如何启用？

**A**:
1. 点击 API → Mock
2. 复制 Mock URL
3. 在前端代码中替换真实 API URL 为 Mock URL

### Q4: 如何批量测试所有 API？

**A**:
1. 创建测试套件
2. 添加所有需要测试的 API
3. 配置前置脚本（自动登录）
4. 运行测试套件

### Q5: 响应时间过长怎么优化？

**A**:
1. 使用性能测试找出慢接口
2. 检查数据库查询
3. 启用缓存
4. 优化数据传输（压缩、分页）

---

## 📞 获取帮助

### Apifox 资源
- **官方文档**: https://apifox.com/help/
- **视频教程**: https://apifox.com/help/video/
- **社区论坛**: https://community.apifox.com/

### MyStocks 资源
- **API 文档**: http://localhost:8020/api/docs
- **导入指南**: `APIFOX_IMPORT_GUIDE.md`
- **成功报告**: `APIFOX_IMPORT_SUCCESS.md`

---

## ✅ 完成检查清单

- [ ] 配置本地开发环境
- [ ] 测试健康检查 API
- [ ] 配置自动认证脚本
- [ ] 测试实时行情 API
- [ ] 测试K线数据 API
- [ ] 创建测试套件
- [ ] 启用 Mock 服务
- [ ] 生成 API 文档
- [ ] 配置 CI/CD 自动化测试

---

**快速访问**: https://app.apifox.com/project/7376246

开始探索您的 218 个 API 端点吧！ 🎉
