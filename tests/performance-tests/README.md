# MyStocks性能测试环境
## Phase 5.1: 配置Locust性能测试环境

本目录包含MyStocks量化平台的完整性能测试环境，基于pytest-benchmark和Locust实现。

## 📊 功能概览

### 1. 性能基线管理 (PerformanceBaseline)
- ✅ 基于pytest-benchmark结果建立性能基线
- ✅ 自动生成性能阈值和优化建议
- ✅ 支持历史对比和趋势分析

### 2. Locust负载测试套件 (LocustTestSuite)
- ✅ 自动生成Locust测试脚本
- ✅ 支持多种API测试场景
- ✅ 实时性能指标收集

### 3. 性能监控和告警 (PerformanceMonitor)
- ✅ 自动检测性能异常
- ✅ 多级别告警机制
- ✅ 性能报告自动生成

## 🚀 快速开始

### 安装依赖
```bash
pip install pytest-benchmark locust
```

### 运行完整性能测试套件
```bash
# 使用集成脚本（推荐）
./scripts/tools/run-performance-suite.sh --all

# 或分别运行
./scripts/tools/run-performance-suite.sh --baseline
./scripts/tools/run-performance-suite.sh --pytest-bench
./scripts/tools/run-performance-suite.sh --locust-test
```

### 建立性能基线
```bash
# 使用Python脚本
python3 scripts/tools/performance_test_suite.py --baseline

# 或使用集成脚本
./scripts/tools/run-performance-suite.sh --baseline
```

### 运行Locust负载测试
```bash
# 基本负载测试（50用户，5用户/秒孵化，2分钟）
./scripts/tools/run-performance-suite.sh --locust-test

# 自定义参数负载测试
./scripts/tools/run-performance-suite.sh --locust-test --users 100 --spawn-rate 10 --run-time 5m
```

## 📁 文件结构

```
performance-tests/
├── locustfile.py              # Locust测试脚本（自动生成）
├── locustfile_backup.py       # 备份文件
└── README.md                  # 本文档

test-reports/
├── performance_baseline.json  # 性能基线
├── benchmark_results.json     # pytest-benchmark结果
├── locust/                    # Locust测试结果
│   ├── results_*.csv         # CSV格式结果
│   ├── report.html           # HTML报告
│   └── locust_results_*.json # JSON格式结果
└── performance_alerts.json   # 性能告警
```

## 🔧 使用方法

### 命令行工具

#### run-performance-suite.sh
```bash
# 显示帮助
./scripts/tools/run-performance-suite.sh --help

# 建立性能基线
./scripts/tools/run-performance-suite.sh --baseline

# 运行pytest-benchmark测试
./scripts/tools/run-performance-suite.sh --pytest-bench

# 运行Locust负载测试
./scripts/tools/run-performance-suite.sh --locust-test --users 100 --spawn-rate 10

# 生成完整性能报告
./scripts/tools/run-performance-suite.sh --report

# 运行完整测试套件
./scripts/tools/run-performance-suite.sh --all
```

#### performance_test_suite.py
```bash
# 显示帮助
python3 scripts/tools/performance_test_suite.py --help

# 建立性能基线
python3 scripts/tools/performance_test_suite.py --baseline

# 运行负载测试
python3 scripts/tools/performance_test_suite.py --load-test --users 50 --run-time 3m

# 启动性能监控
python3 scripts/tools/performance_test_suite.py --monitor
```

### Locust Web界面

启动Locust Web界面进行交互式测试：
```bash
# 生成Locust文件
python3 scripts/tools/performance_test_suite.py --load-test --users 1 --run-time 1s

# 启动Web界面
locust -f performance-tests/locustfile.py --host=http://localhost:8000
```

访问 http://localhost:8089 进行交互式测试。

## 📈 性能指标

### API响应时间阈值
- **市场概览**: < 500ms
- **健康检查**: < 100ms
- **日K线数据**: < 200ms
- **技术指标**: < 300ms

### 吞吐量目标
- **最低RPS**: > 50 req/s
- **目标RPS**: > 100 req/s

### 错误率限制
- **最大错误率**: < 1%

## 📋 测试场景

### Locust测试任务
1. **市场概览** (高频) - 获取市场总览数据
2. **股票报价** (中等) - 获取实时股票报价
3. **日K线数据** (中等) - 获取历史K线数据
4. **技术指标** (中等) - 计算技术指标
5. **策略列表** (低频) - 获取可用策略
6. **健康检查** (低频) - 系统健康状态

### pytest-benchmark测试
- API端点性能基准测试
- 数据处理性能测试
- 数据库查询性能测试

## 🚨 告警机制

### 响应时间告警
- 95%响应时间 > 1000ms 时触发警告
- 影响: 可能影响用户体验

### 错误率告警
- 错误率 > 5% 时触发错误告警
- 影响: 可能影响系统稳定性

### 吞吐量告警
- RPS < 20 时触发警告
- 影响: 可能无法满足业务需求

## 📊 报告分析

### 性能基线报告
```json
{
  "timestamp": "2026-01-18T01:58:54.514045",
  "benchmarks": {
    "test_api_market_overview": {
      "mean": 0.125,
      "median": 0.120,
      "stddev": 0.015
    }
  },
  "thresholds": {...},
  "recommendations": [...]
}
```

### Locust测试报告
```json
{
  "summary": {
    "total_requests": 1714,
    "total_failures": 22,
    "average_response_time": 168.37,
    "requests_per_second": 59.98
  },
  "response_time_percentiles": {
    "50": 124.89,
    "95": 451.34,
    "99": 502.72
  }
}
```

## 🔄 CI/CD集成

### GitHub Actions示例
```yaml
- name: Performance Tests
  run: |
    ./scripts/tools/run-performance-suite.sh --all

- name: Performance Regression Check
  run: |
    python3 scripts/tools/performance_test_suite.py --baseline
    # 检查是否有性能退化
```

### 定期性能监控
```bash
# 每天凌晨2点运行性能测试
0 2 * * * /path/to/project/scripts/tools/run-performance-suite.sh --all
```

## 🛠️ 高级配置

### 自定义Locust配置
```python
# 修改 performance-tests/locustfile.py
class MyStocksUser(HttpUser):
    wait_time = between(0.5, 2.0)  # 自定义等待时间
    # 添加更多测试任务...
```

### 自定义性能阈值
```python
# 修改 performance_test_suite.py 中的 thresholds
thresholds = {
    'api_response_time': {
        'market_overview': 300,  # 自定义阈值
        'health_check': 50,
    }
}
```

### 扩展监控指标
```python
# 添加自定义性能检查
def check_custom_metrics(self, results):
    # 实现自定义监控逻辑
    pass
```

## 📚 相关文档

- [OpenSpec Phase 5.1任务定义](../../openspec/changes/implement-optimized-testing-strategy/tasks.md)
- [Locust官方文档](https://docs.locust.io/)
- [pytest-benchmark文档](https://pytest-benchmark.readthedocs.io/)

## 🐛 故障排除

### 常见问题

1. **Locust启动失败**
   ```bash
   # 检查端口是否被占用
   lsof -i :8000

   # 确保后端服务运行
   curl http://localhost:8000/health
   ```

2. **pytest-benchmark无结果**
   ```bash
   # 确保有benchmark标记的测试
   python -m pytest tests/ -k benchmark --collect-only
   ```

3. **性能基线为空**
   ```bash
   # 检查benchmark_results.json是否存在
   ls -la benchmark_results.json
   ```

## 🎯 最佳实践

1. **定期运行**: 建议每周运行一次完整性能测试
2. **环境一致性**: 在相同环境下运行测试确保可比性
3. **阈值调整**: 根据业务需求调整性能阈值
4. **趋势分析**: 关注性能趋势而非单次结果
5. **告警响应**: 及时响应性能告警并采取措施

---

**最后更新**: 2026-01-18
**版本**: Phase 5.1 Complete