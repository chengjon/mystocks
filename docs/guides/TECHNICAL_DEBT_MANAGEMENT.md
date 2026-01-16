# MyStocks 技术债务管理指南

> **文档版本**: v1.0  
> **更新日期**: 2026-01-14  
> **维护人**: 开发团队

---

## 📋 目录

1. [概述](#1-概述)
2. [技术债务识别](#2-技术债务识别)
3. [债务分类与优先级](#3-债务分类与优先级)
4. [偿还策略](#4-偿还策略)
5. [预防措施](#5-预防措施)
6. [债务追踪](#6-债务追踪)
7. [最佳实践](#7-最佳实践)

---

## 1. 概述

### 1.1 什么是技术债务

技术债务是指在软件开发过程中，为了短期交付而采取的次优技术决策，这些决策会在长期内增加维护成本和降低开发效率。

### 1.2 技术债务的来源

| 来源类型 | 示例 | 影响 |
|----------|------|------|
| **设计债务** | 架构设计不合理、模块耦合度高 | 修改困难、扩展受限 |
| **代码债务** | 重复代码、过长函数、缺少注释 | 可读性差、维护困难 |
| **测试债务** | 缺少单元测试、测试覆盖率低 | 回归风险高 |
| **文档债务** | 文档缺失、过期、不准确 | 新人上手慢 |
| **基础设施债务** | 过时依赖、配置混乱 | 安全风险、性能问题 |

### 1.3 评估框架

```
技术债务影响 = (修复成本) × (风险等级) / (业务价值)

- 修复成本: 修复该问题需要的工作量
- 风险等级: 该问题对系统的潜在影响
- 业务价值: 该功能对业务的贡献
```

---

## 2. 技术债务识别

### 2.1 代码层面识别

#### 代码复杂度检测

```bash
# 使用 radon 计算代码复杂度
pip install radon

radon cc src/ -a  # 分析圈复杂度
radon halstead src/ -a  # 分析代码量
radon mi src/ -a  # 计算维护指数

# 输出示例
# F   48:0 add_stop_loss_position - A (1)
# F   62:0 update_stop_loss_price - A (1)
# F   86:0 remove_stop_loss_position - A (1)
# CC   0.0 avg  9.0 max  24.0 total
```

#### 重复代码检测

```bash
# 使用 jscpd 检测重复代码
pip install jscpd

jscpd --min-tokens 50 src/ web/

# 输出示例
# 0.23% - 26克隆发现于 8 文件
# 最高重复文件:
# - src/adapters/financial_adapter.py (0.45%)
# - web/backend/app/api/v1/risk/core.py (0.32%)
```

#### 类型检查

```bash
# 使用 mypy 检查类型问题
pip install mypy

mypy src/ --ignore-missing-imports

# 输出示例
# src/core/config_driven_table_manager.py:164: error: Argument "table_name" has
# incompatible type "Optional[str]"; expected "str"
```

### 2.2 技术债务识别清单

| 债务类型 | 检测工具 | 阈值 | 当前状态 |
|----------|----------|------|----------|
| 代码重复 | jscpd | > 3% | ☐ |
| 圈复杂度 | radon | > 10 | ☐ |
| 函数长度 | radon | > 50 行 | ☐ |
| 文件长度 | wc -l | > 1000 行 | ☐ |
| 测试覆盖率 | pytest-cov | < 80% | ☐ |
| 类型错误 | mypy | 0 个 error | ☐ |
| 安全漏洞 | bandit | 0 个 high | ☐ |
| 过时依赖 | pip-review | 无过期 | ☐ |

### 2.3 识别方法

#### 手动审查

```markdown
# 代码审查清单

## 代码质量
- [ ] 代码是否遵循项目规范？
- [ ] 是否有重复代码？
- [ ] 函数/类是否过长？
- [ ] 命名是否清晰？

## 测试覆盖
- [ ] 核心逻辑是否有测试？
- [ ] 测试是否可读可维护？
- [ ] 测试是否稳定（无随机失败）？

## 文档
- [ ] 复杂逻辑是否有注释？
- [ ] API 是否有文档？
- [ ] 配置是否已记录？
```

#### 自动化扫描

```bash
#!/bin/bash
# 技术债务扫描脚本

echo "=== 技术债务扫描 ==="

echo "--- 代码重复检测 ---"
jscpd --min-tokens 50 src/ web/ 2>/dev/null || echo "jscpd 未安装"

echo ""
echo "--- 代码复杂度分析 ---"
radon cc src/ -a 2>/dev/null || echo "radon 未安装"

echo ""
echo "--- 类型检查 ---"
mypy src/ --ignore-missing-imports 2>/dev/null || echo "mypy 未安装"

echo ""
echo "--- 安全扫描 ---"
bandit -r src/ 2>/dev/null || echo "bandit 未安装"

echo ""
echo "--- 测试覆盖率 ---"
pytest --cov=src --cov-report=term-missing 2>/dev/null || echo "pytest 未安装"
```

---

## 3. 债务分类与优先级

### 3.1 债务分类

#### 按紧急程度分类

| 类别 | 描述 | 处理策略 |
|------|------|----------|
| **紧急债务** | 安全漏洞、高风险缺陷 | 立即修复 |
| **重要债务** | 影响开发效率的问题 | 近期修复 |
| **普通债务** | 长期维护问题 | 定期修复 |
| **可选债务** | 优化建议 | 有空时处理 |

#### 按类型分类

| 类型 | 示例 | 影响范围 | 优先级 |
|------|------|----------|--------|
| **安全债务** | SQL 注入、XSS 漏洞 | 整个系统 | P0 |
| **性能债务** | N+1 查询、未优化索引 | 特定功能 | P1 |
| **可维护性债务** | 过长函数、重复代码 | 代码库 | P2 |
| **技术升级债务** | 过时依赖、废弃 API | 依赖升级 | P2 |
| **文档债务** | 缺失文档、过时注释 | 新人上手 | P3 |

### 3.2 优先级矩阵

```
高影响 × 低修复成本 = 立即处理
高影响 × 高修复成本 = 计划处理
低影响 × 低修复成本 = 有空处理
低影响 × 高修复成本 = 忽略或重写
```

### 3.3 债务登记模板

```markdown
# 技术债务登记

## 债务 #001
- **描述**: risk_management.py 文件过长（2070行）
- **类型**: 可维护性
- **影响**: 修改困难、难以测试
- **修复成本**: 3 人天
- **优先级**: P1
- **状态**: 已修复
- **解决日期**: 2026-01-14
- **解决方案**: 按领域拆分为 6 个子模块

## 债务 #002
- **描述**: 缺少 ArtDeco 组件样式规范
- **类型**: 可维护性
- **影响**: 样式不一致、维护困难
- **修复成本**: 1 人天
- **优先级**: P2
- **状态**: 进行中
- **解决方案**: 创建 ARTDECO_COMPONENT_GUIDE.md
```

---

## 4. 偿还策略

### 4.1 偿还方法

#### 方法一：专注日

```
安排每周五为"技术债务偿还日"
- 修复 1-2 个中等优先级的债务
- 重构 1 个代码模块
- 更新文档
```

#### 方法二：Boy Scout Rule

```
"每次接触代码时，让它比之前更整洁"
- 提交时修复小问题
- 改进变量命名
- 添加缺失注释
```

#### 方法三：特性驱动偿还

```
在开发新特性时偿还相关债务
- 重构相关代码
- 添加缺失测试
- 更新相关文档
```

### 4.2 重构策略

#### 逐步重构

```python
# 阶段 1: 包装旧代码
class LegacyRiskManager:
    def __init__(self):
        self.old_manager = risk_management  # 旧代码
    
    def calculate_var(self, data):
        # 新方法调用旧实现
        return self.old_manager.calculate_var(data)


# 阶段 2: 添加新方法
class LegacyRiskManager:
    def calculate_var_new(self, data):
        # 新的优化实现
        pass


# 阶段 3: 迁移流量
class LegacyRiskManager:
    def calculate_var(self, data):
        # 切换到新实现
        return self.calculate_var_new(data)


# 阶段 4: 删除旧代码
class RiskManager:
    def calculate_var(self, data):
        # 纯新实现
        pass
```

#### 特性开关重构

```python
# 使用特性开关控制重构代码
from features import feature_flags

def calculate_var(self, data):
    if feature_flags.is_enabled('new_risk_calculator'):
        return self._calculate_var_new(data)
    else:
        return self._calculate_var_old(data)
```

### 4.3 偿还清单

| 债务类型 | 偿还方法 | 验证方式 |
|----------|----------|----------|
| 代码重复 | 提取公共函数 | jscpd 检查 |
| 函数过长 | 拆分为小函数 | 圈复杂度 < 10 |
| 类型缺失 | 添加类型注解 | mypy 检查通过 |
| 测试不足 | 添加单元测试 | 覆盖率 > 80% |
| 文档缺失 | 补充文档 | 文档完整性检查 |
| 过时依赖 | 升级依赖 | pip-compile 检查 |

---

## 5. 预防措施

### 5.1 代码质量门禁

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: code-quality-check
        name: Code Quality Check
        entry: ./scripts/ci/code_quality_check.sh
        language: system
        pass_filenames: false
        stages: [push]

      - id: max-file-length
        name: Max File Length (1000 lines)
        entry: ./scripts/ci/check_file_length.sh
        language: system
        files: \.(py|vue|ts)$
        exclude: ^tests/

      - id: test-coverage-check
        name: Test Coverage Check (80%)
        entry: ./scripts/ci/check_coverage.sh
        language: system
        stages: [push]
```

### 5.2 CI/CD 集成

```yaml
# .github/workflows/technical-debt-monitor.yml
name: Technical Debt Monitor

on:
  schedule:
    - cron: '0 0 * * 0'  # 每周日检查
  workflow_dispatch:

jobs:
  debt-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install tools
        run: |
          pip install radon jscpd mypy bandit

      - name: Run debt analysis
        run: |
          echo "## 技术债务分析" >> $GITHUB_STEP_SUMMARY
          echo "### 代码重复检测" >> $GITHUB_STEP_SUMMARY
          jscpd --min-tokens 50 src/ web/ >> $GITHUB_STEP_SUMMARY || true
          
          echo "### 复杂度分析" >> $GITHUB_STEP_SUMMARY
          radon cc src/ -a >> $GITHUB_STEP_SUMMARY || true
          
          echo "### 类型检查" >> $GITHUB_STEP_SUMMARY
          mypy src/ --ignore-missing-imports >> $GITHUB_STEP_SUMMARY || true

      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: debt-report
          path: debt_report/
```

### 5.3 团队规范

```markdown
# 技术债务预防规范

## 编码规范
1. 遵循 PEP 8 / Airbnb JavaScript Style Guide
2. 函数不超过 50 行
3. 类不超过 500 行
4. 文件不超过 1000 行
5. 圈复杂度不超过 10

## 测试规范
1. 核心业务逻辑必须有单元测试
2. 测试覆盖率不低于 80%
3. 新功能必须包含测试

## 文档规范
1. 公共 API 必须有文档字符串
2. 复杂算法必须添加注释
3. 配置文件必须记录

## 提交规范
1. 提交信息必须描述做了什么
2. 避免大块提交（>500 行变更）
3. 包含相关 Issue 链接
```

---

## 6. 债务追踪

### 6.1 债务登记

```markdown
# docs/technical_debt_register.md

## 技术债务登记表

### 已识别债务

| ID | 描述 | 类型 | 优先级 | 状态 | 负责人 | 预计修复 |
|----|------|------|--------|------|--------|----------|
| TD-001 | risk_management.py 过长 | 可维护性 | P1 | 已修复 | Dev | 3d |
| TD-002 | 缺少组件样式规范 | 可维护性 | P2 | 进行中 | Dev | 1d |
| TD-003 | 过时依赖升级 | 技术升级 | P2 | 待处理 | Dev | 2d |

### 历史记录

| 日期 | 行动 | 债务 ID | 说明 |
|------|------|---------|------|
| 2026-01-14 | 修复 | TD-001 | 拆分为 6 个子模块 |
```

### 6.2 债务仪表板

```
┌─────────────────────────────────────────────────────────┐
│              技术债务仪表板                              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  紧急债务 (P0)    │  ████████░░░░░░░░░░  2              │
│  重要债务 (P1)    │  ██████████████░░░░░  10             │
│  普通债务 (P2)    │  ████████████████████  18             │
│  可选债务 (P3)    │  ██████████████████░░  15             │
│                                                          │
│  ────────────────────────────────────────────────────    │
│                                                          │
│  本月偿还进度        ████████████░░░░░░░░░░░░  40%       │
│                                                          │
│  债务减少趋势        ↑ 12 → ↓ 8 → → 15                   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 6.3 追踪指标

| 指标 | 计算方式 | 目标 | 当前值 |
|------|----------|------|--------|
| 债务数量 | 登记债务总数 | 持续减少 | ☐ |
| 偿还率 | 本月偿还/新增 | > 150% | ☐ |
| 紧急债务数 | P0 债务数 | < 2 | ☐ |
| 平均修复时间 | 总修复时间/债务数 | < 3 天 | ☐ |

---

## 7. 最佳实践

### 7.1 债务预防优先级

```
优先级排序：
1. 🔴 安全债务 - 安全漏洞必须立即处理
2. 🔴 性能债务 - 显著影响用户体验的问题
3. 🟡 可维护性债务 - 影响开发效率的问题
4. 🟢 优化债务 - 锦上添花的改进
```

### 7.2 偿还时机

| 场景 | 是否偿还 | 说明 |
|------|----------|------|
| 开发新功能时 | ✅ 是 | 顺便重构相关代码 |
| Bug 修复时 | ✅ 是 | 改进周围代码质量 |
| 代码审查时 | ✅ 是 | 标记债务待处理 |
| 发布前 | ❌ 否 | 避免引入新问题 |
| 紧急修复时 | ❌ 否 | 聚焦修复本身 |

### 7.3 避免常见陷阱

| 陷阱 | 避免方法 |
|------|----------|
| **过度重构** | 设定时间限制，逐步改进 |
| **忽视业务价值** | 优先处理影响用户的债务 |
| **完美主义** | 接受"足够好"的代码 |
| **孤立偿还** | 与业务需求结合 |

### 7.4 成功指标

- ✅ 债务增长率持续低于偿还率
- ✅ 紧急债务数量控制在 2 个以内
- ✅ 代码重复率低于 3%
- ✅ 测试覆盖率保持在 80% 以上
- ✅ 新人上手时间持续缩短

---

## 📚 相关文档

- [代码规范](../standards/)
- [重构指南](./REFACTORING_GUIDE.md)
- [测试规范](../04-测试与质量保障文档/TESTING_STANDARDS.md)
- [故障排除手册](./TROUBLESHOOTING.md)

---

*最后更新: 2026-01-14*
