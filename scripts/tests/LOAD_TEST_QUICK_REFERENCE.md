# Locust 压测快速参考 (Quick Reference)

> **参考指南说明**:
> 本文件用于说明脚本目录的使用方法、目录用途、测试流程、部署步骤或辅助操作参考，帮助理解脚本层面的局部实践。
> 其中的命令、路径、步骤与示例应先与 `architecture/STANDARDS.md`、当前脚本实现及最新验证结果核对；若涉及仓库执行流程、命令或协作约束，再补充参考根目录 `AGENTS.md`。本文件不得单独充当共享规则或当前状态的唯一事实来源。


**任务**: Task 14.1 - Locust压测脚本和用户行为建模 ✅
**生成日期**: 2025-11-12

---

## 🚀 最常用命令

### 1. 基准测试 (100用户, 5分钟)
```bash
locust -f scripts/tests/load_test_locustfile.py \
  --headless --users=100 --spawn-rate=10 \
  --run-time=300s --host=http://localhost:8000 \
  --csv=load_test_reports/baseline
```

### 2. 正常负载 (500用户, 10分钟)
```bash
locust -f scripts/tests/load_test_locustfile.py \
  --headless --users=500 --spawn-rate=25 \
  --run-time=600s --host=http://localhost:8000 \
  --csv=load_test_reports/normal_load
```

### 3. 高峰负载 (1000用户, 10分钟)
```bash
locust -f scripts/tests/load_test_locustfile.py \
  --headless --users=1000 --spawn-rate=50 \
  --run-time=600s --host=http://localhost:8000 \
  --csv=load_test_reports/peak_load
```

### 4. 压力测试 (2000用户, 15分钟)
```bash
locust -f scripts/tests/load_test_locustfile.py \
  --headless --users=2000 --spawn-rate=100 \
  --run-time=900s --host=http://localhost:8000 \
  --csv=load_test_reports/stress_test
```

### 5. Web UI 界面测试（交互式）
```bash
locust -f scripts/tests/load_test_locustfile.py \
  --host=http://localhost:8000

# 然后访问: http://localhost:8089
```

---

## 📊 结果分析

### 查看CSV报告
```bash
# 统计汇总
head -20 load_test_reports/peak_load_stats.csv

# 完整分析
python << 'EOF'
import pandas as pd
df = pd.read_csv('load_test_reports/peak_load_stats.csv')
print("=" * 60)
print("LOAD TEST RESULTS SUMMARY")
print("=" * 60)
print(f"Total Requests: {df['requests'].sum():,}")
print(f"Total Failures: {df['failures'].sum():,}")
print(f"Success Rate: {100 * (1 - df['failures'].sum() / df['requests'].sum()):.2f}%")
print(f"\nResponse Time Statistics:")
print(f"  Min: {df['min'].min():.0f}ms")
print(f"  Max: {df['max'].max():.0f}ms")
print(f"  Mean: {df['average'].mean():.0f}ms")
print(f"  Median: {df['median'].median():.0f}ms")
print(f"\nSlowest Endpoints:")
for idx, row in df.nlargest(5, 'average').iterrows():
    print(f"  {row['Name']}: {row['average']:.0f}ms")
EOF
```

---

## ⚙️ 环境变量

```bash
# 设置API地址
export API_HOST=http://localhost:8000

# 设置日志级别
export LOCUST_LOG_LEVEL=INFO

# 查看所有选项
locust --help
```

---

## 📁 文件位置

```
scripts/tests/
├── load_test_locustfile.py           # 主脚本 (370行)
├── load_test_user_behaviors.py       # 用户行为 (420行)
├── load_test_scenarios.py            # 场景定义 (413行)
├── LOAD_TESTING_GUIDE.md             # 详细文档 (563行)
├── LOAD_TEST_QUICK_REFERENCE.md      # 本文件
└── load_test_reports/
    ├── scenario_1_config.json        # 基准测试配置
    ├── scenario_2_config.json        # 正常负载配置
    ├── scenario_3_config.json        # 高峰负载配置
    ├── scenario_4_config.json        # 压力测试配置
    ├── load_test_plan.json           # 完整测试计划
    └── load_test_scenarios.md        # 场景详细说明
```

---

## 🎯 关键指标解读

| 指标 | 目标 | 公式 |
|------|------|------|
| 错误率 (ER) | < 1% | 失败数 / 总数 × 100% |
| 吞吐量 (RPS) | > 500 | 总请求数 / 总耗时 |
| P95响应时间 | < 1000ms | 第95百分位响应时间 |
| P99响应时间 | < 2000ms | 第99百分位响应时间 |

---

## 🔍 故障排查

### 问题1: 连接拒绝
```bash
# 验证服务是否运行
curl -v http://localhost:8000/health
```

### 问题2: 性能下降
```bash
# 检查系统资源
top
free -h
netstat -an | grep ESTABLISHED | wc -l  # 连接数
```

### 问题3: 内存泄漏
```bash
# 监控内存占用
watch -n 1 'free -h | grep "Mem:"'
```

---

## 📈 生成对比报告

```bash
# 对比两个测试结果
python << 'EOF'
import pandas as pd

# 读取两个测试的结果
baseline = pd.read_csv('load_test_reports/baseline_stats.csv')
peak = pd.read_csv('load_test_reports/peak_load_stats.csv')

# 合并数据
comparison = baseline[['Name', 'average']].copy()
comparison.columns = ['Name', 'Baseline_Avg']
comparison['Peak_Avg'] = comparison['Name'].map(
    dict(zip(peak['Name'], peak['average']))
)
comparison['Increase%'] = (
    (comparison['Peak_Avg'] - comparison['Baseline_Avg']) /
    comparison['Baseline_Avg'] * 100
).round(1)

# 显示结果
print("=" * 80)
print("PERFORMANCE COMPARISON: BASELINE vs PEAK")
print("=" * 80)
print(comparison.to_string(index=False))
EOF
```

---

## 💡 性能优化建议

### 如果 P95响应时间 > 1000ms
- ❌ 数据库查询需要优化 (Task 14.3)
- ❌ 缓存命中率太低
- ❌ 检查慢查询日志

### 如果 错误率 > 1%
- ❌ 数据库连接池耗尽
- ❌ 内存不足
- ❌ 检查应用日志

### 如果 吞吐量 < 500 RPS
- ❌ CPU瓶颈
- ❌ 网络带宽不足
- ❌ 磁盘I/O不足

---

## 📋 压测前检查清单

```bash
#!/bin/bash

echo "Pre-load test checklist:"
echo "========================"

# 检查API服务
echo -n "✓ API service: "
curl -s http://localhost:8000/health > /dev/null && echo "OK" || echo "FAILED"

# 检查数据库连接
echo -n "✓ Database: "
curl -s -H "Authorization: Bearer test" http://localhost:8000/api/market/realtime/000001 > /dev/null && echo "OK" || echo "FAILED"

# 检查磁盘空间
echo -n "✓ Disk space: "
available=$(df /opt | tail -1 | awk '{print $4}')
if [ $available -gt 5000000 ]; then echo "OK ($((available/1024/1024))GB)"; else echo "LOW"; fi

# 检查系统负载
echo -n "✓ System load: "
load=$(uptime | grep -o "load average.*" | cut -d: -f2)
echo $load

# 检查网络连接
echo -n "✓ Network: "
ping -c 1 8.8.8.8 > /dev/null 2>&1 && echo "OK" || echo "CHECK"

# 检查文件句柄限制
echo -n "✓ File descriptors: "
echo $(ulimit -n)

echo "========================"
echo "Ready to start load test!"
```

---

## 🔗 相关链接

- **完整指南**: [LOAD_TESTING_GUIDE.md](LOAD_TESTING_GUIDE.md)
- **Locust文档**: https://docs.locust.io/
- **API文档**: `/docs/api/README.md`
- **Task 15**: `/docs/api/TASK_15_COMPLETION_SUMMARY.md`

---

## ✅ 任务完成项

- [x] Locust主脚本 (load_test_locustfile.py)
- [x] 用户行为建模 (load_test_user_behaviors.py)
- [x] 压测场景定义 (load_test_scenarios.py)
- [x] 场景配置生成 (4个JSON配置文件)
- [x] 完整文档 (LOAD_TESTING_GUIDE.md)
- [x] 快速参考 (本文件)

**Status**: ✅ COMPLETE
**Total LOC**: 1,766 lines
**Files Created**: 7

---

**Task 14.1 Completed**: 2025-11-12
**Next Task**: Task 14.2 - WebSocket性能优化
