# E2E测试问题报告

**测试日期**: 2026-01-27
**测试范围**: 市场数据页面测试
**测试工具**: Playwright + TypeScript

---

## 测试结果摘要

| 测试项 | 结果 | 说明 |
|--------|------|------|
| 前端服务连接 | ✅ 通过 | 前端在端口3001正常运行 |
| 登录页面加载 | ✅ 通过 | 页面元素正确渲染 |
| 登录功能 | ❌ **失败** | 用户仍停留在登录页面 |
| 市场数据页面 | ❌ 未执行 | 需先完成登录 |

---

## 发现的问题

### 问题1: 登录功能失效 (Critical)

**现象**: 
- 用户尝试登录后，URL仍为 `/login`
- 登录验证失败 `expect(page.url()).not.toContain('/login')`

**可能原因**:
1. **CSRF中间件阻止**: 后端CSRF保护可能阻止了登录请求
2. **API响应格式不匹配**: 前端期望 `access_token`，后端返回 `data.token`
3. **认证端点404**: `/api/auth/login` 端点不存在

**验证步骤**:
```bash
# 测试后端登录API
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**已知修复** (待验证):
- `web/backend/app/api/auth.py` - 添加了兼容登录端点
- `web/frontend/src/stores/auth.ts` - 添加了响应格式转换

---

### 问题2: 测试配置端口不匹配

**现象**: 测试框架使用端口3000，但前端实际运行在3001/3002

**修复**:
- ✅ 更新 `tests/e2e/fixtures/test-data.ts` - 使用 `E2E_BASE_URL` 环境变量
- ✅ 更新 `tests/e2e/pages/LoginPage.ts` - 支持环境变量

**临时解决方案**:
```bash
E2E_BASE_URL=http://localhost:3001 npx playwright test ...
```

---

### 问题3: 后端服务未在PM2中正确配置

**现象**: PM2日志显示 `ImportError: attempted relative import with no known parent package`

**解决方案**: 见 `WEB_FRONTEND_STARTUP_GUIDE.md` 第7节

---

## 待测试页面列表 (43个)

由于登录功能失效，以下页面测试暂停:

### 认证 (1个)
- [ ] Login `/login`

### Dashboard (1个)
- [ ] Dashboard `/dashboard`

### Market Domain (10个)
- [ ] Realtime `/market/realtime`
- [ ] Technical `/market/technical`
- [ ] FundFlow `/market/fund-flow`
- [ ] ETF `/market/etf`
- [ ] Concept `/market/concept`
- [ ] Auction `/market/auction`
- [ ] LongHuBang `/market/longhubang`
- [ ] Institution `/market/institution`
- [ ] Wencai `/market/wencai`
- [ ] Screener `/market/screener`

### Stock Management (2个)
- [ ] Stock Management `/stocks/management`
- [ ] Portfolio `/stocks/portfolio`

### Trading Domain (4个)
- [ ] Signals `/trading/signals`
- [ ] History `/trading/history`
- [ ] Positions `/trading/positions`
- [ ] Attribution `/trading/attribution`

### Strategy Domain (5个)
- [ ] Design `/strategy/design`
- [ ] Management `/strategy/management`
- [ ] Backtest `/strategy/backtest`
- [ ] GPU Backtest `/strategy/gpu-backtest`
- [ ] Optimization `/strategy/optimization`

### Risk Domain (5个)
- [ ] Overview `/risk/overview`
- [ ] Alerts `/risk/alerts`
- [ ] Indicators `/risk/indicators`
- [ ] Sentiment `/risk/sentiment`
- [ ] Announcement `/risk/announcement`

### System Domain (5个)
- [ ] Monitoring `/system/monitoring`
- [ ] Settings `/system/settings`
- [ ] DataUpdate `/system/data-update`
- [ ] DataQuality `/system/data-quality`
- [ ] APIHealth `/system/api-health`

---

## 后续行动

### 优先级1: 修复登录功能
1. 验证后端登录API响应格式
2. 确认前端响应转换逻辑正确
3. 测试完整登录流程

### 优先级2: 更新测试基础设施
1. 将测试文件移到正确目录
2. 配置正确的端口
3. 添加测试覆盖率报告

### 优先级3: 运行完整测试套件
1. 登录修复后，重新运行所有43个页面测试
2. 记录失败的页面和错误
3. 按最小化变动原则修复

---

## 相关文档

- 测试文件: `web/frontend/tests/e2e/comprehensive-all-pages.spec.ts`
- 测试脚本: `scripts/test/run-comprehensive-tests.sh`
- 启动指南: `docs/guides/WEB_FRONTEND_STARTUP_GUIDE.md`
- 问题修复: `docs/reports/FRONTEND_JS_SYNTAX_FIX_REPORT.md`
