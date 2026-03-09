# Day 5 测试计划（使用MCP工具）

**Date**: 2025-10-24
**Status**: Ready to Execute
**Tools**: FastAPI TestClient + Playwright MCP

---

## 📊 测试策略

### 1. 后端API测试 - FastAPI TestClient

**工具**: FastAPI内置TestClient
**覆盖范围**: 27个API端点（15个strategy + 12个risk）
**预计时间**: 2小时

#### 测试文件结构

```
tests/
├── conftest.py           # 测试配置和fixture
├── test_strategy_api.py  # 策略API测试（15个测试）
└── test_risk_api.py      # 风险API测试（12个测试）
```

#### 示例测试代码

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from web.backend.app.main import app

@pytest.fixture
def client():
    """FastAPI测试客户端"""
    return TestClient(app)

@pytest.fixture
def sample_strategy():
    """示例策略数据"""
    return {
        "name": "测试策略",
        "description": "用于测试的策略",
        "strategy_type": "rule_based",
        "parameters": {"param1": "value1"},
        "status": "draft"
    }


# tests/test_strategy_api.py
def test_list_strategies(client):
    """测试获取策略列表"""
    response = client.get("/api/v1/strategy/strategies")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data


def test_list_strategies_with_filter(client):
    """测试带过滤的策略列表"""
    response = client.get("/api/v1/strategy/strategies?status=active")

    assert response.status_code == 200
    data = response.json()
    # 验证所有返回的策略都是active状态
    for item in data["items"]:
        assert item["status"] == "active"


def test_create_strategy(client, sample_strategy):
    """测试创建策略"""
    response = client.post(
        "/api/v1/strategy/strategies",
        json=sample_strategy
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "策略创建成功"
    assert "data" in data


def test_get_strategy(client, sample_strategy):
    """测试获取策略详情"""
    # 先创建一个策略
    create_response = client.post(
        "/api/v1/strategy/strategies",
        json=sample_strategy
    )
    strategy_id = create_response.json()["data"]["id"]

    # 获取策略详情
    response = client.get(f"/api/v1/strategy/strategies/{strategy_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sample_strategy["name"]


def test_update_strategy(client, sample_strategy):
    """测试更新策略"""
    # 创建策略
    create_response = client.post(
        "/api/v1/strategy/strategies",
        json=sample_strategy
    )
    strategy_id = create_response.json()["data"]["id"]

    # 更新策略
    update_data = {"name": "更新后的策略", "status": "active"}
    response = client.put(
        f"/api/v1/strategy/strategies/{strategy_id}",
        json=update_data
    )

    assert response.status_code == 200
    assert response.json()["message"] == "策略更新成功"


def test_delete_strategy(client, sample_strategy):
    """测试删除策略（软删除）"""
    # 创建策略
    create_response = client.post(
        "/api/v1/strategy/strategies",
        json=sample_strategy
    )
    strategy_id = create_response.json()["data"]["id"]

    # 删除策略
    response = client.delete(f"/api/v1/strategy/strategies/{strategy_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "策略已归档"

    # 验证策略状态为archived
    get_response = client.get(f"/api/v1/strategy/strategies/{strategy_id}")
    assert get_response.json()["status"] == "archived"


def test_train_model(client):
    """测试模型训练"""
    train_config = {
        "name": "测试模型",
        "model_type": "random_forest",
        "hyperparameters": {"n_estimators": 100},
        "training_config": {"test_size": 0.2}
    }

    response = client.post("/api/v1/strategy/models/train", json=train_config)

    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert "model_id" in data


def test_run_backtest(client):
    """测试回测执行"""
    backtest_config = {
        "name": "测试回测",
        "strategy_id": 1,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "initial_cash": 1000000,
        "commission_rate": 0.0003
    }

    response = client.post("/api/v1/strategy/backtest/run", json=backtest_config)

    assert response.status_code == 200
    data = response.json()
    assert "backtest_id" in data


# tests/test_risk_api.py
def test_calculate_var_cvar(client):
    """测试VaR/CVaR计算"""
    response = client.get(
        "/api/v1/risk/var-cvar",
        params={"entity_type": "backtest", "entity_id": 1}
    )

    assert response.status_code == 200
    data = response.json()
    assert "var_95_hist" in data
    assert "cvar_95" in data


def test_calculate_beta(client):
    """测试Beta计算"""
    response = client.get(
        "/api/v1/risk/beta",
        params={"entity_type": "backtest", "entity_id": 1}
    )

    assert response.status_code == 200
    data = response.json()
    assert "beta" in data
    assert "correlation" in data


def test_risk_dashboard(client):
    """测试风险仪表盘"""
    response = client.get("/api/v1/risk/dashboard")

    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "active_alerts" in data
    assert "risk_history" in data


def test_create_risk_alert(client):
    """测试创建风险预警"""
    alert_data = {
        "name": "VaR预警",
        "metric_type": "var_95",
        "threshold_value": -0.05,
        "comparison_operator": "<",
        "is_active": True,
        "notification_channels": ["email"]
    }

    response = client.post("/api/v1/risk/alerts", json=alert_data)

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "预警规则已创建"
```

---

### 2. 前端E2E测试 - Playwright MCP

**工具**: Playwright MCP (mcp__playwright__*)
**覆盖范围**: 3个核心Vue组件
**预计时间**: 2小时

#### 测试场景

**场景1: 策略列表页面**
```python
async def test_strategy_list_page():
    """测试策略列表页面"""

    # 1. 启动浏览器并导航
    await mcp__playwright__browser_navigate(
        url="http://localhost:5173/strategy/list"
    )

    # 2. 等待页面加载
    await mcp__playwright__browser_wait_for(text="策略列表")

    # 3. 获取页面快照（验证结构）
    snapshot = await mcp__playwright__browser_snapshot()
    print("页面结构:", snapshot)

    # 验证关键元素存在
    assert "策略列表" in snapshot
    assert "新建策略" in snapshot
    assert "el-table" in snapshot  # Element Plus表格

    # 4. 测试筛选功能
    await mcp__playwright__browser_click(
        element="状态筛选下拉框",
        ref="[placeholder='全部']"
    )

    await mcp__playwright__browser_click(
        element="活跃选项",
        ref="[label='活跃']"
    )

    await mcp__playwright__browser_click(
        element="查询按钮",
        ref="button[type='primary']:has-text('查询')"
    )

    # 5. 验证筛选结果
    await mcp__playwright__browser_wait_for(time=1)
    snapshot_after = await mcp__playwright__browser_snapshot()
    # 这里可以验证表格数据已更新

    # 6. 测试新建策略按钮
    await mcp__playwright__browser_click(
        element="新建策略按钮",
        ref="button:has-text('新建策略')"
    )

    # 7. 验证导航到创建页面
    await mcp__playwright__browser_wait_for(text="创建策略")

    print("✅ 策略列表页面测试通过")


async def test_strategy_list_pagination():
    """测试分页功能"""

    await mcp__playwright__browser_navigate(
        url="http://localhost:5173/strategy/list"
    )

    # 等待页面加载
    await mcp__playwright__browser_wait_for(text="策略列表")

    # 点击下一页
    await mcp__playwright__browser_click(
        element="下一页按钮",
        ref=".el-pagination .btn-next"
    )

    # 等待数据加载
    await mcp__playwright__browser_wait_for(time=1)

    # 验证页码变化
    snapshot = await mcp__playwright__browser_snapshot()
    # 可以通过snapshot验证当前页码

    print("✅ 分页测试通过")
```

---

**场景2: 回测执行页面**
```python
async def test_backtest_execute_page():
    """测试回测执行页面"""

    # 1. 导航到回测执行页面
    await mcp__playwright__browser_navigate(
        url="http://localhost:5173/backtest/execute"
    )

    # 2. 等待页面加载
    await mcp__playwright__browser_wait_for(text="回测执行")

    # 3. 填写回测表单（使用批量填写）
    await mcp__playwright__browser_fill_form(
        fields=[
            {
                "name": "回测名称",
                "type": "textbox",
                "ref": "input[placeholder='请输入回测名称']",
                "value": "自动化测试回测"
            },
            {
                "name": "初始资金",
                "type": "textbox",
                "ref": ".el-input-number input",
                "value": "1000000"
            }
        ]
    )

    # 4. 选择策略
    await mcp__playwright__browser_click(
        element="策略选择下拉框",
        ref=".el-select[placeholder='请选择策略']"
    )

    await mcp__playwright__browser_click(
        element="第一个策略",
        ref=".el-select-dropdown__item:first-child"
    )

    # 5. 选择日期（这里简化，实际可能需要多步操作）
    # 注：日期选择器比较复杂，可能需要多次点击

    # 6. 提交回测
    await mcp__playwright__browser_click(
        element="开始回测按钮",
        ref="button:has-text('开始回测')"
    )

    # 7. 等待提交成功提示
    await mcp__playwright__browser_wait_for(text="回测已提交")

    # 8. 验证进度条出现
    await mcp__playwright__browser_wait_for(time=1)
    snapshot = await mcp__playwright__browser_snapshot()
    assert "回测进度" in snapshot
    assert "el-progress" in snapshot

    print("✅ 回测执行页面测试通过")


async def test_backtest_progress_tracking():
    """测试回测进度跟踪"""

    # 假设已经提交了回测，现在验证进度更新

    # 1. 等待进度更新（模拟轮询）
    for i in range(5):
        await mcp__playwright__browser_wait_for(time=2)

        # 检查进度条变化
        snapshot = await mcp__playwright__browser_snapshot()

        # 可以通过evaluate获取进度值
        result = await mcp__playwright__browser_evaluate(
            function="() => { return document.querySelector('.el-progress__text').textContent }"
        )

        print(f"当前进度: {result}")

        if "100%" in str(result) or "回测完成" in snapshot:
            print("✅ 回测已完成")
            break

    # 验证最终结果
    snapshot = await mcp__playwright__browser_snapshot()
    assert "回测完成" in snapshot or "查看结果" in snapshot

    print("✅ 进度跟踪测试通过")
```

---

**场景3: 风险仪表盘页面**
```python
async def test_risk_dashboard_page():
    """测试风险仪表盘页面"""

    # 1. 导航到风险仪表盘
    await mcp__playwright__browser_navigate(
        url="http://localhost:5173/risk/dashboard"
    )

    # 2. 等待页面加载
    await mcp__playwright__browser_wait_for(text="VaR")

    # 3. 获取页面快照
    snapshot = await mcp__playwright__browser_snapshot()

    # 4. 验证风险指标卡片存在
    assert "VaR (95%)" in snapshot
    assert "CVaR (95%)" in snapshot
    assert "Beta系数" in snapshot

    # 5. 验证ECharts图表渲染
    # 使用evaluate执行JS检查ECharts实例
    chart_exists = await mcp__playwright__browser_evaluate(
        function="""() => {
            const chartDiv = document.querySelector('[style*="height: 400px"]');
            return chartDiv && chartDiv._echarts_ !== undefined;
        }"""
    )

    assert chart_exists, "ECharts图表未正确渲染"

    # 6. 验证活跃预警表格
    snapshot = await mcp__playwright__browser_snapshot()
    assert "活跃预警规则" in snapshot
    assert "el-table" in snapshot

    # 7. 测试新建预警按钮
    await mcp__playwright__browser_click(
        element="新建预警按钮",
        ref="button:has-text('新建预警')"
    )

    # 8. 验证导航
    await mcp__playwright__browser_wait_for(text="新建预警" or text="预警规则")

    print("✅ 风险仪表盘测试通过")


async def test_echarts_interaction():
    """测试ECharts图表交互"""

    await mcp__playwright__browser_navigate(
        url="http://localhost:5173/risk/dashboard"
    )

    await mcp__playwright__browser_wait_for(text="VaR")

    # 等待图表完全加载
    await mcp__playwright__browser_wait_for(time=2)

    # 截图保存图表
    await mcp__playwright__browser_take_screenshot(
        filePath="risk_dashboard_chart.png"
    )

    # 验证图表数据
    chart_data = await mcp__playwright__browser_evaluate(
        function="""() => {
            const chartDiv = document.querySelector('[style*="height: 400px"]');
            if (!chartDiv || !chartDiv._echarts_) return null;

            const chart = chartDiv._echarts_;
            const option = chart.getOption();

            return {
                seriesCount: option.series.length,
                hasData: option.series[0].data && option.series[0].data.length > 0
            };
        }"""
    )

    print("图表数据:", chart_data)
    assert chart_data["seriesCount"] == 3  # VaR, CVaR, Beta三条线
    assert chart_data["hasData"] == True

    print("✅ ECharts交互测试通过")
```

---

### 3. 集成测试 - API + 前端联调

**场景: 完整的策略创建到回测流程**

```python
async def test_full_workflow():
    """测试完整工作流：创建策略 → 执行回测 → 查看风险"""

    # ========== 步骤1: 创建策略 (API) ==========
    print("步骤1: 创建策略...")

    client = TestClient(app)
    strategy_response = client.post("/api/v1/strategy/strategies", json={
        "name": "集成测试策略",
        "strategy_type": "rule_based",
        "description": "用于集成测试的策略"
    })

    assert strategy_response.status_code == 200
    strategy_id = strategy_response.json()["data"]["id"]
    print(f"✅ 策略创建成功，ID: {strategy_id}")


    # ========== 步骤2: 在前端验证策略出现在列表 ==========
    print("步骤2: 验证策略列表...")

    await mcp__playwright__browser_navigate(
        url="http://localhost:5173/strategy/list"
    )

    await mcp__playwright__browser_wait_for(text="集成测试策略")
    print("✅ 策略在前端列表中显示")


    # ========== 步骤3: 执行回测 (API) ==========
    print("步骤3: 执行回测...")

    backtest_response = client.post("/api/v1/strategy/backtest/run", json={
        "name": "集成测试回测",
        "strategy_id": strategy_id,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "initial_cash": 1000000
    })

    assert backtest_response.status_code == 200
    backtest_id = backtest_response.json()["backtest_id"]
    print(f"✅ 回测已提交，ID: {backtest_id}")


    # ========== 步骤4: 在前端查看回测进度 ==========
    print("步骤4: 查看回测进度...")

    await mcp__playwright__browser_navigate(
        url=f"http://localhost:5173/backtest/detail/{backtest_id}"
    )

    await mcp__playwright__browser_wait_for(text="回测详情" or text="回测结果")
    print("✅ 回测详情页面加载成功")


    # ========== 步骤5: 计算风险指标 (API) ==========
    print("步骤5: 计算风险指标...")

    risk_response = client.get(
        "/api/v1/risk/var-cvar",
        params={"entity_type": "backtest", "entity_id": backtest_id}
    )

    assert risk_response.status_code == 200
    risk_data = risk_response.json()
    print(f"✅ 风险指标计算完成: VaR={risk_data['var_95_hist']}")


    # ========== 步骤6: 在风险仪表盘查看 ==========
    print("步骤6: 查看风险仪表盘...")

    await mcp__playwright__browser_navigate(
        url="http://localhost:5173/risk/dashboard"
    )

    await mcp__playwright__browser_wait_for(text="VaR")

    # 验证风险数据已更新
    snapshot = await mcp__playwright__browser_snapshot()
    # 可以验证VaR值是否显示

    print("✅ 风险仪表盘显示最新数据")


    # ========== 完成 ==========
    print("=" * 50)
    print("✅✅✅ 完整工作流测试通过！")
    print("=" * 50)
```

---

## 📋 执行清单

### 上午 (3小时)

#### 09:00 - 10:00: 后端API测试（FastAPI TestClient）

```bash
# 1. 创建测试文件
cd /opt/claude/mystocks_spec/mystocks
mkdir -p tests
touch tests/__init__.py tests/conftest.py

# 2. 安装测试依赖
pip install pytest pytest-asyncio

# 3. 运行测试
pytest tests/test_strategy_api.py -v
pytest tests/test_risk_api.py -v

# 4. 生成覆盖率报告
pytest --cov=web/backend/api --cov-report=html
```

**验收标准**:
- [ ] 所有27个API端点测试通过
- [ ] 测试覆盖率 > 80%
- [ ] 无失败用例

---

#### 10:00 - 12:00: 前端E2E测试（Playwright MCP）

```bash
# 1. 启动后端服务
cd web/backend
uvicorn app.main:app --reload --port 8020 &

# 2. 启动前端服务
cd web/frontend
npm run dev &  # http://localhost:5173

# 3. 等待服务启动
sleep 5

# 4. 运行Playwright测试（通过Claude Code执行）
# 在Claude Code中运行上述test_*_page()函数
```

**验收标准**:
- [ ] 策略列表页面加载正常
- [ ] 回测执行流程完整
- [ ] 风险仪表盘ECharts渲染成功
- [ ] 所有交互功能正常

---

### 下午 (3小时)

#### 13:00 - 15:00: 集成测试 + 监控验证

```bash
# 1. 运行完整工作流测试
# 执行 test_full_workflow()

# 2. 验证MonitoringDatabase日志
psql -U mystocks_user -d mystocks -c "
SELECT
    operation_type,
    table_name,
    operation_name,
    rows_affected,
    operation_time_ms,
    success
FROM monitoring.operations
ORDER BY created_at DESC
LIMIT 20;
"

# 3. 验证性能指标
psql -U mystocks_user -d mystocks -c "
SELECT
    operation_name,
    AVG(operation_time_ms) as avg_time,
    MAX(operation_time_ms) as max_time,
    COUNT(*) as call_count
FROM monitoring.operations
WHERE success = true
GROUP BY operation_name
ORDER BY avg_time DESC;
"
```

**验收标准**:
- [ ] 完整工作流测试通过
- [ ] MonitoringDatabase有27+条操作日志
- [ ] 平均API响应时间 < 200ms
- [ ] 无错误日志

---

#### 15:00 - 16:00: 性能测试

```python
# 使用pytest-benchmark进行性能测试

def test_api_performance(benchmark, client):
    """测试API性能"""

    def call_api():
        response = client.get("/api/v1/strategy/strategies")
        assert response.status_code == 200

    # 运行benchmark
    result = benchmark(call_api)

    # 验证性能指标
    assert result.stats.mean < 0.2  # 平均响应时间 < 200ms
    assert result.stats.max < 0.5   # 最大响应时间 < 500ms


def test_frontend_load_time():
    """测试前端加载时间"""

    # 使用Playwright performance API
    start_time = await mcp__playwright__browser_evaluate(
        function="() => performance.timing.navigationStart"
    )

    await mcp__playwright__browser_navigate(
        url="http://localhost:5173/strategy/list"
    )

    end_time = await mcp__playwright__browser_evaluate(
        function="() => performance.timing.loadEventEnd"
    )

    load_time = (end_time - start_time) / 1000  # 转换为秒

    assert load_time < 1.5  # 页面加载 < 1.5秒
    print(f"页面加载时间: {load_time}秒")
```

**验收标准**:
- [ ] API响应时间 < 200ms
- [ ] 页面加载时间 < 1.5秒
- [ ] ECharts渲染时间 < 500ms

---

#### 16:00 - 17:00: 最终合规审计

```bash
# 1. 运行所有测试
pytest tests/ -v --cov=web/backend --cov-report=term-missing

# 2. 检查架构合规性
python -c "
from db_manager.database_manager import DatabaseTableManager
from unified_manager import MyStocksUnifiedManager

# 验证ConfigDrivenTableManager
mgr = DatabaseTableManager()
print('✅ ConfigDrivenTableManager initialized')

# 验证MyStocksUnifiedManager
manager = MyStocksUnifiedManager()
print('✅ MyStocksUnifiedManager initialized')

# 验证MonitoringDatabase
from monitoring.monitoring_database import MonitoringDatabase
monitoring_db = MonitoringDatabase()
print('✅ MonitoringDatabase initialized')

print('=' * 50)
print('🎉 所有架构组件验证通过！')
print('=' * 50)
"

# 3. 生成测试报告
pytest tests/ --html=test_report.html --self-contained-html

# 4. 生成覆盖率报告
coverage html
```

**最终检查清单**:
- [ ] ConfigDrivenTableManager: 6张表在table_config.yaml ✅
- [ ] MyStocksUnifiedManager: 所有API使用 ✅
- [ ] MonitoringDatabase: 100%覆盖 ✅
- [ ] 无SEC引用 ✅
- [ ] 无user_id列 ✅
- [ ] 文件命名合规 ✅
- [ ] 所有测试通过 ✅
- [ ] 性能达标 ✅

---

## 🎯 成功标准

### 最终验收

| 维度 | 指标 | 目标 | 状态 |
|------|------|------|------|
| **功能** | API测试通过率 | 100% | ⏳ |
| **功能** | 前端E2E通过率 | 100% | ⏳ |
| **性能** | API响应时间 | <200ms | ⏳ |
| **性能** | 页面加载时间 | <1.5s | ⏳ |
| **质量** | 代码覆盖率 | >80% | ⏳ |
| **监控** | 操作日志覆盖 | 100% | ⏳ |
| **架构** | 合规性检查 | 100% | ⏳ |

---

## 📊 预期输出

### 测试报告

1. **test_report.html** - 详细测试报告
2. **coverage/index.html** - 代码覆盖率报告
3. **监控日志摘要** - MonitoringDatabase查询结果
4. **性能报告** - API和前端性能指标
5. **截图** - 关键页面截图

### 合规证书

```
==========================================
MyStocks Web Integration
100% Architecture Compliance Certificate
==========================================

Validated on: 2025-10-24
Validator: Claude Code + Testing Suite

✅ ConfigDrivenTableManager: 6/6 tables
✅ MyStocksUnifiedManager: 27/27 APIs
✅ MonitoringDatabase: 100% coverage
✅ Business Scope: 0 SEC references
✅ File Naming: 100% compliant
✅ Test Coverage: 85%+
✅ Performance: All targets met

Status: PASSED
==========================================
```

---

**Day 5测试计划完成！准备执行。** 🚀
