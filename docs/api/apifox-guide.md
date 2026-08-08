# Apifox 使用指南

> **版本**: 1.0 | **更新日期**: 2026-07-12
> **维护者**: 后端架构
> **合并来源**: `APIFOX_QUICK_START.md` + `APIFOX_IMPORT_GUIDE.md` + `APIFOX_BEGINNER_GUIDE.md`（3 份去重合并）
> **归档分离**: 一次性完成报告 → `archive/apifox-import-success-2025-11-10.md`；旧 MCP 评估 → `archive/apifox-mcp-playwright-legacy.md`

---

## 概览

| 项目 | 信息 |
|------|------|
| 项目地址 | https://app.apifox.com/project/7376246 |
| API 版本 | OpenAPI 3.1.0 |
| 本地 Swagger | http://localhost:8020/api/docs |
| 本地 ReDoc | http://localhost:8020/api/redoc |
| API 模块数 | 24 个 |

---

## 🚀 5 分钟上手

### 1. 访问项目

打开 https://app.apifox.com/project/7376246

### 2. 配置环境变量

在 Apifox →「环境管理」中新建环境（dev / staging / production），配置变量：

| 变量名 | 示例值 | 说明 |
|--------|--------|------|
| `base_url` | `http://localhost:8020` | 后端 API 地址 |
| `auth_token` | `{{auth_token}}` | 登录后自动填充（见认证章节） |
| `csrf_token` | `{{csrf_token}}` | 自动从 cookie 获取 |

### 3. 测试第一个 API

1. 左侧选择 `GET /health`
2. 点击「发送」
3. 预期响应 `200 OK`，body 为 `{"status":"ok"}`

---

## 🔌 API 导入方法

当 API 发生变更时，需重新同步到 Apifox。三种方法按场景选择：

### 方法 1: URL 导入（推荐 - 最简单）

适用：后端服务正在运行。

```bash
# 1. 确认 OpenAPI 端点可访问
curl http://localhost:8020/openapi.json | jq '.info'

# 2. 在 Apifox →「项目设置」→「导入数据」→「URL」
#    输入: http://localhost:8020/openapi.json
#    选择: 智能合并（保留手动配置）
```

### 方法 2: 文件导入（离线环境）

适用：后端未运行或隔离网络。

```bash
# 1. 导出 OpenAPI 文件
http://localhost:8020/openapi.json   # JSON 格式，~480KB
http://localhost:8020/openapi.yaml   # YAML 格式，~341KB

# 2. 在 Apifox →「导入数据」→「文件」选择下载的文件
```

### 方法 3: Apifox CLI 导入（自动化 / CI）

适用：CI/CD 流程中自动同步。

```bash
# 安装 CLI
npm install -g apifox-cli

# 通过本地文件导入
apifox import --file openapi.json --project 7376246

# 或通过 URL 导入
apifox import --url http://localhost:8020/openapi.json --project 7376246
```

### 导入验证清单

- [ ] 218+ 端点完整导入
- [ ] 96+ Schema 完整导入
- [ ] 环境变量 `base_url` 已配置
- [ ] 认证流程已配置（见下节）
- [ ] `/health` 返回 200

---

## 🔐 认证配置

MyStocks API 使用 JWT Bearer + CSRF 双重认证。

### 认证流程（3 步走）

```
配置认证 → 执行登录获取 Token → Token 自动附加到后续请求
```

### 操作步骤

1. 在 Apifox →「项目设置」→「Auth 配置」选择「Bearer Token」
2. 在「登录」接口（`POST /auth/login`）的「Tests」标签页中添加脚本：

```javascript
// 登录成功后自动提取并设置 Token
const response = pm.response.json();
pm.environment.set("auth_token", response.data.access_token);
pm.environment.set("csrf_token", response.data.csrf_token);
```

3. 其他需要认证的接口，在「Headers」中设置 `Authorization: Bearer {{auth_token}}`

---

## 🧪 核心 API 示例

### 1. 获取实时行情

```
GET /api/market/quote/realtime?symbol=000001
```

### 2. 获取 K 线数据

```
GET /api/market/kline?symbol=000001&period=daily&start_date=2025-01-01&end_date=2025-07-01
```

### 3. 批量实时行情

```
POST /api/market/quote/batch
Body: {"symbols": ["000001", "000002", "600000"]}
```

### 4. 行业资金流向

```
GET /api/market/flow/industry?date=2025-07-01
```

---

## 🔄 持续同步策略

| 方案 | 适用场景 | 方法 |
|------|---------|------|
| 手动同步 | 偶尔更新 | 重新导入 + 智能合并 |
| CI 自动同步 | 频繁迭代 | `scripts/sync_api_to_apifox.sh` |
| Webhook 同步 | 实时同步 | GitHub webhook 触发 |

### CI 自动同步脚本

```bash
# 1. 启动后端服务（如未运行）
uvicorn app.main:app --port 8020 &

# 2. 导出最新 OpenAPI
curl -s http://localhost:8020/openapi.json > openapi.json

# 3. 同步到 Apifox
apifox import --file openapi.json --project 7376246
```

---

## 📚 高级功能

### 接口测试套件

在 Apifox →「自动化测试」中创建用例链：登录 → 查询 → 下单 → 校验

### 性能测试

在接口详情页 →「性能测试」配置 QPS / 并发数，定位高负载瓶颈

### 数据驱动测试

使用 CSV / JSON 数据集做批量参数化测试

### Mock 数据

在接口详情页 →「Mock」配置模拟响应，前端可在 API 未就绪时并行开发

---

## 🔧 故障排查

### 401 Unauthorized

- Token 过期 → 重新登录
- `Authorization` 头拼写错误 → 确认 `Bearer {{auth_token}}`

### 403 CSRF Token Invalid

- CSRF 未配置 → 确认登录脚本已提取 `csrf_token`
- Cookie 未携带 → 在 Apifox 中开启「自动携带 Cookie」

### 404 Not Found

- API 路径拼写错误 → 对照 Swagger 确认
- 路由未注册 → 检查 `main.py` 的 `include_in_schema=True`

### 500 Internal Server Error

- 查看后端日志 `pm2 logs` 或 `uvicorn` 控制台
- 确认数据库服务正常

### 中文乱码

- 确认响应头 `Content-Type: application/json; charset=utf-8`
- 确认文件编码为 UTF-8

### 导入格式不支持

- 检查 OpenAPI 版本（应为 3.1.0）
- 如 Apifox 不支持 3.1，降级到 3.0 后导入

---

## ✅ 完成检查清单

### 基础（无需认证）
- [ ] 环境变量已配置
- [ ] `/health` 返回 200
- [ ] `/api/market/quote/realtime` 正常响应

### 认证流程
- [ ] 登录接口成功获取 Token
- [ ] Token 自动附加到业务接口
- [ ] CSRF 双重认证已配置

### 业务 API
- [ ] K 线接口正常返回
- [ ] 批量行情接口正常返回
- [ ] 资金流向接口正常返回

### 进阶
- [ ] CI 同步脚本已配置
- [ ] 自动化测试套件已创建
- [ ] Mock 数据已配置（用于前端联调）

---

## 📚 资源链接

| 资源 | 链接 |
|------|------|
| Apifox 官方文档 | https://docs.apifox.com |
| MyStocks Swagger UI | http://localhost:8020/api/docs |
| MyStocks ReDoc | http://localhost:8020/api/redoc |
| 同步脚本 | `scripts/sync_api_to_apifox.sh` |
| API 契约源文件 | [contracts/](contracts/) |
