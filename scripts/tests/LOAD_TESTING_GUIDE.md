# MyStocks 压测指南 (Load Testing Guide)

> **参考指南说明**:
> 本文件用于说明脚本目录的使用方法、目录用途、测试流程、部署步骤或辅助操作参考，帮助理解脚本层面的局部实践。
> 其中的命令、路径、步骤与示例应先与 `architecture/STANDARDS.md`、当前脚本实现及最新验证结果核对；若涉及仓库执行流程、命令或协作约束，再补充参考根目录 `AGENTS.md`。本文件不得单独充当共享规则或当前状态的唯一事实来源。


**任务**: Task 14.1 - Locust压测脚本和用户行为建模
**状态**: ✅ 完成
**日期**: 2025-11-12

---

## 📋 概述

本文档描述了MyStocks系统的完整压测套件，包括：
- **Locust压测脚本**: `load_test_locustfile.py` - 1000+并发用户模拟
- **用户行为建模**: `load_test_user_behaviors.py` - 5种用户角色和行为模式
- **压测场景定义**: `load_test_scenarios.py` - 4种压测场景

---

## 🎯 目标

通过压测验证系统的以下性能指标：

| 指标 | 目标 | 备注 |
|------|------|------|
| 并发用户数 | 1000+ | 模拟日常和高峰流量 |
| 响应时间 P95 | < 1000ms | 95%请求响应时间 |
| 响应时间 P99 | < 2000ms | 99%请求响应时间 |
| 错误率 | < 1% | 容错能力验证 |
| 吞吐量 | > 500 req/s | 并发处理能力 |
| 缓存命中率 | > 70% | 缓存策略验证 |
| 数据库连接 | 60-100 | 连接池优化 |
| WebSocket连接 | > 500 | 实时行情支持 |

---

## 📦 文件结构

```
scripts/tests/
├── load_test_locustfile.py           # Locust主脚本（直接运行）
├── load_test_user_behaviors.py       # 用户行为建模库
├── load_test_scenarios.py            # 压测场景定义和执行
├── LOAD_TESTING_GUIDE.md            # 本文件
└── load_test_reports/               # 压测报告目录（自动创建）
    ├── scenario_1_config.json       # 场景1配置
    ├── scenario_2_config.json       # 场景2配置
    ├── scenario_3_config.json       # 场景3配置
    ├── scenario_4_config.json       # 场景4配置
    ├── load_test_plan.json          # 完整测试计划
    └── load_test_scenarios.md       # 场景详细说明
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装Locust
pip install locust>=2.20.0

# 或更新所有依赖
pip install -r requirements.txt
```

### 2. 生成压测配置

```bash
# 生成所有场景的配置文件和测试计划
cd /opt/claude/mystocks_spec
python scripts/tests/load_test_scenarios.py
```

输出：
```
✓ Generated: ./load_test_reports/scenario_1_config.json
✓ Generated: ./load_test_reports/scenario_2_config.json
✓ Generated: ./load_test_reports/scenario_3_config.json
✓ Generated: ./load_test_reports/scenario_4_config.json
✓ Generated: ./load_test_reports/load_test_plan.json
✓ Generated: ./load_test_reports/load_test_scenarios.md
```

### 3. 运行压测

```bash
# 基本用法：运行Locust Web UI
cd /opt/claude/mystocks_spec
locust -f scripts/tests/load_test_locustfile.py --host=http://localhost:8000

# 然后在浏览器中打开: http://localhost:8089
# 配置用户数和spawn_rate，点击"Start swarming"
```

### 4. 命令行模式（自动化）

```bash
# 运行基准测试（100用户，5分钟）
locust -f scripts/tests/load_test_locustfile.py \
  --headless \
  --users=100 \
  --spawn-rate=10 \
  --run-time=300s \
  --host=http://localhost:8000

# 运行高峰负载测试（1000用户，10分钟）
locust -f scripts/tests/load_test_locustfile.py \
  --headless \
  --users=1000 \
  --spawn-rate=50 \
  --run-time=600s \
  --host=http://localhost:8000 \
  --csv=load_test_reports/peak_load_results

# 运行压力测试（2000用户，15分钟）
locust -f scripts/tests/load_test_locustfile.py \
  --headless \
  --users=2000 \
  --spawn-rate=100 \
  --run-time=900s \
  --host=http://localhost:8000 \
  --csv=load_test_reports/stress_test_results
```

---

## 📊 压测场景详解

### 场景1: 基准测试 (Baseline)

**目的**: 验证基础API性能
**用户数**: 100
**持续时间**: 5分钟
**增长速率**: 每秒10个用户

**目标**:
- ✓ 响应时间 < 500ms (P95)
- ✓ 错误率 < 1%
- ✓ 数据库连接 20-30

**适用场景**: 开发环境验证、CI/CD流程中的基础性能检查

```bash
locust -f scripts/tests/load_test_locustfile.py \
  --headless --users=100 --spawn-rate=10 --run-time=300s \
  --host=http://localhost:8000 \
  --csv=load_test_reports/baseline_results
```

---

### 场景2: 正常负载 (Normal Load)

**目的**: 模拟日常交易时段
**用户数**: 500
**持续时间**: 10分钟
**增长速率**: 每秒25个用户

**用户分布**:
- 日内交易者: 150个 (30%)
- 波段交易者: 125个 (25%)
- 长期投资者: 200个 (40%)
- 分析师: 75个 (15%)
- 监控: 25个 (5%)

**目标**:
- ✓ 响应时间 < 1s (P95)
- ✓ 错误率 < 0.5%
- ✓ 缓存命中率 > 70%
- ✓ 数据库连接 30-50

**适用场景**: 日常性能验证、负载均衡器测试

```bash
locust -f scripts/tests/load_test_locustfile.py \
  --headless --users=500 --spawn-rate=25 --run-time=600s \
  --host=http://localhost:8000 \
  --csv=load_test_reports/normal_load_results
```

---

### 场景3: 高峰负载 (Peak Load)

**目的**: 模拟开盘/收盘高峰
**用户数**: 1000
**持续时间**: 10分钟
**增长速率**: 每秒50个用户

**用户分布**:
- 日内交易者: 150个 - 高频查询 (2 req/s)
- 波段交易者: 250个 - 中频查询 (0.8 req/s)
- 长期投资者: 400个 - 低频查询 (0.2 req/s)
- 分析师: 150个 - 分析查询 (1.5 req/s)
- 监控: 50个 - 健康检查 (0.1 req/s)

**目标**:
- ✓ 响应时间 < 2s (P95)
- ✓ 错误率 < 1%
- ✓ WebSocket连接 > 500
- ✓ 数据库连接 60-100

**压力点**:
- 市场开盘 (9:30)
- 午休时段 (11:30-13:00)
- 市场收盘 (15:00)
- 盘后时段 (18:00)

**适用场景**: 生产环境验证、故障恢复测试

```bash
locust -f scripts/tests/load_test_locustfile.py \
  --headless --users=1000 --spawn-rate=50 --run-time=600s \
  --host=http://localhost:8000 \
  --csv=load_test_reports/peak_load_results
```

---

### 场景4: 压力测试 (Stress Test)

**目的**: 测试系统极限
**用户数**: 2000
**持续时间**: 15分钟
**增长速率**: 每秒100个用户

**测试阶段**:
1. **Ramp-up** (200s): 0 → 2000用户线性增加
2. **Sustained** (600s): 保持2000用户
3. **Breakdown** (100s): 优雅断开连接

**监控项**:
- CPU使用率
- 内存消耗
- 网络带宽
- 磁盘I/O
- 数据库连接池
- WebSocket连接数
- 请求队列深度

**告警阈值**:
- ⚠️ 错误率 > 5%
- ⚠️ 响应时间 P95 > 5s
- 🔴 数据库连接池 > 90%利用率
- 🔴 WebSocket连接失败 > 1%

**适用场景**: 容量规划、系统限制识别、故障注入测试

```bash
locust -f scripts/tests/load_test_locustfile.py \
  --headless --users=2000 --spawn-rate=100 --run-time=900s \
  --host=http://localhost:8000 \
  --csv=load_test_reports/stress_test_results
```

---

## 👥 用户行为模型

### 5种用户角色

#### 1. 日内交易者 (Day Trader) - 15%
- **会话时长**: 8小时 (交易时间)
- **请求频率**: 2.0 req/s (最高)
- **自选股**: 20个
- **查询比例**:
  - 实时行情: 40% (最频繁)
  - K线数据: 30%
  - 资金流向: 15%
  - 搜索: 10%
  - 自选股管理: 5%
- **典型操作**: 快速查询多只股票行情，判断买卖点

#### 2. 波段交易者 (Swing Trader) - 25%
- **会话时长**: 2小时
- **请求频率**: 0.8 req/s
- **自选股**: 30个
- **查询比例**:
  - K线数据: 35%
  - 资金流向: 25%
  - 实时行情: 20%
  - 行业分析: 15%
  - 自选股管理: 5%
- **典型操作**: 分析多周期K线，研究行业流向

#### 3. 长期投资者 (Investor) - 40%
- **会话时长**: 30分钟
- **请求频率**: 0.2 req/s (最低)
- **自选股**: 50个
- **查询比例**:
  - 市场概览: 30%
  - 搜索: 30%
  - 自选股管理: 20%
  - 实时行情: 15%
  - 历史K线: 5%
- **典型操作**: 浏览市场概况，管理投资组合

#### 4. 分析师 (Analyst) - 15%
- **会话时长**: 4小时
- **请求频率**: 1.5 req/s
- **自选股**: 100个
- **查询比例**:
  - 行业分析: 25%
  - 资金流向: 25%
  - 多周期K线: 20%
  - 告警历史: 20% (Task 15)
  - 服务健康度: 10%
- **典型操作**: 深度数据分析，撰写研究报告

#### 5. 监控用户 (Monitoring) - 5%
- **会话时长**: 24小时 (后台)
- **请求频率**: 0.1 req/s (很低)
- **自选股**: 0个
- **查询比例**:
  - 健康检查: 40%
  - 告警历史: 40%
  - 服务健康度: 20%
- **典型操作**: 系统健康监控，告警响应

---

## 📈 性能指标解读

### 响应时间分布

```
P50 (中位数)   : 50%的请求在此时间以下 (目标: < 200ms)
P95 (百分位)   : 95%的请求在此时间以下 (目标: < 1000ms)
P99 (百分位)   : 99%的请求在此时间以下 (目标: < 2000ms)
```

### 错误率

```
< 0.1%: 优秀
0.1-0.5%: 良好
0.5-1%: 可接受
> 1%: 需要优化
```

### 吞吐量 (RPS - Requests Per Second)

```
场景1 (100用户): 预期 100-200 RPS
场景2 (500用户): 预期 200-400 RPS
场景3 (1000用户): 预期 400-700 RPS
场景4 (2000用户): 预期 系统极限，可能出现降级
```

---

## 🔧 性能优化建议

### 发现的问题场景

如果在压测中发现以下问题，建议优化方向：

#### 响应时间过长 (P95 > 2000ms)
- [ ] 检查数据库查询性能 (Task 14.3)
- [ ] 增加缓存命中率 (查看缓存策略)
- [ ] 优化API端点逻辑
- [ ] 检查网络延迟

#### 错误率升高 (> 1%)
- [ ] 检查数据库连接池是否耗尽
- [ ] 检查内存占用是否过高
- [ ] 检查磁盘空间
- [ ] 查看应用日志中的错误

#### WebSocket连接失败
- [ ] 调整WebSocket连接池大小
- [ ] 优化消息批处理
- [ ] 增加服务器资源

---

## 📊 生成压测报告

### CSV格式的结果文件

Locust会生成CSV文件，包含以下数据：

```csv
Type,Name,requests,failures,median,average,min,max,Average Size,Requests/s,Failures/s
GET,/api/market/realtime/[stock_code],10000,50,250,300,50,2000,1024,50.0,0.25
POST,/api/auth/login,500,5,100,150,50,500,512,2.5,0.025
...
```

### 分析CSV报告

```bash
# 查看报告
cat load_test_reports/peak_load_results_stats.csv

# 使用Python分析
python << 'EOF'
import pandas as pd

df = pd.read_csv('load_test_reports/peak_load_results_stats.csv')

# 统计汇总
print("Total Requests:", df['requests'].sum())
print("Total Failures:", df['failures'].sum())
print("Success Rate:", 1 - df['failures'].sum() / df['requests'].sum())
print("\nSlowest Endpoints:")
print(df.nlargest(5, 'average')[['Name', 'average']])

print("\nEndpoints with Most Failures:")
print(df[df['failures'] > 0].nlargest(5, 'failures')[['Name', 'failures']])
EOF
```

---

## 🐛 常见问题

### Q1: 压测时出现连接错误

**症状**: `Connection refused` 或 `Connection timeout`

**解决方案**:
1. 检查API服务是否运行: `curl http://localhost:8000/health`
2. 检查防火墙规则
3. 检查API_HOST环境变量设置
4. 检查DNS解析

```bash
# 验证服务连接
curl -v http://localhost:8000/health
```

### Q2: 压测过程中内存持续增长

**症状**: 内存占用不断上升，最终导致系统崩溃

**解决方案**:
1. 检查是否有内存泄漏
2. 减少并发用户数
3. 增加测试间隔
4. 检查WebSocket连接是否正确关闭

### Q3: WebSocket连接失败

**症状**: WebSocket连接建立失败或频繁断开

**解决方案**:
1. 检查WebSocket端口是否开放
2. 增加WebSocket连接超时时间
3. 检查反向代理配置 (nginx/haproxy)
4. 调整OS层面的socket连接限制

```bash
# 查看当前连接限制
ulimit -n

# 临时增加限制 (需要root)
ulimit -n 65536
```

### Q4: 数据库连接池耗尽

**症状**: `无可用连接池` 或 `连接超时`

**解决方案**:
1. 增加连接池大小 (Task 14.3)
2. 优化数据库查询时间
3. 实施连接复用策略
4. 添加连接等待超时

---

## 📝 下一步工作

在Task 14.1完成后，建议进行：

### Task 14.2: WebSocket性能优化
- [ ] 连接池管理
- [ ] 消息批处理
- [ ] 内存优化

### Task 14.3: 数据库性能优化
- [ ] 连接池调优
- [ ] 查询批处理
- [ ] 缓存策略优化

### Task 14.4: 压测报告分析
- [ ] 性能指标分析
- [ ] 瓶颈识别
- [ ] 优化建议

---

## 📚 参考资源

- **Locust官方文档**: https://docs.locust.io/
- **Performance Testing Best Practices**: https://github.com/locustio/locust
- **MyStocks API文档**: `/docs/api/README.md`
- **告警升级机制**: `/docs/api/TASK_15_COMPLETION_SUMMARY.md`

---

## ✅ 清单

### 任务14.1完成项

- [x] Locust主脚本 (`load_test_locustfile.py`) - 650+行
  - [x] HTTP用户行为 (StockBehaviors)
  - [x] WebSocket用户行为 (WebSocketBehaviors)
  - [x] 权重分布 (40种API端点)
  - [x] 事件监听和日志

- [x] 用户行为建模 (`load_test_user_behaviors.py`) - 450+行
  - [x] 5种用户角色定义
  - [x] 用户行为工厂 (UserBehaviorFactory)
  - [x] 请求序列生成 (RequestSequenceGenerator)
  - [x] 流量模型生成 (TrafficModelGenerator)
  - [x] 性能指标收集 (LoadTestMetrics)

- [x] 压测场景定义 (`load_test_scenarios.py`) - 400+行
  - [x] 4种压测场景
  - [x] 场景配置生成
  - [x] JSON配置输出
  - [x] Markdown文档输出

- [x] 完整文档 (LOAD_TESTING_GUIDE.md) - 本文件
  - [x] 快速开始指南
  - [x] 详细场景说明
  - [x] 性能优化建议
  - [x] 常见问题解答

### 验证步骤

```bash
# 1. 验证Python脚本语法
python -m py_compile scripts/tests/load_test_locustfile.py
python -m py_compile scripts/tests/load_test_user_behaviors.py
python -m py_compile scripts/tests/load_test_scenarios.py

# 2. 生成所有配置文件
python scripts/tests/load_test_scenarios.py

# 3. 列出生成的文件
ls -lah load_test_reports/

# 4. 启动Locust进行测试 (可选)
locust -f scripts/tests/load_test_locustfile.py --host=http://localhost:8000
```

---

## 📞 支持

如有问题，请参考：
- 项目Issue: https://github.com/your-project/issues
- 技术文档: `/docs/api/`
- 任务详情: `.taskmaster/tasks/task-14.md`

---

**Task 14.1 Status**: ✅ COMPLETE
**Created**: 2025-11-12
**Last Updated**: 2025-11-12
