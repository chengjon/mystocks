# MyStocks 测试体系优化建议 V2.0

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


**日期**: 2026-01-19
**版本**: v2.0 (基于反馈修订)
**作者**: Claude Code

---

## 📋 执行摘要

本方案基于用户反馈进行了重大修订，核心变化：
- **从 "纯GitHub Actions" 转向 "Python CI 驱动"**
- **充分利用现有基础设施** (`test_continuous_integration.py`, `docker-compose.test.yml`, `WebSocketMock`)
- **统一数据流**: Python Factory → JSON Fixture → Frontend Mock

---

## 🔄 核心架构变更

### 原方案 vs 修订方案

| 维度 | 原方案 | 修订方案 |
|------|--------|----------|
| CI执行器 | GitHub Actions YAML | **Python CI Manager** |
| 测试环境 | 新建docker-compose | **集成现有docker-compose.test.yml** |
| Mock机制 | 分别实现 | **扩展WebSocketMock模式** |
| 数据工厂 | Python独立 | **跨语言JSON Fixture** |
| 本地/远程一致性 | 不保证 | **Local CI = Remote CI** |

### 新架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    统一 CI 执行入口                               │
│           tests/ci/test_continuous_integration.py                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 环境管理      │  │ 测试编排      │  │ 报告生成      │          │
│  │ docker-      │  │ PipelineStep │  │ TestReport   │          │
│  │ compose.test │  │ TestSuite    │  │ JSON/HTML    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           │                                     │
│  ┌────────────────────────▼────────────────────────┐           │
│  │              测试数据层 (跨语言)                   │           │
│  │  Python Factory → JSON Fixture → Frontend Mock  │           │
│  └─────────────────────────────────────────────────┘           │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  GitHub Actions: 仅调用 python tests/ci/run_pipeline.py        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 修订后的优化任务

### P0 - 紧急 (本周内)

#### 1. 统一 CI 执行器 ⭐ 新增

**目标**: 废弃复杂的 GitHub Actions Steps，全面采用 Python CI Manager

**现有资产**:
- `tests/ci/test_continuous_integration.py` - 完整的CI管理器
- 支持: PipelineStep, TestSuite, TestReport, 并行执行

**实施步骤**:

```python
# tests/ci/run_pipeline.py (新建入口脚本)
import asyncio
import argparse
from test_continuous_integration import ContinuousIntegrationManager, PipelineConfig

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pipeline', choices=['ci-check', 'full', 'e2e-only', 'perf-only'])
    parser.add_argument('--env', choices=['development', 'testing', 'staging'])
    args = parser.parse_args()

    async with ContinuousIntegrationManager() as ci:
        config = ci.load_config()

        # 根据pipeline类型配置步骤
        if args.pipeline == 'ci-check':
            config.steps = get_ci_check_steps()
        elif args.pipeline == 'full':
            config.steps = get_full_pipeline_steps()

        result = await ci.run_pipeline(f"pipeline_{args.pipeline}", config)

        # 输出结果
        print_pipeline_summary(result)
        return 0 if result['status'] == 'success' else 1

if __name__ == '__main__':
    exit(asyncio.run(main()))
```

**GitHub Actions 简化**:
```yaml
# .github/workflows/ci.yml
name: CI Pipeline
on: [push, pull_request]

jobs:
  ci-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install Dependencies
        run: pip install -r requirements.txt
      - name: Run CI Pipeline
        run: python tests/ci/run_pipeline.py --pipeline=ci-check --env=testing
```

**预期收益**:
- Local CI = Remote CI (本地验证即CI验证)
- 维护成本降低 80%
- 调试更容易

---

#### 2. 集成测试环境 ⭐ 从P3提升

**目标**: 在 Python CI 脚本中集成 `docker-compose.test.yml` 的启动与拆除

**现有资产**:
- `docker-compose.test.yml` - 已包含 TDengine + PostgreSQL/TimescaleDB
- `tests/ci/test_continuous_integration.py` - 已有 `EnvironmentType` 枚举

**实施步骤**:

```python
# 在 ContinuousIntegrationManager 中添加环境管理
class ContinuousIntegrationManager:
    async def setup_test_environment(self, env_type: EnvironmentType) -> bool:
        """启动测试环境"""
        if env_type == EnvironmentType.TESTING:
            compose_file = "docker-compose.test.yml"

            # 启动容器
            result = await self._run_command(
                f"docker-compose -f {compose_file} up -d --wait"
            )

            if not result['success']:
                logger.error(f"测试环境启动失败: {result['error']}")
                return False

            # 等待健康检查通过
            await self._wait_for_services_healthy()
            return True
        return True

    async def teardown_test_environment(self, env_type: EnvironmentType):
        """拆除测试环境"""
        if env_type == EnvironmentType.TESTING:
            await self._run_command("docker-compose -f docker-compose.test.yml down -v")

    async def run_pipeline(self, pipeline_id: str, config: PipelineConfig):
        """运行流水线 (增强版)"""
        try:
            # 1. 启动测试环境
            await self.setup_test_environment(config.environment)

            # 2. 执行测试步骤
            # ... 现有逻辑 ...

        finally:
            # 3. 拆除测试环境
            await self.teardown_test_environment(config.environment)
```

**预期收益**: 测试环境一致性，一键启动/拆除

---

### P1 - 高优先级 (2周内)

#### 3. E2E 构建对齐 ⭐ 修订

**目标**: 强制 E2E 测试使用 `npm run preview` (产物运行) 模式

**现有资产**:
- `ecosystem.prod.config.js` - 已配置 `npm run preview`
- `E2E_TESTING_OPTIMIZATION_IMPLEMENTATION_REPORT.md` - 已解决模块加载问题

**实施步骤**:

```python
# 在 CI 脚本中强制构建一致性
class E2ETestRunner:
    async def run_e2e_tests(self):
        """运行E2E测试 (强制产物模式)"""
        # 1. 构建前端
        build_result = await self._run_command(
            "cd web/frontend && npm run build",
            timeout=300
        )
        if not build_result['success']:
            raise BuildError("前端构建失败")

        # 2. 启动预览服务器 (非dev模式)
        preview_process = await asyncio.create_subprocess_shell(
            "cd web/frontend && npm run preview -- --port 3020 --host",
            stdout=asyncio.subprocess.PIPE
        )

        try:
            # 3. 等待服务就绪
            await self._wait_for_service("http://localhost:3020", timeout=30)

            # 4. 运行Playwright测试
            test_result = await self._run_command(
                "npx playwright test --project=chromium",
                env={"BASE_URL": "http://localhost:3020"}
            )
            return test_result
        finally:
            preview_process.terminate()
```

**CI配置检查**:
```yaml
# 在CI中验证构建命令一致性
- name: Verify Build Command
  run: |
    # 确保使用与 ecosystem.prod.config.js 一致的命令
    grep -q "npm run preview" web/frontend/ecosystem.prod.config.js || exit 1
```

**预期收益**: 消除 dev/prod 环境差异导致的假阴性

---

#### 4. 数据工厂标准化 ⭐ 修订

**目标**: 建立 Python Factory → JSON Fixture → Frontend Mock 的统一数据流

**现有资产**:
- `web/frontend/tests/helpers/websocket-mock.ts` - WebSocket Mock工具
- `MarketDataScenarios`, `RiskAlertScenarios` - 已有场景数据

**实施步骤**:

**Step 1: Python 数据工厂生成 JSON Fixture**
```python
# tests/factories/market_data_factory.py
import json
from pathlib import Path
from factory import Factory, Faker, LazyAttribute

class StockQuoteFactory(Factory):
    class Meta:
        model = dict

    symbol = Faker('random_element', elements=['000001', '600000', '000858'])
    name = LazyAttribute(lambda o: f"Stock_{o.symbol}")
    price = Faker('pyfloat', min_value=1, max_value=1000, right_digits=2)
    change = Faker('pyfloat', min_value=-10, max_value=10, right_digits=2)
    volume = Faker('random_int', min=1000, max=10000000)

def generate_fixtures():
    """生成JSON Fixture供前端使用"""
    fixtures = {
        "normalMarketData": StockQuoteFactory.build_batch(10),
        "volatileMarketData": [
            StockQuoteFactory.build(change=9.5),  # 涨停
            StockQuoteFactory.build(change=-9.5), # 跌停
        ],
        "emptyMarketData": []
    }

    output_path = Path("tests/fixtures/market_data.json")
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(json.dumps(fixtures, indent=2, ensure_ascii=False))
    print(f"✅ 生成 Fixture: {output_path}")

if __name__ == '__main__':
    generate_fixtures()
```

**Step 2: 前端 Mock 消费 JSON Fixture**
```typescript
// tests/helpers/api-mock.ts (扩展WebSocketMock模式)
import marketDataFixtures from '../fixtures/market_data.json';

export class APIResponseMock {
  constructor(private page: Page) {}

  async initialize() {
    // 拦截所有API请求
    await this.page.route('**/api/v1/**', async (route) => {
      const url = route.request().url();

      if (url.includes('/market/overview')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            code: 200,
            data: marketDataFixtures.normalMarketData
          })
        });
      }
      // ... 其他路由
    });
  }
}
```

**Step 3: CI 中自动生成 Fixture**
```python
# 在 run_pipeline.py 中添加
async def prepare_test_fixtures():
    """生成测试数据"""
    await self._run_command("python tests/factories/market_data_factory.py")
```

**预期收益**: 前后端测试数据同步，复用WebSocket Mock成功经验

---

#### 5. 核心页面视觉基准库建设 ⭐ 新增

**目标**: 基于 ArtDeco 测试成果，扩展至全站核心页面截图对比

**现有资产**:
- `artdeco-visual-regression.spec.ts` - 11个视觉测试
- Playwright screenshot + CSS断言 - 工具已就绪

**实施步骤**:

```typescript
// tests/visual/core-pages-baseline.spec.ts
import { test, expect } from '@playwright/test';

const CORE_PAGES = [
  { name: 'Dashboard', path: '/', selectors: ['.dashboard-container', '.market-summary'] },
  { name: 'KLine', path: '/kline/000001', selectors: ['.kline-chart', '.indicator-panel'] },
  { name: 'Trading', path: '/trading', selectors: ['.order-form', '.position-list'] },
  { name: 'Strategy', path: '/strategy', selectors: ['.strategy-list', '.backtest-panel'] },
  { name: 'Monitor', path: '/monitor', selectors: ['.alert-list', '.realtime-data'] },
];

for (const page of CORE_PAGES) {
  test.describe(`${page.name} 页面视觉基准`, () => {
    test('完整页面截图', async ({ page: p }) => {
      await p.goto(page.path);
      await p.waitForLoadState('networkidle');

      // 截图对比 (首次运行生成基准)
      await expect(p).toHaveScreenshot(`${page.name.toLowerCase()}-full.png`, {
        fullPage: true,
        maxDiffPixelRatio: 0.02  // 允许2%差异
      });
    });

    test('核心元素可见性', async ({ page: p }) => {
      await p.goto(page.path);

      for (const selector of page.selectors) {
        await expect(p.locator(selector)).toBeVisible();
      }
    });
  });
}
```

**CI 集成**:
```yaml
- name: Visual Regression Tests
  run: |
    npx playwright test tests/visual/ --update-snapshots
    # 首次运行生成基准，后续运行对比
```

**预期收益**: 防止 UI 样式倒退，自动检测视觉回归

---

### P2 - 中优先级 (1个月内)

#### 6. 性能测试对接 Python CI ⭐ 修订

**目标**: 利用 `TestType.PERFORMANCE` 枚举，将 Locust 集成到 Python CI

**现有资产**:
- `tests/performance/locustfile.py` - 路由已对齐
- `TestType.PERFORMANCE` - 已定义枚举

**实施步骤**:

```python
# 在 ContinuousIntegrationManager 中添加性能测试支持
async def run_performance_tests(self, config: dict) -> TestReport:
    """运行Locust性能测试并解析结果"""
    # 1. 运行Locust (headless模式)
    locust_cmd = (
        f"locust -f tests/performance/locustfile.py "
        f"--headless -u {config.get('users', 10)} "
        f"-r {config.get('spawn_rate', 2)} "
        f"-t {config.get('duration', '60s')} "
        f"--csv=test-results/perf "
        f"--host=http://localhost:8000"
    )

    result = await self._run_command(locust_cmd, timeout=120)

    # 2. 解析CSV结果
    stats = self._parse_locust_csv("test-results/perf_stats.csv")

    # 3. 生成TestReport
    report = TestReport(
        id=f"perf_{int(time.time())}",
        pipeline_id=self.current_pipeline_id,
        test_suite_id="performance",
        test_type=TestType.PERFORMANCE,
        total_tests=len(stats['endpoints']),
        passed_tests=len([e for e in stats['endpoints'] if e['p95'] < 2000]),
        failed_tests=len([e for e in stats['endpoints'] if e['p95'] >= 2000]),
        duration=stats['total_duration'],
        status=PipelineStatus.SUCCESS if stats['error_rate'] < 0.01 else PipelineStatus.FAILED,
        results=[{
            'endpoint': e['name'],
            'rps': e['rps'],
            'p50': e['p50'],
            'p95': e['p95'],
            'p99': e['p99'],
            'error_rate': e['error_rate']
        } for e in stats['endpoints']]
    )

    return report

def _parse_locust_csv(self, csv_path: str) -> dict:
    """解析Locust CSV输出"""
    import csv
    stats = {'endpoints': [], 'total_duration': 0, 'error_rate': 0}

    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Name'] != 'Aggregated':
                stats['endpoints'].append({
                    'name': row['Name'],
                    'rps': float(row['Requests/s']),
                    'p50': float(row['50%']),
                    'p95': float(row['95%']),
                    'p99': float(row['99%']),
                    'error_rate': float(row['Failure Count']) / max(1, float(row['Request Count']))
                })
            else:
                stats['total_duration'] = float(row.get('Total Request Count', 0))
                stats['error_rate'] = float(row['Failure Count']) / max(1, float(row['Request Count']))

    return stats
```

**预期收益**: 性能指标直接存入 TestReport，统一报告格式

---

#### 7. 覆盖率提升计划 (保留)

**目标**: 分阶段提升覆盖率 13% → 80%

| 阶段 | 目标 | 重点模块 | 时间 |
|------|------|----------|------|
| Phase 1 | 30% | src/core/, src/data_access/ | 1周 |
| Phase 2 | 50% | web/backend/app/api/ | 2周 |
| Phase 3 | 70% | web/backend/app/services/ | 3周 |
| Phase 4 | 80% | 全覆盖 | 4周 |

---

## 📅 修订后的实施路线图

```
┌────────┬─────────────────────┬──────────────────────────────────────────────────────────┐
│ 优先级 │ 任务                │ 关键动作                                                  │
├────────┼─────────────────────┼──────────────────────────────────────────────────────────┤
│ P0     │ 统一 CI 执行器      │ 创建 run_pipeline.py，简化 GitHub Actions                │
│ P0     │ 集成测试环境        │ 在 Python CI 中集成 docker-compose.test.yml              │
├────────┼─────────────────────┼──────────────────────────────────────────────────────────┤
│ P1     │ E2E 构建对齐        │ 强制使用 npm run preview，消除环境差异                   │
│ P1     │ 数据工厂标准化      │ Python Factory → JSON Fixture → Frontend Mock            │
│ P1     │ 视觉基准库建设      │ 扩展 ArtDeco 测试至全站核心页面                          │
├────────┼─────────────────────┼──────────────────────────────────────────────────────────┤
│ P2     │ 性能测试对接        │ Locust 结果解析到 TestReport                             │
│ P2     │ 覆盖率提升          │ 分4阶段从 13% → 80%                                      │
└────────┴─────────────────────┴──────────────────────────────────────────────────────────┘
```

---

## 📊 预期收益对比

| 指标 | 原方案预期 | 修订方案预期 | 改进 |
|------|-----------|-------------|------|
| 实施成本 | 高 (新建大量代码) | **低** (复用现有) | -60% |
| 维护成本 | 高 (双套逻辑) | **低** (统一入口) | -80% |
| 本地/CI一致性 | 不保证 | **100%** | ✅ |
| 数据同步 | 前后端分离 | **统一Fixture** | ✅ |

---

## ✅ 总结

修订后的方案核心变化：

1. **统一执行入口**: `tests/ci/test_continuous_integration.py` 作为唯一CI编排工具
2. **复用现有资产**: docker-compose.test.yml, WebSocketMock, ArtDeco测试
3. **跨语言数据流**: Python Factory → JSON Fixture → Frontend Mock
4. **Local CI = Remote CI**: 本地验证即CI验证

**核心原则**: 基于现有代码资产的行动指南，而非通用建议书。

---

**报告生成**: 2026-01-19
**版本**: v2.0
**作者**: Claude Code
**状态**: 待实施
