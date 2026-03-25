# MyStocks BUG报告系统使用指南

**目的**: 记录具有一定难度/或出现频度高的BUG，总结经验教训，为后续开发提供预防指引。

---

## 📁 文件结构

```
docs/
├── standards/
│   └── bug-report-template.json          # BUG报告模板
├── guides/
│   └── BUG_LESSONS_LEARNED.md             # 经验教训索引
└── quality/
    └── bugs/                              # BUG报告存储目录
        ├── BUG-20260108-ERR_DDD_IMPORT_001.json
        ├── BUG-20260108-ERR_FLOAT_PRECISION_001.json
        └── ...
```

---

## 🚀 快速开始

### 1. 登记BUG

当发现需要登记的BUG时，使用以下任一命令：

```
"登记BUG"
"记BUG"
"登记bug"
"记bug"
```

Claude Code将自动：
1. 读取BUG报告模板
2. 填写BUG信息
3. 保存到 `docs/quality/bugs/BUG-YYYYMMDD-{errorCode}.json`
4. 更新经验教训索引

### 2. 查阅经验教训

在开始开发前，查阅经验教训索引：

```bash
# 查看常见BUG类型和预防措施
cat docs/guides/BUG_LESSONS_LEARNED.md
```

### 3. 手动登记BUG

如果需要手动登记BUG：

```bash
# 1. 复制模板
cp docs/standards/bug-report-template.json temp-bug.json

# 2. 填写BUG信息（参考模板中的说明）
vim temp-bug.json

# 3. 保存到正确位置
mv temp-bug.json docs/quality/bugs/BUG-YYYYMMDD-{errorCode}.json
```

---

## 📝 BUG报告模板

### 支持两种格式

#### 格式1：单个BUG

```json
{
  "metadata": {
    "version": "1.0",
    "format": "mystocks-bug-report",
    "reportedAt": "2026-01-08T11:30:00Z",
    "reporter": "Claude Code"
  },
  "bug": {
    "errorCode": "ERR_DDD_IMPORT_001",
    "title": "DDD模块导入路径错误",
    "message": "详细错误描述...",
    "severity": "high",
    "context": {
      "projectName": "MyStocks",
      "component": "domain-layer"
    }
  }
}
```

#### 格式2：批量BUG（推荐）

```json
{
  "metadata": {
    "version": "1.0",
    "format": "mystocks-bug-report",
    "reportedAt": "2026-01-08T11:30:00Z",
    "reporter": "Claude Code",
    "description": "今日测试发现的问题汇总"
  },
  "bugs": [
    {
      "errorCode": "ERR_DDD_IMPORT_001",
      "title": "DDD模块导入路径错误",
      "message": "详细错误描述...",
      "severity": "high"
    },
    {
      "errorCode": "ERR_FLOAT_PRECISION_001",
      "title": "浮点数精度比较",
      "message": "详细错误描述...",
      "severity": "medium"
    }
  ]
}
```

### 必填字段说明

| 字段 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `errorCode` | ✅ | 大写字母、数字、下划线 | `ERR_DDD_IMPORT_001` |
| `title` | ✅ | BUG标题 | "DDD模块导入路径错误" |
| `message` | ✅ | 详细错误描述 | "在Phase 6验证测试时..." |
| `severity` | ✅ | 严重程度 | `critical`/`high`/`medium`/`low` |
| `stackTrace` | ❌ | 错误堆栈信息 | `ModuleNotFoundError: ...` |
| `context` | ❌ | 上下文信息（强烈建议） | `{projectName, component, phase}` |

### 严重程度分级

| 级别 | 标识 | 响应时间 | 使用场景 |
|------|------|----------|----------|
| 🔴 **critical** | 崩溃 | **立即修复** | 系统不可用、数据丢失、安全漏洞 |
| 🟠 **high** | 严重 | **4小时内** | 核心功能不可用、性能严重下降 |
| 🟡 **medium** | 中等 | **24小时内** | 功能异常、有workaround |
| 🟢 **low** | 轻微 | **下迭代** | UI问题、代码规范 |

---

## 📚 经验教训索引

**文档位置**: `docs/guides/BUG_LESSONS_LEARNED.md`

### 核心功能

1. **记录常见BUG类型**: DDD架构、数据类型、测试、导入、配置
2. **提供预防措施**: 每个BUG都有详细的预防指引
3. **快速参考**: 错误代码速查表、严重程度定义
4. **检查清单**: 开发前检查清单

### 使用方法

```bash
# 开发前查阅
cat docs/guides/BUG_LESSONS_LEARNED.md

# 搜索特定类型的BUG
grep "ERR_DDD" docs/guides/BUG_LESSONS_LEARNED.md
```

---

## 🔧 开发前检查清单

在开始开发前，请确认：

- [ ] **查阅经验教训索引**: `docs/guides/BUG_LESSONS_LEARNED.md`
- [ ] **读取现有实现**: 使用Glob/Grep查找相关代码
- [ ] **理解现有API**: 检查方法签名、参数、返回值
- [ ] **验证导入路径**: 确保`__init__.py`正确导出
- [ ] **了解命名约定**: 遵循现有代码风格
- [ ] **运行现有测试**: 确保基线测试通过

---

## 🎯 已记录的BUG类型

### DDD架构问题

| 错误代码 | 问题 | 预防措施 |
|---------|------|---------|
| `ERR_DDD_DATACLASS_ORDER_001` | Dataclass字段顺序错误 | required字段在前 |
| `ERR_DDD_PROPERTY_PARAM_001` | Property参数错误 | 使用普通方法 |

### 数据类型问题

| 错误代码 | 问题 | 预防措施 |
|---------|------|---------|
| `ERR_FLOAT_PRECISION_001` | 浮点数精度比较 | 使用近似判断 |

### 测试问题

| 错误代码 | 问题 | 预防措施 |
|---------|------|---------|
| `ERR_TEST_MISMATCH_001` | 测试与实现不匹配 | 先读实现 |

### 导入路径问题

| 错误代码 | 问题 | 预防措施 |
|---------|------|---------|
| `ERR_IMPORT_PATH_MISMATCH_001` | 导入路径与文件名不一致 | 确保路径正确 |

### 配置问题

| 错误代码 | 问题 | 预防措施 |
|---------|------|---------|
| `ERR_LINTER_EXPORT_MISSING_001` | Linter自动修改导致导出缺失 | 更新__init__.py |

---

## 📂 相关文档

**项目内部**:
- BUG报告模板: `docs/standards/bug-report-template.json`
- 经验教训索引: `docs/guides/BUG_LESSONS_LEARNED.md`
- BUG报告目录: `docs/quality/bugs/`
- 项目开发指南: `CLAUDE.md` - BUG登记章节

**外部参考**:
- BUGer模板: `/opt/iflow/buger/tools/maintenance/manual-bug-template.json`
- BUGer指南: `/opt/iflow/buger/tools/maintenance/MANUAL_BUG_REPORTING_GUIDE.md`

---

## 🤖 自动化功能（计划中）

### 待实现功能

1. ✅ Pre-commit hook: 检测commit message是否包含BUG修复
2. ⏳ 自动生成BUG报告: 从diff中提取BUG信息
3. ⏳ 自动更新索引: 提取关键信息更新经验教训文档
4. ⏳ 集成到CI/CD: 测试失败时自动登记BUG

### Hook触发机制

```bash
# 未来实现：git commit时自动触发
git commit -m "fix: 修复DDD模块导入路径错误"

# Hook将自动：
# 1. 检测到"fix:"前缀
# 2. 生成BUG报告
# 3. 保存到 docs/quality/bugs/
# 4. 更新经验教训索引
```

---

## 📊 统计信息

当前已记录的BUG：

- **总BUG数**: 6个
- **严重程度分布**:
  - 🔴 critical: 0个
  - 🟠 high: 2个
  - 🟡 medium: 3个
  - 🟢 low: 1个
- **类型分布**:
  - DDD架构: 2个
  - 数据类型: 1个
  - 测试: 1个
  - 导入路径: 1个
  - 配置: 1个

---

**文档维护**: 定期更新经验教训索引，确保包含最新的BUG和预防措施
**问题反馈**: 发现新问题请按模板登记到`docs/quality/bugs/`目录
**最后更新**: 2026-01-08
