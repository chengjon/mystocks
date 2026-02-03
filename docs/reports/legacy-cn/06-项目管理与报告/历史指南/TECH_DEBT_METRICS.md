# 技术负债指标仪表板 (Technical Debt Metrics Dashboard)

**最后更新**: 2025-12-05
**基准日期**: 2025-12-05
**目标完成**: 2026-01-16

---

## 核心指标 (Key Performance Indicators)

### 📊 代码质量指标

#### 1. 文件大小分布

```
当前状态 (2025-12-05):
├─ > 2000 行: 1 个文件   (data_adapter.py)
├─ 1000-2000 行: 9 个文件
├─ 500-1000 行: 15 个文件
└─ < 500 行: ~200 个文件 ✅

目标 (2026-01-16):
├─ > 2000 行: 0 个文件 ⭐
├─ 1000-2000 行: 0 个文件 ⭐
├─ 500-1000 行: 5 个文件 (过渡期)
└─ < 500 行: ~220 个文件

改进指标:
  当前: 平均 650 行/文件
  目标: 平均 250 行/文件
  改进: -62% (大幅度)
```

#### 2. 异常处理质量

```
当前状态:
  except Exception 捕获: 786 次 ❌
  except 特定异常: 45 次 ✅
  比例: 94.6% 过度宽泛

目标状态:
  except Exception 捕获: 0 次 ⭐
  except 特定异常: 850+ 次 ✅
  比例: 100% 特定异常

修复进度追踪:
  Week 1: 786 → 600+ (剩余 60%)
  Week 2: 600 → 400+ (剩余 30%)
  Week 3: 400 → 200+ (剩余 15%)
  Week 4: 200 → 0 (完成 ✅)
```

#### 3. TODO/FIXME 注释计数

```
当前状态:
  总数: 20+ (后端) + 69 (前端) = 89+ 个

  分类:
  ├─ 🔴 CRITICAL: 4 个 (认证、数据获取)
  ├─ 🟠 HIGH: 8 个 (缓存、监控)
  └─ 🟡 MEDIUM: 77 个 (文档、优化)

目标状态:
  总数: 0 个 ⭐

修复时间线:
  Week 1-2: 20 → 10 (第一批 critical)
  Week 3-4: 10 → 0 (完成所有)
```

#### 4. 代码覆盖率

```
当前状态:
  整体: ~30% (估计)
  后端: ~35%
  前端: ~25%

目标状态:
  整体: >= 80% ⭐
  后端: >= 85%
  前端: >= 75%

周目标:
  Week 1: 30% → 35% (+ 5%)
  Week 2: 35% → 45% (+ 10%)
  Week 3: 45% → 60% (+ 15%)
  Week 4: 60% → 70% (+ 10%)
  Week 5: 70% → 80% (+ 10%)
  Week 6: 80% → 85% (+ 5%)
```

#### 5. E2E 测试通过率

```
当前状态:
  总测试: 72 个
  通过: 56 个 (77.8%)
  失败: 16 个 (22.2%)

目标状态:
  通过: 70 个 (97%+) ⭐
  失败: < 2 个

失败原因分析:
  ├─ 选择器错误: 8 个 (50%)
  ├─ 超时问题: 5 个 (31%)
  ├─ API 不稳定: 2 个 (12%)
  └─ 其他: 1 个 (6%)

修复进度:
  Week 2: 16 → 12 (-4, 修复选择器)
  Week 3: 12 → 8 (-4, 调整超时)
  Week 4: 8 → 2 (-6, API 修复)
  Week 5: 2 → 0 (完成 ✅)
```

---

## 详细指标跟踪 (Detailed Metrics Tracking)

### 安全性指标

#### 凭证安全

```
指标: 已知凭证泄露数
  当前: 3 个 (TDENGINE_PASSWORD, POSTGRESQL_PASSWORD, JWT_SECRET)
  周目标:
    Week 1 Day 1: 3 → 0 (立即轮换)
    目标: 保持 0 ⭐

指标: Pre-commit Hook 有效性
  当前: 无 Hook
  周目标:
    Week 1 Day 2: Hook 部署完成
    目标: 100% 防止敏感信息提交 ⭐

指标: CVE 漏洞数
  当前: 1-3 个 (未扫描)
  周目标:
    Week 4: 运行 pip-audit
    Week 8: 所有 CVE 修复
    目标: 0 个已知漏洞 ⭐
```

### 复杂性指标

#### 函数复杂性

```
指标: 圈复杂度 > 10 的函数数
  当前: ~50 个
  目标: < 5 个

  改进目标:
    Week 2: 50 → 35 (-30%)
    Week 4: 35 → 15 (-57%)
    Week 6: 15 → 5 (-67%)

指标: 平均函数长度
  当前: ~45 行
  目标: < 30 行

指标: 类的方法数
  当前: 平均 12 个方法/类
  目标: < 8 个方法/类
```

#### 依赖复杂性

```
指标: 导入链深度
  当前: 5-6 层
  目标: < 3 层

指标: 循环依赖
  当前: 0 个 (好)
  目标: 维持 0 个 ✅

指标: 外部依赖数
  当前: 55+ 个包
  目标: 40 个包 (移除未使用的)
```

---

## 周进度报告模板

### Week 1-2 进度报告

```
日期: 2025-12-09 - 2025-12-20
阶段: 严重问题处理 (Critical Issues)

✅ 完成的任务:
  ├─ 凭证轮换 (2h) ✓
  ├─ Pre-commit hook 设置 (1h) ✓
  └─ 技术负债项目创建 (1h) ✓

🔄 进行中:
  ├─ 异常类定义 (3h/3h 完成) ✓
  ├─ stock_search.py 异常处理 (3h/4h)
  └─ auth.py 认证系统 (2h/4h)

⏳ 计划进行:
  ├─ market_data_service.py (剩余 3h)
  ├─ cache_manager.py (5h)
  └─ indicators.py (3h)

📊 指标变化:
  异常处理: 786 → 700+ (11% 改进)
  TODO 项: 20+ → 15+ (25% 改进)
  文件 > 1000 行: 10 → 9 (10% 改进)

💡 阻塞问题:
  - (如果有)

✅ 下周计划:
  - 继续异常处理重构 (剩余 15h)
  - 启动 TODO 项完成 (数据获取和缓存)
  - 测试和验证
```

---

## 仪表板数据收集

### 自动化收集脚本

```python
# scripts/collect_metrics.py

import os
import json
from pathlib import Path
from datetime import datetime

def count_large_files():
    """统计超大文件数"""
    large_files = []
    for py_file in Path('src').rglob('*.py'):
        lines = len(py_file.read_text().split('\n'))
        if lines > 500:
            large_files.append({
                'file': str(py_file),
                'lines': lines
            })
    return sorted(large_files, key=lambda x: x['lines'], reverse=True)

def count_exceptions():
    """统计异常捕获模式"""
    generic = 0
    specific = 0

    for py_file in Path('src').rglob('*.py'):
        content = py_file.read_text()
        generic += content.count('except Exception')
        specific += content.count('except ') - content.count('except Exception')

    return {'generic': generic, 'specific': specific}

def count_todos():
    """统计 TODO 注释"""
    todos = []
    for file_path in Path('src').rglob('*'):
        if file_path.is_file():
            try:
                content = file_path.read_text()
                for i, line in enumerate(content.split('\n'), 1):
                    if 'TODO' in line or 'FIXME' in line:
                        todos.append({
                            'file': str(file_path),
                            'line': i,
                            'content': line.strip()
                        })
            except:
                pass
    return todos

def collect_all_metrics():
    """收集所有指标"""
    metrics = {
        'timestamp': datetime.now().isoformat(),
        'large_files': count_large_files(),
        'exceptions': count_exceptions(),
        'todos': count_todos(),
    }

    # 保存到文件
    with open('metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)

    return metrics

if __name__ == '__main__':
    metrics = collect_all_metrics()
    print(json.dumps(metrics, indent=2))
```

### 指标收集计划

```bash
# 自动化收集
# 每日 00:00: 收集指标
# 0 0 * * * python scripts/collect_metrics.py

# 每周总结 (周五 18:00)
# 0 18 * * 5 python scripts/generate_weekly_report.py

# 每月报告 (月末 23:00)
# 0 23 L * * python scripts/generate_monthly_report.py
```

---

## 指标可视化

### 进度甘特图

```
Week 1-2: 严重问题处理
████████░░░░░░░░░░░░  42 小时
  │
  ├─ 凭证安全 ██░░░░░░ 2h
  ├─ 异常处理 ████████░░ 20h
  └─ TODO 完成 ██████░░░░ 20h

Week 3-4: 高优先级
░░░░░░░░░░░░░░░░░░░░ (等待)
  │
  ├─ 文件重构 ████████░░ 40h
  └─ 缓存统一 ██░░░░░░░░ 12h

Week 5-6: 中等优先级
░░░░░░░░░░░░░░░░░░░░ (等待)
  │
  ├─ TypeScript ████████░░ 40h
  ├─ 组件优化 ██████░░░░ 24h
  └─ 测试覆盖 ████░░░░░░ 12h

Week 7-8: 优先级低
░░░░░░░░░░░░░░░░░░░░ (等待)
  │
  ├─ 依赖审计 ██░░░░░░░░ 6h
  ├─ 配置统一 ██░░░░░░░░ 4h
  ├─ 代码提取 ████░░░░░░ 12h
  └─ Lint 配置 ██░░░░░░░░ 6h
```

### 质量趋势图

```
代码覆盖率趋势
100% │
     │                              ★ 目标
  80% │                         ✓
  70% │                     ✓
  60% │                ✓
  50% │          ✓
  40% │      ✓
  30% │★ 基准
     │____________________________________
     W1  W2  W3  W4  W5  W6  W7  W8

异常处理改进
786  │★ 基准
700  │   ★
600  │       ★
500  │           ★
400  │               ★
300  │                   ★
200  │                       ★
100  │                           ★
  0  │                               ★ 目标
     │____________________________________
     W1  W2  W3  W4  W5  W6  W7  W8
```

---

## 成功标准检查清单

### 第 1 阶段成功 (Week 1-2)

- [ ] 凭证完全轮换 (0 个泄露)
- [ ] Pre-commit hook 有效 (100% 防护)
- [ ] 异常处理: 786 → 0 (完全替换)
- [ ] TODO: 20+ → 0 (全部完成)
- [ ] 测试覆盖率: 30% → 40%+ (基本改进)
- [ ] 代码审查: 所有更改审查通过

### 第 2 阶段成功 (Week 3-4)

- [ ] 文件 > 500 行: 10 → 0
- [ ] 缓存系统: 3 → 1 (统一)
- [ ] 性能提升: +20% (基准测试验证)
- [ ] 代码覆盖率: 40% → 60%
- [ ] 文档完整率: 50% → 80%

### 第 3 阶段成功 (Week 5-6)

- [ ] TypeScript 迁移: 30% → 100%
- [ ] 组件优化: 大文件 → 小模块
- [ ] 测试覆盖率: 60% → 80%+
- [ ] E2E 通过率: 77.8% → 95%+

### 第 4 阶段成功 (Week 7-8)

- [ ] 依赖项审计: 0 个已知漏洞
- [ ] 配置统一: 8 → 3 文件
- [ ] 整体评分: 🟢 从 🔴 改进

---

## 报告和通信

### 每日 Standup

```
时间: 每日 09:30
参与: 全体团队
议程:
  1. 昨天完成: (2 min)
  2. 今天计划: (2 min)
  3. 阻塞问题: (1 min)
  4. 指标更新: (1 min)
```

### 每周周五报告

```
时间: 每周五 16:00
模板:
  1. 本周完成工时: X/Y 小时
  2. 指标变化: 表格显示
  3. 阻塞和风险: 列表
  4. 下周计划: 任务列表
  5. ROI 计算: 速度提升
```

### 每月管理评审

```
时间: 每月末
参与: 技术负债协调员 + 管理层
议程:
  1. 月度指标总结
  2. ROI 分析
  3. 风险评估
  4. 下月目标
```

---

**更新周期**: 每日自动收集，每周五生成报告
**维护者**: 技术负债协调员
**下次审查**: 2025-12-12
