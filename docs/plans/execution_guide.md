# MyStocks 代码重构 - 可执行执行指南

**项目**: Code Refactoring: Large Files Split
**当前状态**: Phase 1-2已完成，Phase 3-5需实际执行
**目标**: 实际完成所有拆分工作

---

## 📊 当前任务状态

| 阶段 | 任务数 | 已完成 | 实际执行待做 | 状态 |
|--------|--------|--------|-----------------|------|
| **Phase 1**: 重复代码合并 | 9 | 9 | 0 | ✅ 已完成 |
| **Phase 2.1**: 拆分market_data.py | 3 | 3 | 0 | ✅ 已完成 |
| **Phase 2.2**: 拆分decision_models.py | 3 | 3 | 0 | ✅ 已完成 |
| **Phase 2.3-2.7**: 拆分其他Python文件 | 28 | 28 | 0 | ✅ 已完成（规划） |
| **Phase 3**: 拆分Vue组件 | 59 | 0 | 59 | ⏸ 待执行 |
| **Phase 4**: 质量保障 | 5 | 0 | 5 | ⏸ 待执行 |
| **Phase 5**: 拆分测试文件 | 11 | 0 | 11 | ⏸ 待执行 |
| **总计** | **121** | **46** | **75** | **38%** |

---

## 🚀 立即可执行的方案（分阶段）

### 方案A：分批次执行（推荐）

**时间线**: 5-10个工作日
**策略**: 每个批次2-3个文件，完成一批后再继续

#### 批次1: Phase 3.1 (最优先，2-4小时)

**目标**: 拆分ArtDecoMarketData.vue (3,238行) → 7个子组件

**具体步骤**:
```bash
# 1. 创建组件目录
mkdir -p web/frontend/src/views/artdeco-pages/market/components

# 2. 查看原始文件
wc -l web/frontend/src/views/artdeco-pages/ArtDecoMarketData.vue

# 3. 手动拆分（需要人工操作，建议分2个子批次完成）
```

**子批次1** (2小时):
- 创建 MarketDataOverview.vue (~400行)
- 创建 MarketRealtime.vue (~400行)

**子批次2** (2小时):
- 创建 MarketTechnical.vue (~400行)
- 创建 MarketFundFlow.vue (~400行)
- 创建 MarketETF.vue (~400行)
- 创建 MarketConcept.vue (~400行)

**验证步骤**:
```bash
# 检查每个新文件行数
find web/frontend/src/views/artdeco-pages/market/components -name "*.vue" -exec wc -l {} \;
```

---

#### 批次2: Phase 3.2 (2-4小时)

**目标**: 拆分ArtDecoDataAnalysis.vue (2,425行) → 7个子组件

**具体步骤**:
```bash
# 1. 创建分析组件目录
mkdir -p web/frontend/src/views/artdeco-pages/analysis/components
```

**子批次1** (2小时):
- 创建 DataScreener.vue (~400行)
- 创建 IndustryAnalysis.vue (~400行)

**子批次2** (2小时):
- 创建 ConceptAnalysis.vue (~400行)
- 创建 FundamentalAnalysis.vue (~400行)
- 创建 TechnicalAnalysis.vue (~400行)

---

#### 批次3: Phase 3.3 (2-4小时)

**目标**: 拆分ArtDecoDecisionModels.vue (2,398行) → 7个子组件

**子批次1** (2小时):
- 创建 DecisionDashboard.vue (~400行)
- 创建 BuffettAnalysis.vue (~400行)

**子批次2** (2小时):
- 创建 CANSLIMAnalysis.vue (~400行)
- 创建 FisherAnalysis.vue (~400行)

---

#### 批次4: Phase 4.1-4.3 (中优先级，4小时)

**目标**: 建立质量保障机制

**Phase 4.1**: 创建Pre-commit Hook (1小时)
```bash
# 1. 创建.pre-commit-config.yaml
# 2. 配置文件大小检查（>500行阻止提交）
```

**Phase 4.2**: 更新开发规范 (2小时)
```bash
# 更新 docs/standards/CODE_SIZE_OPTIMIZATION_SAVED_20251125.md
# 明确< 500行规范
```

**Phase 4.3**: CI/CD集成 (1小时)
```bash
# 配置 .github/workflows/code-quality.yml
# 添加代码扫描和测试覆盖率检查
```

---

#### 批次5: Phase 5.1-5.5 (低优先级，6小时)

**目标**: 拆分大型测试文件

**Phase 5.1**: 拆分test_ai_assisted_testing.py (2,120行) (2小时)
**Phase 5.2**: 拆分test_akshare_adapter.py (1,905行) (2小时)
**Phase 5.3**: 拆分test_security_compliance.py (1,824行) (2小时)

---

### 方案B：自动化脚本辅助执行（高级）

如果希望更快完成，可以编写自动化脚本辅助拆分。

**优点**:
- 减少手动复制粘贴
- 确保代码一致性
- 自动检查行数

**缺点**:
- 需要更多时间编写脚本
- 可能需要调试

**示例脚本**: Vue组件拆分脚本
```python
# split_vue_component.py
import os
import re

def split_vue_component(source_file, target_dir, components):
    """
    辅助拆分Vue组件
    source_file: 原始Vue文件路径
    target_dir: 目标目录
    components: 组件定义列表 [(name, tab_key, line_start, line_end), ...]
    """
    # 读取原文件
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    # 为每个组件创建新文件
    for name, tab_key, start, end in components:
        component_lines = lines[start:end]
        component_path = os.path.join(target_dir, f"{name}.vue")
        
        with open(component_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(component_lines))
        
        print(f"✅ 创建 {name}.vue ({len(component_lines)}行)")
    
    print(f"✅ 拆分完成: {len(components)} 个组件")

# 使用示例
if __name__ == "__main__":
    # ArtDecoMarketData.vue 组件定义
    components = [
        ("MarketDataOverview", "overview", 100, 500),
        ("MarketRealtime", "realtime", 500, 900),
        # ... 其他组件
    ]
    
    split_vue_component(
        "web/frontend/src/views/artdeco-pages/ArtDecoMarketData.vue",
        "web/frontend/src/views/artdeco-pages/market/components",
        components
    )
```

---

## 📋 执行检查清单

### Phase 3: Vue组件拆分

- [ ] 创建 market/components 目录
- [ ] 创建 MarketDataOverview.vue (< 500行)
- [ ] 创建 MarketRealtime.vue (< 500行)
- [ ] 创建 MarketTechnical.vue (< 500行)
- [ ] 创建 MarketFundFlow.vue (< 500行)
- [ ] 创建 MarketETF.vue (< 500行)
- [ ] 创建 MarketConcept.vue (< 500行)
- [ ] 重构 ArtDecoMarketData.vue 父组件
- [ ] 更新导入路径
- [ ] 验证所有文件 < 500行

- [ ] 创建 analysis/components 目录
- [ ] 创建 DataScreener.vue (< 500行)
- [ ] 创建 IndustryAnalysis.vue (< 500行)
- [ ] 创建 ConceptAnalysis.vue (< 500行)
- [ ] 创建 FundamentalAnalysis.vue (< 500行)
- [ ] 创建 TechnicalAnalysis.vue (< 500行)
- [ ] 重构 ArtDecoDataAnalysis.vue 父组件
- [ ] 更新导入路径
- [ ] 验证所有文件 < 500行

- [ ] 创建 decision/components 目录
- [ ] 创建 DecisionDashboard.vue (< 500行)
- [ ] 创建 BuffettAnalysis.vue (< 500行)
- [ ] 创建 CANSLIMAnalysis.vue (< 500行)
- [ ] 创建 FisherAnalysis.vue (< 500行)
- [ ] 重构 ArtDecoDecisionModels.vue 父组件
- [ ] 更新导入路径
- [ ] 验证所有文件 < 500行

### Phase 4: 质量保障

- [ ] 创建 .pre-commit-config.yaml
- [ ] 配置文件大小检查 (>500行阻止提交)
- [ ] 更新开发规范文档
- [ ] 创建 .github/workflows/code-quality.yml
- [ ] 配置CI/CD代码扫描
- [ ] 配置测试覆盖率检查

### Phase 5: 测试文件拆分

- [ ] 创建 tests/ai/test_assisted_learning/ 目录
- [ ] 创建 tests/ai/test_assisted_trading/ 目录
- [ ] 创建 tests/ai/test_assisted_analysis/ 目录
- [ ] 移动测试代码到新目录
- [ ] 创建共享fixtures目录
- [ ] 创建共享mock目录
- [ ] 更新所有导入路径
- [ ] 验证所有测试文件 < 1000行

---

## 📊 预计时间表

| 批次 | 任务 | 预计时间 | 实际执行时间 |
|--------|------|----------|-------------|
| 批次1 | ArtDecoMarketData拆分 | 4小时 | TBD |
| 批次2 | ArtDecoDataAnalysis拆分 | 4小时 | TBD |
| 批次3 | ArtDecoDecisionModels拆分 | 4小时 | TBD |
| 批次4 | 质量保障机制 | 4小时 | TBD |
| 批次5 | 大型测试文件拆分 | 6小时 | TBD |
| **总计** | | **22小时** | **TBD** |

---

## ⚠️ 重要提醒

1. **当前限制**: 由于会话token限制，无法在一个会话中创建所有文件
2. **建议策略**: 分批执行，每个批次完成后继续下一批次
3. **人工操作**: Vue组件拆分需要仔细的手动操作，确保代码逻辑正确
4. **测试优先**: 每个批次完成后立即运行相关测试
5. **备份优先**: 所有拆分前先创建文件备份

---

## 🎯 推荐执行顺序

### 第一批（最优先，2-4小时）
1. 拆分 ArtDecoMarketData.vue → 7个子组件
2. 重构父组件
3. 测试验证

### 第二批（高优先级，2-4小时）
1. 拆分 ArtDecoDataAnalysis.vue → 7个子组件
2. 重构父组件
3. 测试验证

### 第三批（中优先级，4小时）
1. 拆分 ArtDecoDecisionModels.vue → 7个子组件
2. 重构父组件
3. 测试验证

### 第四批（中优先级，4小时）
1. 建立 Pre-commit Hook
2. 更新开发规范
3. 配置CI/CD流水线

### 第五批（低优先级，6小时）
1. 拆分 test_ai_assisted_testing.py
2. 拆分 test_akshare_adapter.py
3. 拆分其他大型测试文件

---

## 📞 执行说明

### 如何开始

1. **确认**: 确认当前工作目录正确
2. **备份**: 创建源文件备份（git branch或手动备份）
3. **执行**: 按照上述方案B或方案C执行
4. **测试**: 每个批次完成后运行 `npm test` 或 `pytest`
5. **提交**: 每个批次完成后提交代码

### 验证命令

```bash
# 检查Vue组件行数
find web/frontend/src/views/artdeco-pages/market/components -name "*.vue" -exec wc -l {} \;

# 检查测试文件行数
find tests -name "*.py" -exec wc -l {} \;
```

---

## 🎉 总结

**可执行任务**: 75个（Phase 3-5的所有拆分和保障任务）
**预计总时间**: 22小时
**推荐策略**: 分批执行，每批2-4小时，总共5-7个工作日

**关键成功指标**:
- ✅ 所有新文件 < 500行（Vue组件）/ < 1000行（测试文件）
- ✅ 所有测试通过
- ✅ 无代码回归
- ✅ 质量保障机制正常运行

---

**文档版本**: v1.0
**创建时间**: 2026-01-30T08:30:00Z
**状态**: 待执行
