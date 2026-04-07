# src/ 目录说明

> **参考指南说明**:
> 本文件用于说明 `src/` 目录下局部模块的使用方式、结构背景、调试方法、部署提示或技术参考，帮助理解具体实现。
> 其中的路径、步骤、指标和示例应先与 `architecture/STANDARDS.md`、当前代码实现及最新验证结果核对；若涉及仓库执行流程、命令或协作约束，再补充参考根目录 `AGENTS.md`。本文件不得单独视为共享规则或当前状态的唯一事实来源。


**创建日期**: 2025-10-19
**目的**: 3层目录结构的核心代码组织

---

## 📁 目录结构

```
src/
├── core/                    # 核心业务逻辑
│   ├── models/             # 数据模型
│   ├── services/           # 业务服务
│   ├── classification_root.py     # 数据分类（从根目录复制）
│   ├── unified_manager.py         # 统一管理器（从根目录复制）
│   ├── data_classification.py     # 数据分类枚举
│   ├── data_storage_strategy.py   # 存储策略
│   ├── config_driven_table_manager.py  # 配置驱动表管理
│   └── batch_failure_strategy.py  # 批处理失败策略
│
├── adapters/                # 数据源适配器
│   ├── akshare/            # AKShare适配器（子目录）
│   ├── baostock/           # Baostock适配器（子目录）
│   ├── tdx/                # 通达信适配器（子目录）
│   ├── akshare_adapter.py
│   ├── baostock_adapter.py
│   ├── tdx_adapter.py
│   ├── financial_adapter.py
│   └── ... （其他适配器）
│
├── storage/                 # 数据存储层
│   ├── database/           # 数据库管理
│   │   ├── database_manager.py
│   │   ├── database_test_menu.py
│   │   └── ... （21个文件）
│   ├── models/             # ORM模型
│   │   └── （数据模型）
│   └── access/             # 数据访问层
│       └── data_access.py
│
├── monitoring/              # 监控系统
│   ├── performance/        # 性能监控（子目录）
│   ├── quality/            # 数据质量（子目录）
│   ├── alerts/             # 告警系统（子目录）
│   ├── monitoring_service.py     # 监控服务（从根目录复制）
│   ├── alert_manager.py
│   ├── data_quality_monitor.py
│   ├── monitoring_database.py
│   ├── performance_monitor.py
│   └── 生成监控数据说明.md
│
└── utils/                   # 工具函数
    ├── column_mapper.py
    ├── date_utils.py
    ├── symbol_utils.py
    ├── add_doc_metadata.py
    ├── add_python_headers.py
    ├── check_api_health.py
    ├── check_db_health.py
    └── ... （14个文件）
```

---

## 🎯 设计原则

### 3层结构

1. **Layer 1 (src/)**: 项目整体代码组织
2. **Layer 2 (core/, adapters/, storage/, etc.)**: 按功能职责划分
3. **Layer 3 (models/, services/, etc.)**: 按文件类型划分

### 单一职责

- `core/`: 核心业务逻辑和数据分类
- `adapters/`: 外部数据源接入
- `storage/`: 数据持久化
- `monitoring/`: 系统监控
- `utils/`: 通用工具函数

### 命名清晰

- 目录名直接反映功能
- 避免缩写和模糊命名
- 保持一致的命名风格

---

## 📊 文件统计

| 目录 | 文件数 | 说明 |
|------|--------|------|
| core/ | 8 | 核心业务逻辑 |
| adapters/ | 14 | 数据源适配器 |
| storage/database/ | 21 | 数据库管理 |
| storage/models/ | 待定 | 数据模型 |
| storage/access/ | 1 | 数据访问层 |
| monitoring/ | 6 | 监控系统 |
| utils/ | 14 | 工具函数 |
| **总计** | **64+** | **所有文件** |

---

## 🔗 与原有结构的关系

### 向后兼容

根目录保留了关键文件以保持向后兼容：
- `core.py` → 保留 + 复制到 `src/core/classification_root.py`
- `data_access.py` → 保留 + 复制到 `src/storage/access/`
- `monitoring.py` → 保留 + 复制到 `src/monitoring/`
- `unified_manager.py` → 保留 + 复制到 `src/core/`

### 原有目录映射

| 原有目录 | 新位置 | 状态 |
|---------|--------|------|
| core/ | src/core/ | 复制 |
| adapters/ | src/adapters/ | 复制 |
| db_manager/ | src/storage/database/ | 复制 |
| models/ | src/storage/models/ | 复制 |
| monitoring/ | src/monitoring/ | 复制 |
| utils/ | src/utils/ | 复制 |

**注意**: 原有目录保持不变，src/是新组织的代码

---

## 🚀 使用方式

### 导入示例

```python
# 从新结构导入
from src.core.data_classification import DataClassification
from src.adapters.akshare_adapter import AkshareDataSource
from src.storage.database.database_manager import DatabaseTableManager
from src.monitoring.monitoring_service import MonitoringDatabase
from src.utils.date_utils import get_trade_dates

# 向后兼容 - 旧的导入方式仍然有效
from core.data_classification import DataClassification
from adapters.akshare_adapter import AkshareDataSource
```

### 添加新模块

1. 确定模块职责（核心/适配器/存储/监控/工具）
2. 放入对应的Layer 2目录
3. 如需细分，创建Layer 3子目录
4. 更新`__init__.py`导出

---

## ⚠️ 注意事项

1. **不要删除原有目录**: src/是新组织，原有结构保留以保证兼容性
2. **渐进式迁移**: 新代码优先使用src/结构，旧代码逐步迁移
3. **测试充分**: 任何导入路径更改都需要充分测试
4. **文档同步**: 更新CLAUDE.md中的架构说明

---

## 📝 TODO

- [ ] 创建adapter基类 (`src/adapters/base.py`)
- [ ] 完善storage/models/目录
- [ ] 整合factory/和interfaces/到adapters/
- [ ] 更新主入口导入路径
- [ ] 运行完整测试套件
- [ ] 更新CLAUDE.md文档

---

**维护者**: MyStocks重构团队
**最后更新**: 2025-10-19
