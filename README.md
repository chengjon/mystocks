# CLI-2: Phase 6 E2E 测试执行

**分支**: `phase6-e2e-testing`  
**工作目录**: `/opt/claude/mystocks_phase6_e2e`  
**预计时间**: 6-8 小时（最大工作量）  
**优先级**: 🔴 高（质量保证关键路径）  
**分配给**: CLAUDE 或 IFLOW  

**重要提示**: 由于此任务工作量最大，建议**提前30分钟开始**，以确保与其他CLI同步完成。

---

## 🎯 任务目标

执行完整的 Playwright E2E 测试套件，确保前端和后端集成正常工作：

1. ✅ 安装并配置 Playwright 测试框架
2. ✅ 运行所有 7 个测试套件（100% 通过率）
3. ✅ 修复所有失败的测试
4. ✅ 生成测试覆盖率报告
5. ✅ 配置 CI/CD 集成
6. ✅ 性能基准测试

---

## 📋 详细任务清单

### 任务 2.1: 安装 Playwright 依赖 (30分钟)

**目标**: 安装 Playwright 及所有依赖

**步骤**:
```bash
# 1. 进入前端目录
cd /opt/claude/mystocks_phase6_e2e/web/frontend

# 2. 安装 Playwright 测试框架
npm install -D @playwright/test

# 3. 安装浏览器
npx playwright install

# 4. 验证安装
npx playwright --version
```

**验收标准**:
- ✅ `@playwright/test` 安装成功（在 `package.json` 中）
- ✅ 浏览器安装完成（chromium, firefox, webkit）
- ✅ `npx playwright --version` 输出版本号

**可能的问题**:
- **问题**: npm 安装失败
  - **解决**: 删除 `node_modules` 和 `package-lock.json`，重新安装
  
- **问题**: 浏览器下载缓慢
  - **解决**: 使用国内镜像: `PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright npx playwright install`

---

### 任务 2.2: 配置测试环境 (30分钟)

**目标**: 配置 Playwright 和测试环境变量

**步骤**:
```bash
# 1. 检查 Playwright 配置文件
cd /opt/claude/mystocks_phase6_e2e/web/frontend
cat playwright.config.ts

# 2. 验证配置包含:
# - testDir: tests/e2e
# - timeout: 30000 (30秒)
# - retries: 2
# - workers: process.env.CI ? 1 : undefined
# - reporter: [['html'], ['json', { outputFile: 'test-results/results.json' }]]
# - use: {
#     baseURL: 'http://localhost:3020',
#     trace: 'on-first-retry',
#     screenshot: 'only-on-failure',
#     video: 'retain-on-failure'
#   }

# 3. 创建环境变量文件
cat > .env.test << 'ENV'
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000

# Frontend URL
FRONTEND_URL=http://localhost:3020

# Test credentials
TEST_USERNAME=test@example.com
TEST_PASSWORD=password123
ENV

# 4. 验证测试文件存在
ls -la tests/e2e/test_*.py
```

**验收标准**:
- ✅ `playwright.config.ts` 配置正确
- ✅ `.env.test` 文件创建成功
- ✅ 测试文件存在（至少 7 个）
- ✅ `tests/e2e/conftest.py` fixtures 配置正确

**可能的问题**:
- **问题**: 配置文件不存在
  - **解决**: 从 `config/monitoring/playwright.config.ts` 复制或创建新配置
  
- **问题**: 测试文件缺失
  - **解决**: 检查是否在 `tests/e2e/` 目录下

---

### 任务 2.3: 启动测试环境 (20分钟)

**目标**: 启动前端和后端服务用于测试

**步骤**:
```bash
# 1. 启动后端服务（在后台）
cd /opt/claude/mystocks_phase6_e2e/web/backend
ADMIN_PASSWORD=password python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# 2. 等待后端启动
sleep 10

# 3. 验证后端健康
curl http://localhost:8000/health

# 4. 启动前端服务（在后台）
cd /opt/claude/mystocks_phase6_e2e/web/frontend
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# 5. 等待前端启动
sleep 15

# 6. 验证前端可访问
curl -I http://localhost:3020

# 7. 记录 PID，方便后续清理
echo "$BACKEND_PID" > /tmp/backend_pid.txt
echo "$FRONTEND_PID" > /tmp/frontend_pid.txt
```

**验收标准**:
- ✅ 后端服务在 8000 端口运行
- ✅ 前端服务在 3020 端口运行
- ✅ `/health` 端点返回 200 OK
- ✅ 前端页面可访问

**可能的问题**:
- **问题**: 端口被占用
  - **解决**: 检查并停止占用端口的进程：`lsof -i :8000` 或 `lsof -i :3020`
  
- **问题**: 前端构建失败
  - **解决**: 检查 Node 版本，删除 `node_modules` 重新安装

---

### 任务 2.4: 运行 7 个测试套件 (2-3小时)

**目标**: 执行所有 E2E 测试并记录结果

**7 个测试套件**:
1. `test_charts.py` - 图表功能测试（233行）
2. `test_export.py` - 数据导出测试（300行）
3. `test_fund_flow.py` - 资金流向测试（170行）
4. `test_login.py` - 登录流程测试（94行）
5. `test_market.py` - 市场数据测试（116行）
6. `test_risk.py` - 风险管理测试（215行）
7. `conftest.py` - 测试配置和 fixtures（130行）

**步骤**:
```bash
# 1. 进入前端目录
cd /opt/claude/mystocks_phase6_e2e/web/frontend

# 2. 运行所有测试
npx playwright test

# 3. 如果需要，单独运行特定测试文件
npx playwright test tests/e2e/test_login.py
npx playwright test tests/e2e/test_market.py
npx playwright test tests/e2e/test_charts.py
npx playwright test tests/e2e/test_export.py
npx playwright test tests/e2e/test_fund_flow.py
npx playwright test tests/e2e/test_risk.py

# 4. 查看测试报告
npx playwright show-report
```

**验收标准**:
- ✅ 所有测试套件执行完成
- ✅ 测试通过率 > 95%（允许少量失败）
- ✅ 测试报告生成（HTML + JSON）
- ✅ 失败测试有截图和视频

**可能的问题**:
- **问题**: 测试超时
  - **解决**: 增加 `playwright.config.ts` 中的 `timeout` 值
  
- **问题**: 元素找不到
  - **解决**: 检查页面选择器，可能是前端加载慢导致
  
- **问题**: 大量测试失败
  - **解决**: 先运行单个测试文件，逐个调试

---

### 任务 2.5: 修复失败的测试 (2-3小时)

**目标**: 确保所有测试通过（100% 通过率）

**调试工作流**:
```bash
# 1. 查看失败测试的详细信息
npx playwright test --reporter=list

# 2. 重新运行仅失败的测试
npx playwright test --grep @failed

# 3. 调试模式运行（打开浏览器）
npx playwright test --debug

# 4. 查看失败的截图和视频
ls -la test-results/
# 失败测试会有:
# - screenshot.png
# - video.webm
# - trace.zip

# 5. 检查失败原因
# 常见原因:
# a. 元素选择器错误
# b. 页面加载慢导致超时
# c. API 响应数据格式变化
# d. 测试数据不一致
```

**修复策略**:
```bash
# 1. 更新选择器（如果前端DOM变化）
# 编辑 tests/e2e/test_*.py，更新 page.locator()

# 2. 增加等待时间（如果页面加载慢）
await page.wait_for_selector('.data-loaded', timeout=10000)

# 3. 添加重试逻辑（如果是网络问题）
await page.reload(wait_until='networkidle')

# 4. 更新测试数据（如果API变化）
# 编辑 tests/e2e/conftest.py 中的 fixtures
```

**验收标准**:
- ✅ 所有测试通过（100%）
- ✅ 无 skipped tests
- ✅ 无 flaky tests（不稳定的测试）

**可能的问题**:
- **问题**: 测试时好时坏（flaky）
  - **解决**: 添加显式等待，增加重试次数
  
- **问题**: 无法修复的测试
  - **解决**: 联系 Main CLI，可能需要调整测试用例或修复代码

---

### 任务 2.6: 生成测试覆盖率报告 (45分钟)

**目标**: 生成详细的测试覆盖率报告

**步骤**:
```bash
# 1. 安装覆盖率工具
cd /opt/claude/mystocks_phase6_e2e/web/frontend
npm install -D @playwright/test-coverage

# 2. 运行测试并收集覆盖率
npx playwright test --coverage

# 3. 生成覆盖率报告
npx playwright test --reporter=html

# 4. 查看覆盖率报告
# 打开: test-results/index.html
# 应该看到:
# - 总覆盖率百分比
# - 按模块的覆盖率
# - 未覆盖的代码行

# 5. 导出覆盖率数据
npx playwright test --reporter=json > test-results/coverage-report.json
```

**验收标准**:
- ✅ 覆盖率报告生成（HTML + JSON）
- ✅ 整体覆盖率 > 80%
- ✅ 关键功能覆盖率 > 90%
- ✅ 报告可分享（可上传到服务器）

**可能的问题**:
- **问题**: 覆盖率低于 80%
  - **解决**: 识别未覆盖的代码路径，添加额外测试用例

---

### 任务 2.7: 性能基准测试 (45分钟)

**目标**: 执行性能基准测试并记录结果

**步骤**:
```bash
# 1. 运行性能基准测试
cd /opt/claude/mystocks_phase6_e2e
python tests/performance/benchmark.py

# 2. 使用 Locust 进行负载测试
cd /opt/claude/mystocks_phase6_e2e/tests/performance
locust -f locustfile.py --headless -u 100 -r 10 -t 1m

# 3. 记录性能指标
# - API 响应时间（p50, p95, p99）
# - 每秒请求数（RPS）
# - 错误率
# - 并发用户数

# 4. 生成性能报告
cat > PERFORMANCE_REPORT.md << 'EOF'
# E2E 性能测试报告

## 测试环境
- CPU: [CPU信息]
- Memory: [内存信息]
- Network: [网络信息]

## 性能指标
### API 响应时间
- p50: [50th percentile]
- p95: [95th percentile]
- p99: [99th percentile]

### 吞吐量
- RPS: [每秒请求数]
- 并发用户: [并发数]

### 错误率
- 错误率: [百分比]

## 瓶颈分析
[识别性能瓶颈]

## 优化建议
[基于测试结果的建议]
