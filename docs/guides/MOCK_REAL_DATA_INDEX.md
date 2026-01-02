# Mock/Real数据文档索引

**最后更新**: 2026-01-02
**维护者**: Main CLI (Claude Code)

---

## 📋 快速导航

### 🎯 我想要...

| 需求 | 推荐文档 |
|------|---------|
| 了解如何切换Mock/Real模式 | [Mock/Real数据切换指南](#mockreal数据切换指南) |
| 了解前端环境切换 | [前端环境切换指南](#前端环境切换指南) |
| 了解Mock数据使用规范 | [Mock数据使用规则](#mock数据使用规则) |
| 查看所有相关文档列表 | [本文档](#mockreal数据文档索引) |
| 了解环境切换实现细节 | [环境切换实现报告](#环境切换实现报告) |
| 了解Real数据集成原则 | [Real数据集成原则](#real数据集成原则-历史参考) |

---

## 📚 核心文档

### 1. Mock/Real数据切换指南

**路径**: `docs/guides/MOCK_REAL_DATA_SWITCHING_GUIDE.md`
**类型**: 核心用户指南
**大小**: 13KB
**最后更新**: 2026-01-01
**阅读时间**: 10分钟
**适用人群**: 开发人员、测试人员、运维人员

**内容概览**:
- ✅ 三层数据源架构设计
- ✅ 环境变量驱动的数据源切换机制
- ✅ 后端数据源切换（USE_MOCK_DATA）
- ✅ 前端API端点切换（VITE_APP_MODE）
- ✅ 实战示例和最佳实践
- ✅ 常见问题解答

**快速链接**:
```bash
# 查看文档
cat docs/guides/MOCK_REAL_DATA_SWITCHING_GUIDE.md

# 或使用代码编辑器打开
code docs/guides/MOCK_REAL_DATA_SWITCHING_GUIDE.md
```

---

### 2. Mock数据使用规则

**路径**: `docs/guides/MOCK_DATA_USAGE_RULES.md`
**类型**: 开发规范
**大小**: 13KB
**最后更新**: 2025-12-21
**阅读时间**: 8分钟
**适用人群**: 开发人员

**内容概览**:
- ✅ Mock数据核心原则
- ✅ 正确的Mock数据使用方式
- ✅ 禁止的硬编码数据模式
- ✅ Mock数据工厂使用说明
- ✅ 常见错误示例和修正方法

**核心规则**:
```python
# ✅ 正确: 通过工厂函数获取Mock数据
from src.data_sources.factory import get_timeseries_source
source = get_timeseries_source(source_type="mock")
data = source.get_kline_data(symbol, start_time, end_time, interval)

# ❌ 错误: 直接硬编码数据
historical_data = [
    {"date": "2025-01-01", "close": 10.5},  # 严禁!
]
```

---

### 3. 前端环境切换指南

**路径**: `web/frontend/ENVIRONMENT_SWITCHING_GUIDE.md`
**类型**: 前端开发指南
**大小**: 5KB
**最后更新**: 2026-01-02
**阅读时间**: 5分钟
**适用人群**: 前端开发人员

**内容概览**:
- ✅ Mock模式和Real模式对比
- ✅ 快速切换方法
- ✅ 验证当前模式
- ✅ 配置对比
- ✅ 使用场景
- ✅ 故障排除

**快速切换**:
```bash
# 切换到Mock模式
cd web/frontend
cp .env.mock .env
npm run dev

# 切换到Real模式
cd web/frontend
cp .env.real .env
npm run dev
```

---

### 4. 环境切换实现报告

**路径**: `docs/reports/ENVIRONMENT_SWITCHING_IMPLEMENTATION_REPORT.md`
**类型**: 技术实现报告
**大小**: 20KB
**最后更新**: 2026-01-02
**阅读时间**: 15分钟
**适用人群**: 架构师、技术负责人

**内容概览**:
- ✅ 实现任务概述
- ✅ 后端配置更新
- ✅ 前端服务更新
- ✅ NPM脚本添加
- ✅ 环境配置文件
- ✅ 架构分析
- ✅ 测试验证结果

**技术亮点**:
- 后端通过 `USE_MOCK_DATA` 控制Mock API注册
- 前端通过 `VITE_APP_MODE` 动态选择API端点
- 保留所有功能，不降级、不取消功能
- 完整的测试验证

---

## 📌 历史参考文档

### 5. Real数据集成原则

**路径**: `docs/guides/REAL_DATA_INTEGRATION_PRINCIPLES.md`
**类型**: 历史参考文档
**大小**: 27KB
**最后更新**: 2025-12-21
**状态**: ⚠️ 部分内容已被新指南替代

**说明**:
本文档包含Real数据集成的架构原则和设计思路，部分内容已被新的环境切换指南更新和替代。建议优先阅读 `MOCK_REAL_DATA_SWITCHING_GUIDE.md`，本文档保留作为历史参考。

**相关内容**:
- 数据分类体系
- 数据存储策略
- 质量保证机制
- 性能优化方案

---

## 🎓 按角色分类的文档推荐

### 前端开发人员
1. **必读**: [前端环境切换指南](../web/frontend/ENVIRONMENT_SWITCHING_GUIDE.md)
2. **推荐**: [Mock/Real数据切换指南](./MOCK_REAL_DATA_SWITCHING_GUIDE.md) - 第4节"前端配置"

### 后端开发人员
1. **必读**: [Mock/Real数据切换指南](./MOCK_REAL_DATA_SWITCHING_GUIDE.md)
2. **必读**: [Mock数据使用规则](./MOCK_DATA_USAGE_RULES.md)
3. **推荐**: [环境切换实现报告](../reports/ENVIRONMENT_SWITCHING_IMPLEMENTATION_REPORT.md)

### 测试人员
1. **必读**: [前端环境切换指南](../web/frontend/ENVIRONMENT_SWITCHING_GUIDE.md)
2. **推荐**: [Mock/Real数据切换指南](./MOCK_REAL_DATA_SWITCHING_GUIDE.md) - 第5节"验证方法"

### 运维人员
1. **必读**: [Mock/Real数据切换指南](./MOCK_REAL_DATA_SWITCHING_GUIDE.md)
2. **推荐**: [环境切换实现报告](../reports/ENVIRONMENT_SWITCHING_IMPLEMENTATION_REPORT.md) - 第6节"使用方法"

### 架构师
1. **推荐**: [环境切换实现报告](../reports/ENVIRONMENT_SWITCHING_IMPLEMENTATION_REPORT.md)
2. **参考**: [Real数据集成原则](./REAL_DATA_INTEGRATION_PRINCIPLES.md) - 历史参考

---

## 🔍 文档关键词索引

### 快速查找关键词

| 关键词 | 相关文档 | 章节 |
|--------|---------|------|
| 环境切换 | Mock/Real数据切换指南 | 第3节 |
| USE_MOCK_DATA | Mock/Real数据切换指南 | 第3.1节 |
| VITE_APP_MODE | 前端环境切换指南 | 第3节 |
| Mock数据规范 | Mock数据使用规则 | 全文 |
| API端点切换 | 环境切换实现报告 | 第3.3节 |
| 故障排除 | 前端环境切换指南 | 第6节 |
| 数据源架构 | Mock/Real数据切换指南 | 第2节 |
| 实现细节 | 环境切换实现报告 | 全文 |

---

## 📊 文档统计

| 类型 | 数量 | 总大小 |
|------|------|--------|
| 核心指南 | 3 | 31KB |
| 前端指南 | 1 | 5KB |
| 实现报告 | 1 | 20KB |
| 历史参考 | 1 | 27KB |
| **总计** | **6** | **83KB** |

---

## 🔄 文档更新历史

### 2026-01-02
- ✅ 创建前端环境切换指南
- ✅ 创建环境切换实现报告
- ✅ 删除10个过时/重复文档
- ✅ 创建本文档索引

### 2025-12-21
- ✅ 更新Mock数据使用规则
- ✅ 更新Real数据集成原则

### 2025-01-21
- ✅ 创建Mock/Real数据切换指南（初版）

---

## ❓ 常见问题

### Q: 如何快速切换到Mock模式？
**A**: 参考[前端环境切换指南](../web/frontend/ENVIRONMENT_SWITCHING_GUIDE.md)的"快速切换"章节。

### Q: Mock数据使用有哪些规则？
**A**: 参考[Mock数据使用规则](./MOCK_DATA_USAGE_RULES.md)的核心原则章节。

### Q: 环境切换如何实现的？
**A**: 参考[环境切换实现报告](../reports/ENVIRONMENT_SWITCHING_IMPLEMENTATION_REPORT.md)的技术实现部分。

### Q: 遇到问题如何排查？
**A**: 参考[前端环境切换指南](../web/frontend/ENVIRONMENT_SWITCHING_GUIDE.md)的故障排除章节。

---

## 📞 反馈与贡献

如果您发现文档有任何问题或有改进建议，请：
1. 提交Issue描述问题
2. 提交PR直接修改文档
3. 联系维护者：Main CLI (Claude Code)

---

**文档版本**: 1.0
**维护周期**: 按需更新
**文档状态**: ✅ 最新
