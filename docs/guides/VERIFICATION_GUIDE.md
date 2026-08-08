# MyStocks 项目验证指南：从零确认"功能全跑通"

> **版本**: 1.0 | **适用**: 首次搭建/回归验证/上线前检查
> **核心理念**: 从外到内、从简到繁、逐层递进，每一步都产出可量化的证据

---

## 总览：六层验证金字塔

```
                    ╱  P0 质量门禁  ╲           ← Level 5: CI 全通道
                   ╱   36 条 CI 管道   ╲
                  ╱  全量 Playwright E2E  ╲      ← Level 4: 端到端
                 ╱   85+ 个 E2E 测试用例    ╲
                ╱   后端集成测试              ╲   ← Level 3: 集成
               ╱   前端类型检查 + 前端集成测试   ╲
              ╱   后端单元测试 (pytest)          ╲ ← Level 2: 单测
             ╱   前端单元测试 (vitest)             ╲
            ╱   健康检查 + 冒烟测试 (23 项)         ╲ ← Level 1: 冒烟
           ╱   环境就绪 + 配置完整性 + 端口可达性    ╲ ← Level 0: 环境
```

**建议执行顺序**：从 Level 0 爬到 Level 5，任何一层失败先停下来修，不要跳过。

---

## Level 0：环境就绪检查（10 分钟）

### 0.1 依赖完整性

```bash
# Python 版本
python3 --version          # 预期: Python 3.12.x

# Node.js 版本
node --version             # 预期: v18.x+
npm --version

# PM2 进程管理器
pm2 --version

# Docker 可选
docker --version
docker compose version
```

### 0.2 项目配置文件完整性

```bash
# 检查关键配置文件是否存在
ls -la .env                 # 环境变量（必需）
ls -la pyproject.toml       # Python 项目配置
ls -la package.json         # 前端项目配置（根目录）
ls -la web/frontend/package.json  # 前端依赖
ls -la web/backend/requirements.txt  # 后端依赖
ls -la config/ecosystem.config.js    # PM2 后端配置
ls -la config/ecosystem.test.config.js  # PM2 测试配置
ls -la playwright.config.ts  # Playwright E2E 配置
ls -la pytest.ini            # Pytest 配置
```

### 0.3 关键端口可用性

```bash
# 确认端口未被占用
for port in 8020 3020 3000 9090 6379; do
  if lsof -i :$port > /dev/null 2>&1; then
    echo "⚠️  端口 $port 已被占用"
  else
    echo "✅ 端口 $port 可用"
  fi
done
```

**端口规划**:
| 端口 | 服务 | 说明 |
|------|------|------|
| 8020 | 后端 API (FastAPI) | 主服务 |
| 3020 | 前端 (Vite) | 开发/测试端口 |
| 3000 | Grafana | 监控面板 |
| 9090 | Prometheus | 指标收集 |
| 6379 | Redis | 缓存/会话 |

### 0.4 环境变量模板

确保 `.env` 包含（无 `.env` 时从 `.env.example` 复制）：

```bash
# 最小必需变量
BACKEND_PORT=8020
FRONTEND_PORT=3020
FRONTEND_BACKUP_PORT=3021
DATABASE_URL=postgresql://user:pass@localhost:5432/mystocks
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your-secret-key
```

---

## Level 1：冒烟测试（15 分钟）

### 1.1 启动服务

```bash
# 清理旧进程
pm2 delete all 2>/dev/null || true

# 启动 PM2 服务（后端 + 前端）
pm2 start ecosystem.test.config.js

# 等待服务就绪（约 30 秒）
sleep 30

# 确认所有服务都在线
pm2 list
```

服务启动后，预期看到：
```
┌─────┬──────────────────────┬──────────┐
│ id  │ name                 │ status   │
├─────┼──────────────────────┼──────────┤
│ 0   │ mystocks-backend     │ online   │
│ 1   │ mystocks-frontend    │ online   │
└─────┴──────────────────────┴──────────┘
```

### 1.2 后端健康检查

```bash
# 基本健康探针
curl -s http://localhost:8020/health

# 就绪探针（验证数据库连通性等）
curl -s http://localhost:8020/api/health/ready

# 预期响应:
# {"status":"healthy","database":"connected","redis":"connected","timestamp":"2026-07-29T..."}
```

### 1.3 运行冒烟测试（23 项检查）

```bash
python3 smoke_test.py
```

**自动覆盖**:
- 2 项服务进程检查 (pm2 list)
- 1 项登录认证
- 15 项后端 API (Dashboard / 实时行情 / K 线 / 龙虎榜 / 板块 / 概念 / 资金流 / 自选 / 股票 / 策略 / 信号 / 头寸 / 健康 / 详情 / 指标)
- 5 项前端页面 (首页 / Dashboard / 实时行情 / 股票列表 / 股票详情)

**预期结果**:
```
=======================================================
  通过: 23/23
  状态: ✅ 冒烟通过
=======================================================
```

> **如果冒烟失败**: 先修通登录或健康检查，它们是所有后续测试的基础。

---

## Level 2：单元测试（30 分钟）

### 2.1 后端 Python 单元测试

```bash
# 仅跑单元测试（标记为 unit 的测试）
pytest -m unit -v --tb=short

# 或指定路径跑
pytest tests/unit/ -v --tb=short

# 查看覆盖率报告
pytest --cov=src --cov=web/backend/app --cov-report=term-missing
```

**关键指标**:
| 指标 | 门槛 | 建议值 |
|------|------|--------|
| 通过率 | ≥95% | 目标 100% |
| 覆盖率 | ≥30% (CI 门禁) | 建议 ≥80% |

> 注: 有些测试可能需要数据库连接（标记为 `database` 或 `integration`）。纯 `unit` 测试应无需外部依赖。

### 2.2 前端单元测试

```bash
cd web/frontend

# 运行所有前端单元测试（Vitest）
npm run test

# 带覆盖率
npm run test:coverage

# 监视模式（开发用）
npm run test:watch
```

### 2.3 前端类型检查

```bash
cd web/frontend

# TypeScript 类型检查（无实质性构建）
vue-tsc --noEmit

# 或走完整流程（生成类型后校验 + 类型冲突检测）
npm run type:build     # = generate-types + type:validate + type-check
```

**预期**: 无类型错误退出（exit code 0）

---

## Level 3：集成测试（45 分钟）

### 3.1 后端集成测试

```bash
# 后端集成测试（需要数据库服务运行中）
pytest -m integration -v

# 特定模块集成测试
pytest tests/integration/test_api_endpoints.py -v
pytest tests/integration/test_tdengine_integration.py -v
pytest tests/integration/test_postgresql_integration.py -v
pytest tests/integration/test_dashboard_api.py -v
```

### 3.2 数据流集成测试

```bash
# 数据源切换测试
pytest tests/integration/test_datasource_switching.py -v

# 三层链路集成（Core -> Service -> API）
pytest tests/integration/test_three_layer_integration.py -v

# API 接口对齐验证
pytest tests/api_contract_tests.py -v
```

### 3.3 前端集成测试

```bash
cd web/frontend

# 前端 API layer 测试
npx vitest run tests/unit/api/

# 前端 Store 集成测试
npx vitest run tests/unit/stores/
```

### 3.4 API 契约验证

```bash
# 契约测试（对比 OpenAPI 规范与代码实现）
pytest -m contract_test -v

# API File Level 测试
pytest tests/file_level/ -v
```

---

## Level 4：端到端测试（E2E，60 分钟）

### 4.1 Playwright E2E 冒烟

```bash
# 方式一：自动启动服务后跑 E2E（推荐）
bash scripts/run_e2e_pm2.sh

# 方式二：如果服务已在运行，直接跑
cd tests/e2e
npx playwright test --config=playwright.config.ts
```

### 4.2 按功能域逐个验证

```bash
# 市场行情（1-实时行情 / K 线 / 龙虎榜）
npx playwright test tests/e2e/market-data.spec.ts
npx playwright test tests/e2e/market-page.spec.ts
npx playwright test tests/e2e/technical-analysis.spec.ts

# 数据分析（板块 / 概念 / 资金流）
npx playwright test tests/e2e/industry-concept-integration.spec.js
npx playwright test tests/e2e/market-view-integration.spec.js

# 策略管理（策略 / 回测）
npx playwright test tests/e2e/strategy-management.spec.ts
npx playwright test tests/e2e/strategy-management-page.spec.ts
npx playwright test tests/e2e/backtest-analysis.spec.ts

# 交易管理（头寸 / 交易）
npx playwright test tests/e2e/trade-management.spec.ts
npx playwright test tests/e2e/trade-management-page.spec.ts
npx playwright test tests/e2e/trade-management-integration.spec.js

# 风险管理（监控 / 告警）
npx playwright test tests/e2e/risk-monitor.spec.ts
npx playwright test tests/e2e/risk-monitor-page.spec.ts
npx playwright test tests/e2e/risk-monitor-integration.spec.js

# 仪表盘 / 综合
npx playwright test tests/e2e/dashboard.spec.ts
npx playwright test tests/e2e/dashboard-page.spec.ts
npx playwright test tests/e2e/auth.spec.ts
npx playwright test tests/e2e/settings.spec.ts
npx playwright test tests/e2e/settings-page.spec.ts
```

### 4.3 综合性 E2E 链路测试

```bash
# 全链路: 登录 -> 行情 -> 策略 -> 回测 -> 交易 -> 风控
npx playwright test tests/e2e/mystocks-comprehensive-e2e.spec.js
npx playwright test tests/e2e/mystocks-comprehensive-api.spec.js

# 业务数据对齐验证
npx playwright test tests/e2e/business-api-data-alignment.spec.js
npx playwright test tests/e2e/business-driven-api-tests.spec.js
```

### 4.4 Web 可用性验证

```bash
# 可访问性 / 响应式 / 白屏修复验证
npx playwright test tests/e2e/web-usability-tests.spec.js
npx playwright test tests/e2e/white-screen-fix-verify.spec.ts
npx playwright test tests/e2e/navigation-consistency.spec.ts
```

**E2E 通过标准**: 所有套件通过率 ≥95%，关键路径（认证/行情/交易）100% 通过。

---

## Level 5：CI 质量门禁全通道（自动执行）

### 5.1 本地模拟 CI 全通道

```bash
# 本地 CI 快速检查（约 5 分钟）
bash scripts/dev/ci/local_ci_check.sh
python3 scripts/ci/run_local_ci.py --quick

# 完整门口模拟（约 15-20 分钟，取决于硬件）
cd .github/workflows
# 按顺序模拟关键门禁
```

### 5.2 36 条 CI 管道（GitHub Actions）

项目已配置 **36 个 CI 工作流**，运行于 `.github/workflows/`：

| 优先级 | 工作流 | 门禁级别 | 通过要求 |
|--------|--------|----------|----------|
| P0 | `p0-quality-gate.yml` | **阻塞** | 必须 100% |
| P0 | `code-quality.yml` | **阻塞** | Black/MyPy/Ruff/Bandit 全通过 |
| P0 | `e2e-testing.yml` | **阻塞** | E2E ≥95% |
| P1 | `frontend-testing.yml` | 重要 | Vitest + vue-tsc + 审计 |
| P1 | `contract-testing.yml` | 重要 | 契约一致性 |
| P1 | `security-testing.yml` | 重要 | 安全扫描无 CRITICAL |
| P2 | `comprehensive-testing.yml` | 建议 | AI/混沌/性能/安全 |
| P2 | `performance-testing.yml` | 建议 | API P95 ≤300ms |
| P2 | `visual-testing.yml` | 建议 | 视觉回归 |
| — | 其余 27 个 | 按需 | — |

### 5.3 P0 质量门禁详解（阻塞项）

P0 门禁 `p0-quality-gate.yml` 在 **PR 到 main/develop** 和 **push 到 main** 时触发，包含：

| 门禁步骤 | 检查内容 | 失败后果 |
|----------|----------|----------|
| Pylint Errors | Error 级别问题 | ❌ 阻塞合并 |
| MyPy Strict | Python 类型错误 | ❌ 阻塞合并 |
| Ruff Critical | 严重代码风格违规 | ❌ 阻塞合并 |
| Bandit High | 高安全风险 | ❌ 阻塞合并 |
| Safety Check | 依赖漏洞 (CRITICAL/HIGH) | ❌ 阻塞合并 |
| Vitest | 前端单测 | ❌ 阻塞合并 |
| vue-tsc | 前端类型 | ❌ 阻塞合并 |
| Playwright | E2E 冒烟 | ❌ 阻塞合并 |

---

## 十功能域逐个验证清单

基于 `docs/FUNCTION_TREE.md` 的 11 域，以下验证清单可按域逐个确认：

### 01-市场数据与行情（完成度 95%）

| 检查项 | 验证方式 | 预期 |
|--------|----------|------|
| TDX 实时行情 | API: `GET /api/v1/market/quotes?limit=3` | 返回 200 + 股票报价 |
| 实时行情前端 | 访问 `/market/realtime` | 页面加载，数据表格显示 |
| K 线数据 | API: `GET /api/v1/market/kline?symbol=000001&interval=1d&limit=50` | 返回 OHLCV 数组 |
| K 线前端 | 访问 `/market/technical` | K 线图表渲染 |
| 龙虎榜 | API: `GET /api/v1/market/lhb?limit=3` | 返回龙虎榜数据 |
| 资金流向 | API: `GET /api/akshare/market/fund-flow/hsgt-summary?...` | 返回资金流数据 |
| WebSocket 推送 | 连接 `ws://localhost:8020/ws/market/quotes` | 接收实时行情推送 |
| 多数据源切换 | 配置 `adapter_priority_config.yaml` | 主源失败自动切换 |

### 02-技术分析与指标（完成度 90%）

| 检查项 | 验证方式 | 预期 |
|--------|----------|------|
| 指标计算 | API: `GET /api/v1/technical/000001/indicators` | 返回 MA/RSI/MACD 等 |
| 指标注册表 | API: `GET /api/v1/indicators/registry` | 列出所有可用指标 |
| 前端技术分析 | 访问技术分析页面 | Tab 切换 + 指标叠加 |
| 十字光标 | 悬停 K 线图 | 显示交互十字线 |

### 03-策略管理与回测（完成度 85%）

| 检查项 | 验证方式 | 预期 |
|--------|----------|------|
| 策略 CRUD | API: `POST/GET/PUT/DELETE /api/v1/strategies/*` | 完整增删改查 |
| 策略克隆 | API: `POST /api/v1/strategies/{id}/clone` | 深拷贝新策略 |
| 创建回测 | API: `POST /api/v1/backtests` | 回测成功执行 |
| 回测指标 | API: `GET /api/v1/backtests/{id}/metrics` | 返回 Sharpe/MDD/收益率 |
| 前端策略页 | 访问 `/strategy/repo` | 策略管理页面就绪 |
| 前端回测页 | 访问 `/strategy/backtest` | 回测配置 + 结果展示 |

### 04-风险管理与监控（完成度 80%）

| 检查项 | 验证方式 | 预期 |
|--------|----------|------|
| 风险概览 | API: `GET /api/risk-management/*` | 返回风险指标 |
| 止损雷达 | API: `GET /api/risk_v31/stop_loss` | 止损监控就绪 |
| 告警中心 | 访问 `/risk/alerts` | 告警列表展示 |
| 组合盈亏 | 访问 `/risk/pnl` | 盈亏图表显示 |

### 05-投资组合与交易（完成度 70%）

| 检查项 | 验证方式 | 预期 |
|--------|----------|------|
| 交易下单 | API: `POST /api/v1/trade/order` | 订单创建成功 |
| 持仓查询 | API: `GET /api/v1/trade/positions` | 返回持仓数据 |
| 委托查询 | API: `GET /api/v1/trade/orders` | 返回委托列表 |
| 交易终端 | 访问 `/trade/terminal` | 交易面板可用 |
| 持仓透视 | 访问 `/trade/portfolio` | 持仓展示 |

### 06-监控与告警（完成度 75%）

| 检查项 | 验证方式 | 预期 |
|--------|----------|------|
| 健康检查 | `curl http://localhost:8020/health` | 返回 healthy |
| 就绪探针 | `curl http://localhost:8020/api/health/ready` | DB/Redis 连通 |
| Prometheus | 访问 `http://localhost:9090/targets` | 指标采集端点在线 |
| Grafana | 访问 `http://localhost:3000` | 面板数据展示 |

### 07-高级分析与 AI（完成度 50%，实验性）

| 检查项 | 验证方式 | 预期 |
|--------|----------|------|
| GPU 回测 | GPU 环境下测试 | 15-44 倍加速 |
| AI 预测 | API: `GET /api/ai/*` | 预测结果 |
| 量化因子 | API: 因子查询 | 因子数据 |

### 08-系统管理与配置（完成度 85%）

| 检查项 | 验证方式 | 预期 |
|--------|----------|------|
| 登录认证 | API: `POST /api/v1/auth/login` | 返回 JWT Token |
| Token 刷新 | API: `POST /api/v1/auth/refresh` | 新 Token |
| 系统状态 | API: `GET /api/v1/system/status` | 系统运行状态 |
| CSRF 防护 | 非 GET 请求携带 CSRF Token | 403 阻断无 Token 请求 |

### 09-数据存储与管理（完成度 90%）

| 检查项 | 验证方式 | 预期 |
|--------|----------|------|
| TDengine 连通 | `python scripts/database/check_tdengine_tables.py` | 表列全部存在 |
| PostgreSQL 连通 | `python scripts/database/check_postgresql_tables.py` | 表列全部存在 |
| 表管理 | 配置 `table_config.yaml` | 自动建表/迁移 |

### 10-公告与信息（完成度 80%）

| 检查项 | 验证方式 | 预期 |
|--------|----------|------|
| 公告 API | API: `GET /api/v1/announcement` | 返回公告数据 |
| 前端公告 | 访问公告页面 | 公告列表展示 |

---

## 验证结果报告模板

执行完成后，请按以下模板记录验证结果：

```markdown
# 验证结果报告 — [日期]

## 环境信息
- 操作系统: xxx
- Python 版本: 3.12.x
- Node.js 版本: v18.x
- PM2 版本: x.x.x
- 数据库状态: TDengine [✅/❌] | PostgreSQL [✅/❌]
- Redis: [✅/❌]

## 各层验证结果

| 层级 | 用例数 | 通过 | 失败 | 通过率 | 状态 |
|------|--------|------|------|--------|------|
| L0-环境就绪 | N | N | 0 | 100% | ❓ |
| L1-冒烟测试 | 23 | N | 0 | xx% | ❓ |
| L2-单元测试 | N | N | 0 | xx% | ❓ |
| L3-集成测试 | N | N | 0 | xx% | ❓ |
| L4-E2E测试 | N | N | 0 | xx% | ❓ |

## 功能域验证清单

| 功能域 | 完成度 | 关键 API (通过/总数) | 前端页面 (通过/总数) | 状态 |
|--------|--------|---------------------|---------------------|------|
| 01-市场数据与行情 | 95% | n/n | n/n | ❓ |
| 02-技术分析与指标 | 90% | n/n | n/n | ❓ |
| 03-策略管理与回测 | 85% | n/n | n/n | ❓ |
| 04-风险管理与监控 | 80% | n/n | n/n | ❓ |
| 05-投资组合与交易 | 70% | n/n | n/n | ❓ |
| 08-系统管理与配置 | 85% | n/n | n/n | ❓ |
| 09-数据存储与管理 | 90% | n/n | — | ❓ |

## 已知问题
- [问题描述] — [影响域] — [严重程度] — [原因/链接]

## 结论
[✅ 全部通过 / ⚠️ 次要问题 / ❌ 阻塞项]
```

---

## 一键快速验证脚本

将以下内容保存为 `quick_verify.sh` 并运行：

```bash
#!/bin/bash
set -euo pipefail

echo "=================================================="
echo "  MyStocks 快速验证 — $(date)"
echo "=================================================="

# 1. 检查服务
echo ""
echo "--- [L0] 环境检查 ---"
python3 --version && node --version && npm --version

echo ""
echo "--- [L1] 服务状态 ---"
pm2 list 2>/dev/null | grep -E "online|offline" || echo "PM2 未启动"

echo ""
echo "--- [L1] 健康检查 ---"
curl -s http://localhost:8020/health | python3 -m json.tool 2>/dev/null || echo "后端不可达"
curl -s -o /dev/null -w '前端 HTTP 状态: %{http_code}\n' http://localhost:3020 2>/dev/null || echo "前端不可达"

echo ""
echo "--- [L1] 冒烟测试 ---"
python3 smoke_test.py 2>/dev/null && echo "冒烟通过" || echo "冒烟失败"

echo ""
echo "--- [L2] 后端单元测试 ---"
pytest -m unit -q --tb=short --no-header 2>/dev/null && echo "单元测试通过" || echo "单元测试有失败"

echo ""
echo "--- [L2] 前端类型检查 ---"
cd web/frontend && vue-tsc --noEmit 2>/dev/null && echo "类型检查通过" || echo "类型检查有错误"
cd ../..

echo ""
echo "=================================================="
echo "  快速验证完成"
echo "=================================================="
```

---

## 常见问题排查

### 后端启动失败
- **检查 `.env`**: 是否包含所有必需的环境变量
- **检查端口**: `lsof -i :8020` 确认未被占用
- **检查依赖**: `pip install -r web/backend/requirements.txt` 重新安装
- **检查日志**: `pm2 logs mystocks-backend --lines 50`

### 前端启动失败
- **检查依赖**: `cd web/frontend && npm ci`
- **检查类型生成**: `cd web/frontend && npm run generate-types`
- **检查端口**: `lsof -i :3020` 确认可用

### E2E 测试失败
- **服务是否运行**: 先执行 `pm2 list` 确认 backend + frontend 均在 online
- **登录失败**: 确认后端 `/api/v1/auth/login` 可正常返回 Token
- **404 错误**: 检查前端路由是否匹配、后端 API 端点是否正确
- **白屏**: 检查浏览器的 Console 错误、后端 API 是否有 CORS 错误

### 测试运行慢
- 使用 `-m "not slow"` 跳过慢测试
- 使用 `-n auto` 并行执行（pytest 已默认配置）
- 对有 database 标记的测试，确保数据库服务已启动

---

*本文档基于项目 2026-07-29 状态编写，覆盖了已有的验证基础设施。部分实验性功能（AI/GPU）需要特殊环境配置，不在标准验证范围内。*
