# MyStocks API 导入 Apifox 完整指南

## 📋 概述

本指南将帮助您将 MyStocks 项目的所有 API（24个API模块）导入到 Apifox 进行统一管理。

**当前API状态**:
- ✅ OpenAPI 3.1.0 规范完整
- ✅ 24个API模块已实现
- ✅ 完整的请求/响应定义
- ✅ API文档已生成（openapi.json, openapi.yaml）

---

## 🚀 快速开始（3种方法）

### 方法1: 通过URL导入（推荐 - 最简单）

**前提条件**: 确保后端服务正在运行

```bash
# 1. 启动后端服务
cd /opt/claude/mystocks_spec/web/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 2. 验证OpenAPI端点可访问
curl http://localhost:8000/openapi.json | jq '.info'
```

**Apifox导入步骤**:

1. **打开Apifox** → 选择目标项目（或创建新项目 "MyStocks API"）

2. **导入数据** → 点击"导入" → 选择"URL导入"

3. **配置导入**:
   ```
   导入方式: URL导入
   URL地址: http://localhost:8000/openapi.json
   数据格式: OpenAPI 3.0
   导入模式: 智能合并（首次导入选"全部覆盖"）
   ```

4. **点击"导入"** → 等待导入完成（约10-30秒）

5. **验证导入结果**:
   - 检查API数量（应有60+个端点）
   - 检查API分组（按功能模块分类）
   - 检查数据模型（Schema）定义

---

### 方法2: 通过文件导入（离线环境）

**适用场景**: 无法访问运行中的服务，或需要离线导入

```bash
# 1. 准备OpenAPI文件（已存在）
ls -lh /opt/claude/mystocks_spec/docs/api/openapi.json
# 文件大小: ~480KB

# 2. 可选：使用YAML格式（更易读）
ls -lh /opt/claude/mystocks_spec/docs/api/openapi.yaml
# 文件大小: ~341KB
```

**Apifox导入步骤**:

1. **打开Apifox** → 选择目标项目

2. **导入数据** → 点击"导入" → 选择"文件导入"

3. **上传文件**:
   ```
   文件路径: /opt/claude/mystocks_spec/docs/api/openapi.json
   或
   文件路径: /opt/claude/mystocks_spec/docs/api/openapi.yaml

   数据格式: OpenAPI 3.0（自动识别）
   导入模式: 全部覆盖（首次）/ 智能合并（更新）
   ```

4. **高级选项**（可选）:
   - ✅ 导入API文档描述
   - ✅ 导入Mock数据
   - ✅ 导入数据模型
   - ✅ 保留原有分组结构

5. **点击"导入"** → 验证导入结果

---

### 方法3: 通过Apifox CLI导入（自动化）

**适用场景**: CI/CD自动化、批量导入、定期同步

**安装Apifox CLI**:
```bash
npm install -g apifox-cli
```

**导入命令**:
```bash
# 使用本地文件导入
apifox import \
  --project-id <你的项目ID> \
  --file /opt/claude/mystocks_spec/docs/api/openapi.json \
  --format openapi \
  --merge-mode smart

# 或使用URL导入
apifox import \
  --project-id <你的项目ID> \
  --url http://localhost:8000/openapi.json \
  --format openapi \
  --merge-mode smart
```

**获取项目ID**:
- 打开Apifox → 项目设置 → 项目信息 → 复制项目ID

---

## 📊 导入后的API结构

导入完成后，您将看到以下API分组结构：

```
MyStocks API (根目录)
├── 🏥 系统管理 (System)
│   ├── GET /health - 健康检查
│   ├── GET /api/system/info - 系统信息
│   └── GET /api/socketio-status - Socket.IO状态
│
├── 🔐 认证授权 (Authentication)
│   ├── POST /api/auth/login - 用户登录
│   ├── POST /api/auth/logout - 用户登出
│   ├── POST /api/auth/refresh - 刷新Token
│   └── GET /api/auth/csrf-token - 获取CSRF Token
│
├── 📊 市场数据 (Market Data)
│   ├── GET /api/market/realtime/{symbol} - 实时行情
│   ├── GET /api/market/kline - K线数据
│   ├── GET /api/market/fund-flow - 资金流向
│   ├── GET /api/market/chip-distribution - 筹码分布
│   └── GET /api/market/etf-analysis - ETF分析
│
├── 📈 市场数据V2 (Market Data V2)
│   ├── GET /api/market/v2/realtime-batch - 批量实时行情
│   ├── GET /api/market/v2/sector-flow - 板块资金流向
│   └── GET /api/market/v2/market-overview - 市场概览
│
├── 🔍 股票搜索 (Stock Search)
│   ├── GET /api/stocks/search - 搜索股票
│   └── GET /api/stocks/info/{symbol} - 股票详情
│
├── 📋 自选股 (Watchlist)
│   ├── GET /api/watchlist - 获取自选股列表
│   ├── POST /api/watchlist/add - 添加自选股
│   └── DELETE /api/watchlist/remove/{symbol} - 删除自选股
│
├── 🤖 问财 (Wencai)
│   ├── POST /api/wencai/query - 问财查询
│   └── GET /api/wencai/hot-queries - 热门查询
│
├── 💾 缓存管理 (Cache Management)
│   ├── GET /api/cache/stats - 缓存统计
│   ├── POST /api/cache/clear - 清除缓存
│   └── POST /api/cache/warmup - 缓存预热
│
├── 📉 策略管理 (Strategy)
│   ├── GET /api/strategy/list - 策略列表
│   ├── POST /api/strategy/create - 创建策略
│   ├── POST /api/strategy/backtest - 策略回测
│   └── GET /api/strategy/performance - 策略绩效
│
├── 📊 指标数据 (Metrics)
│   ├── GET /api/metrics/system - 系统指标
│   └── GET /api/metrics/market - 市场指标
│
├── 🔔 通知管理 (Notifications)
│   ├── GET /api/notifications - 获取通知
│   ├── POST /api/notifications/mark-read - 标记已读
│   └── DELETE /api/notifications/{id} - 删除通知
│
├── 📡 通达信 (TDX)
│   ├── GET /api/tdx/realtime - TDX实时数据
│   └── GET /api/tdx/history - TDX历史数据
│
├── 📝 任务管理 (Tasks)
│   ├── GET /api/tasks - 任务列表
│   ├── POST /api/tasks/create - 创建任务
│   └── GET /api/tasks/{task_id}/status - 任务状态
│
└── 🎯 监控管理 (Monitoring)
    ├── GET /api/monitoring/health - 监控健康检查
    ├── GET /api/monitoring/performance - 性能监控
    └── GET /api/monitoring/alerts - 告警列表
```

**统计数据**:
- 总API端点: 60+
- API模块数: 24个
- 数据模型: 50+个Schema定义
- 认证方式: JWT Bearer Token

---

## ⚙️ 导入后的配置建议

### 1. 配置环境变量

在Apifox中创建环境（开发/测试/生产）：

**开发环境**:
```json
{
  "name": "开发环境",
  "variables": {
    "base_url": "http://localhost:8000",
    "auth_token": "",
    "csrf_token": ""
  }
}
```

**生产环境**:
```json
{
  "name": "生产环境",
  "variables": {
    "base_url": "https://api.mystocks.com",
    "auth_token": "",
    "csrf_token": ""
  }
}
```

### 2. 配置认证流程

**前置脚本**（自动获取Token）:

```javascript
// 1. 获取CSRF Token
const csrfResponse = await pm.sendRequest({
  url: pm.environment.get('base_url') + '/api/auth/csrf-token',
  method: 'GET'
});
pm.environment.set('csrf_token', csrfResponse.json().data.token);

// 2. 登录获取JWT Token
const loginResponse = await pm.sendRequest({
  url: pm.environment.get('base_url') + '/api/auth/login',
  method: 'POST',
  header: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': pm.environment.get('csrf_token')
  },
  body: {
    mode: 'raw',
    raw: JSON.stringify({
      username: 'admin',
      password: 'your_password'
    })
  }
});
pm.environment.set('auth_token', loginResponse.json().data.access_token);
```

### 3. 配置Mock数据

Apifox会自动根据OpenAPI Schema生成Mock数据，您可以：

1. **启用智能Mock**: 自动生成符合规则的测试数据
2. **自定义Mock规则**: 针对特定字段设置Mock规则
3. **使用真实数据**: 导入真实的历史数据作为Mock响应

### 4. 创建测试用例

建议为核心API创建自动化测试：

**示例：市场数据测试套件**
```javascript
// 测试用例1: 实时行情API
pm.test("实时行情API返回正确", function() {
  pm.response.to.have.status(200);
  const data = pm.response.json().data;
  pm.expect(data).to.have.property('symbol');
  pm.expect(data).to.have.property('price');
  pm.expect(data.price).to.be.a('number');
});

// 测试用例2: K线数据验证
pm.test("K线数据格式正确", function() {
  const klines = pm.response.json().data;
  pm.expect(klines).to.be.an('array');
  klines.forEach(k => {
    pm.expect(k).to.have.all.keys('timestamp', 'open', 'high', 'low', 'close', 'volume');
  });
});
```

---

## 🔄 持续同步策略

### 方案1: 手动同步（适用于偶尔更新）

```bash
# 1. 重新生成OpenAPI文档（如果API有变化）
curl http://localhost:8000/openapi.json > /opt/claude/mystocks_spec/docs/api/openapi.json

# 2. 在Apifox中重新导入（选择"智能合并"模式）
```

### 方案2: 自动同步（推荐 - CI/CD集成）

**在项目中添加同步脚本**:

```bash
#!/bin/bash
# scripts/sync_api_to_apifox.sh

# 1. 启动后端服务（如果未运行）
# 2. 导出最新OpenAPI文档
curl -s http://localhost:8000/openapi.json > /tmp/openapi_latest.json

# 3. 使用Apifox CLI同步
apifox import \
  --project-id ${APIFOX_PROJECT_ID} \
  --file /tmp/openapi_latest.json \
  --format openapi \
  --merge-mode smart \
  --token ${APIFOX_API_TOKEN}

echo "✅ API文档已同步到Apifox"
```

**集成到CI/CD**（GitHub Actions示例）:

```yaml
name: Sync API to Apifox

on:
  push:
    branches: [main]
    paths:
      - 'web/backend/app/api/**'

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Start Backend
        run: |
          cd web/backend
          pip install -r requirements.txt
          uvicorn app.main:app --host 0.0.0.0 --port 8000 &
          sleep 10

      - name: Sync to Apifox
        env:
          APIFOX_PROJECT_ID: ${{ secrets.APIFOX_PROJECT_ID }}
          APIFOX_API_TOKEN: ${{ secrets.APIFOX_API_TOKEN }}
        run: |
          bash scripts/sync_api_to_apifox.sh
```

### 方案3: Webhook自动同步

**在FastAPI中添加Webhook端点**:

```python
@app.post("/api/webhooks/apifox-sync")
async def trigger_apifox_sync(background_tasks: BackgroundTasks):
    """触发Apifox同步的Webhook"""
    background_tasks.add_task(sync_to_apifox)
    return {"message": "Sync triggered"}

async def sync_to_apifox():
    """后台任务：同步到Apifox"""
    # 调用Apifox API进行同步
    pass
```

---

## 🧪 验证导入结果

### 检查清单

- [ ] **API数量**: 确认60+个端点全部导入
- [ ] **API分组**: 检查14个功能模块分组正确
- [ ] **数据模型**: 验证50+个Schema定义完整
- [ ] **认证配置**: JWT Bearer Token配置正确
- [ ] **请求参数**: 所有必填参数标记正确
- [ ] **响应示例**: Mock数据生成正常
- [ ] **API描述**: 中文描述显示正确
- [ ] **环境配置**: 开发/生产环境变量配置完成

### 测试核心API

**推荐测试顺序**:

1. **健康检查**: `GET /health` - 验证基础连通性
2. **认证流程**: `POST /api/auth/login` - 验证认证配置
3. **实时行情**: `GET /api/market/realtime/{symbol}` - 验证业务API
4. **批量请求**: `GET /api/market/v2/realtime-batch` - 验证复杂场景

---

## 📚 Apifox高级功能

### 1. 接口测试套件

创建完整的回归测试套件：

```
测试套件: MyStocks核心功能
├── 前置条件: 登录并获取Token
├── 测试用例1: 市场数据完整性测试
├── 测试用例2: 缓存功能测试
├── 测试用例3: 策略回测性能测试
└── 后置清理: 清理测试数据
```

### 2. 性能测试

配置压力测试：

```
场景: 高并发行情请求
- 并发用户: 100
- 持续时间: 60秒
- 目标QPS: 1000
- 断言: 95%响应时间 < 200ms
```

### 3. 数据库集成

连接PostgreSQL数据库进行数据驱动测试：

```sql
-- 示例：从数据库读取测试用的股票代码
SELECT symbol FROM stock_basic
WHERE market = 'A股'
LIMIT 10;
```

### 4. 文档生成

导出精美的API文档：

- **在线文档**: 生成可分享的在线文档链接
- **Markdown**: 导出到项目README
- **PDF**: 导出PDF版本文档
- **HTML**: 生成静态HTML文档站点

---

## 🔧 故障排查

### 问题1: 导入失败 - "格式不支持"

**原因**: OpenAPI版本不兼容

**解决方案**:
```bash
# 检查OpenAPI版本
cat /opt/claude/mystocks_spec/docs/api/openapi.json | jq '.openapi'
# 应显示: "3.1.0"

# 如果Apifox不支持3.1，降级到3.0
# （通常不需要，Apifox支持3.1）
```

### 问题2: API数量不完整

**原因**: 部分API未包含在OpenAPI文档中

**解决方案**:
```python
# 检查main.py中的include_in_schema设置
# 确保所有API路由都设置为include_in_schema=True

@app.get("/api/hidden", include_in_schema=False)  # ❌ 不会导入
@app.get("/api/visible", include_in_schema=True)  # ✅ 会导入
```

### 问题3: 认证配置不生效

**原因**: SecuritySchemes未正确识别

**解决方案**:
```bash
# 检查OpenAPI的securitySchemes定义
cat openapi.json | jq '.components.securitySchemes'

# 应包含JWT Bearer定义
{
  "HTTPBearer": {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT"
  }
}
```

### 问题4: 中文乱码

**原因**: 文件编码问题

**解决方案**:
```bash
# 确认文件编码为UTF-8
file -bi /opt/claude/mystocks_spec/docs/api/openapi.json
# 应显示: application/json; charset=utf-8

# 如有问题，转换编码
iconv -f GBK -t UTF-8 openapi.json > openapi_utf8.json
```

---

## 📞 获取帮助

### Apifox资源
- **官方文档**: https://apifox.com/help/
- **OpenAPI导入指南**: https://apifox.com/help/import-export/openapi/
- **API Key申请**: Apifox设置 → API管理

### MyStocks项目资源
- **API文档**: http://localhost:8000/api/docs
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **项目文档**: `/docs/api/README.md`

### 问题反馈
- **GitHub Issues**: 项目仓库 Issues页面
- **邮件支持**: api@mystocks.com

---

## ✅ 完成检查清单

导入完成后，确认以下项目：

- [ ] 所有API端点已导入（60+个）
- [ ] API分组结构清晰（14个模块）
- [ ] 环境变量配置完成（开发/生产）
- [ ] 认证流程配置正确（JWT + CSRF）
- [ ] Mock数据生成正常
- [ ] 核心API测试通过
- [ ] 测试用例创建完成
- [ ] 文档生成并分享
- [ ] 自动同步脚本配置（可选）
- [ ] 团队成员访问权限配置

---

**恭喜！您已成功将MyStocks项目所有API导入Apifox进行统一管理！** 🎉

现在您可以：
- ✅ 在Apifox中测试和调试所有API
- ✅ 使用Mock数据进行前端开发
- ✅ 自动生成API文档分享给团队
- ✅ 创建自动化测试保证API质量
- ✅ 监控API性能和可用性
