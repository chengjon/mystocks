# 目录重组计划 - Week 1 Day 4-5

**日期**: 2025-10-19
**目标**: 按照3层目录结构重组项目代码
**原则**: 单一职责、命名清晰、结构稳定

---

## 📋 重组原则

### 3层目录结构

```
Layer 1: 项目整体（顶层分类）
    ↓
Layer 2: 功能拆分（按职责划分）
    ↓
Layer 3: 文件类型（具体实现）
```

### 设计原则

1. **单一职责**: 每个目录只负责一类功能
2. **命名清晰**: 目录名直接反映内容
3. **结构稳定**: 3层结构，不过度嵌套
4. **向后兼容**: 保留关键导入路径

---

## 🎯 目标结构

### 方案：保守渐进式重组

考虑到项目已经在运行，采用**保守方案**：
- 保留现有可用的结构
- 只整合明显重复的目录
- 重点清理根目录的混乱

```
mystocks_spec/                    # 项目根目录
│
├── src/                          # Layer 1: 源代码（新增）
│   ├── core/                     # Layer 2: 核心业务逻辑
│   │   ├── models/               # Layer 3: 数据模型
│   │   ├── services/             # Layer 3: 业务服务
│   │   └── classification.py    # 数据分类逻辑
│   │
│   ├── adapters/                 # Layer 2: 数据源适配器
│   │   ├── akshare/             # Layer 3: AKShare适配器
│   │   ├── baostock/            # Layer 3: Baostock适配器
│   │   ├── tdx/                 # Layer 3: 通达信适配器
│   │   └── base.py              # 基础接口
│   │
│   ├── storage/                  # Layer 2: 数据存储
│   │   ├── database/            # Layer 3: 数据库管理
│   │   ├── models/              # Layer 3: ORM模型
│   │   └── access/              # Layer 3: 数据访问层
│   │
│   ├── monitoring/               # Layer 2: 监控
│   │   ├── performance/         # Layer 3: 性能监控
│   │   ├── quality/             # Layer 3: 数据质量
│   │   └── alerts/              # Layer 3: 告警
│   │
│   └── utils/                    # Layer 2: 工具函数
│       ├── date_utils.py
│       ├── symbol_utils.py
│       └── validators.py
│
├── web/                          # Layer 1: Web应用（保持独立）
│   ├── backend/                 # FastAPI后端
│   └── frontend/                # Vue前端
│
├── ml_strategy/                  # Layer 1: 机器学习和策略（保持独立）
│   ├── backtest/                # 回测引擎
│   ├── indicators/              # 技术指标
│   ├── strategy/                # 交易策略
│   └── automation/              # 自动化交易
│
├── tests/                        # Layer 1: 测试（保持独立）
├── docs/                         # Layer 1: 文档（保持独立）
├── scripts/                      # Layer 1: 脚本工具（保持独立）
├── config/                       # Layer 1: 配置（保持独立）
├── logs/                         # Layer 1: 日志（保持独立）
│
├── main.py                       # 主入口
├── unified_manager.py            # 统一管理器（向后兼容）
└── table_config.yaml             # 表配置
```

---

## 📊 当前状态分析

### 当前目录结构（30+个目录）

| 目录 | 当前状态 | 重组决策 |
|------|---------|---------|
| **核心模块** | | |
| core/ | 空目录? | → src/core/ |
| data_access/ | 数据访问层 | → src/storage/access/ |
| unified_manager.py | 根目录文件 | 保留（兼容）+ 复制到src/ |
| core.py | 根目录文件 | → src/core/classification.py |
| data_access.py | 根目录文件 | → src/storage/access/data_access.py |
| monitoring.py | 根目录文件 | → src/monitoring/监控服务 |
| **适配器** | | |
| adapters/ | 数据源适配器 | → src/adapters/ |
| factory/ | 工厂模式 | 合并到src/adapters/base.py |
| interfaces/ | 接口定义 | 合并到src/adapters/base.py |
| data_sources/ | 数据源 | 合并到src/adapters/ |
| **存储层** | | |
| db_manager/ | 数据库管理 | → src/storage/database/ |
| models/ | 数据模型 | → src/storage/models/ |
| data/ | 数据目录 | 保留在根目录 |
| **监控** | | |
| monitoring/ | 监控模块 | → src/monitoring/ |
| **工具** | | |
| utils/ | 工具函数 | → src/utils/ |
| **业务模块（独立）** | | |
| ml_strategy/ | ML和策略 | 保留独立 |
| backtest/ | 回测 | → ml_strategy/backtest/ |
| strategy/ | 策略 | → ml_strategy/strategy/ |
| indicators/ | 指标 | → ml_strategy/indicators/ |
| automation/ | 自动化 | → ml_strategy/automation/ |
| realtime/ | 实时交易 | → ml_strategy/realtime/ |
| **Web应用** | | |
| web/ | Web应用 | 保留独立 |
| visualization/ | 可视化 | → web/或删除 |
| reporting/ | 报告 | → web/或ml_strategy/ |
| **其他** | | |
| tests/ | 测试 | 保留独立 |
| docs/ | 文档 | 保留独立 |
| scripts/ | 脚本 | 保留独立 |
| config/ | 配置 | 保留独立 |
| examples/ | 示例 | 保留或删除 |
| specs/ | 规格文档 | 保留独立 |
| inside/ | ? | 评估后决定 |
| manager/ | 管理器 | 合并到src/core/ |
| logs/ | 日志 | 保留独立 |

---

## 🚀 执行计划

### Phase 1: 创建新目录结构（10分钟）

```bash
# 创建src/主目录结构
mkdir -p src/core/{models,services}
mkdir -p src/adapters/{akshare,baostock,tdx}
mkdir -p src/storage/{database,models,access}
mkdir -p src/monitoring/{performance,quality,alerts}
mkdir -p src/utils

# 创建__init__.py
touch src/__init__.py
touch src/core/__init__.py
touch src/adapters/__init__.py
touch src/storage/__init__.py
touch src/monitoring/__init__.py
touch src/utils/__init__.py
```

### Phase 2: 整合ml_strategy目录（15分钟）

```bash
# 移动业务模块到ml_strategy
mv backtest ml_strategy/ 2>/dev/null || echo "backtest already in ml_strategy"
mv strategy ml_strategy/ 2>/dev/null || echo "strategy already in ml_strategy"
mv indicators ml_strategy/ 2>/dev/null || echo "indicators already in ml_strategy"
mv automation ml_strategy/ 2>/dev/null || echo "automation already in ml_strategy"
mv realtime ml_strategy/ 2>/dev/null || echo "realtime already in ml_strategy"

# 创建__init__.py
touch ml_strategy/__init__.py
```

### Phase 3: 迁移核心文件到src/（30分钟）

```bash
# 复制（不删除原文件，保持向后兼容）
cp core.py src/core/classification.py
cp data_access.py src/storage/access/data_access.py
cp monitoring.py src/monitoring/monitoring_service.py

# 迁移目录
cp -r adapters/* src/adapters/ 2>/dev/null
cp -r db_manager/* src/storage/database/ 2>/dev/null
cp -r utils/* src/utils/ 2>/dev/null

# 创建适配器基类
cat > src/adapters/base.py << 'EOF'
"""
数据源适配器基类
整合了interfaces/和factory/的功能
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import pandas as pd

class IDataSource(ABC):
    """数据源接口基类"""

    @abstractmethod
    def get_daily_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取日线数据"""
        pass

    @abstractmethod
    def get_realtime_quotes(self, symbols: list) -> pd.DataFrame:
        """获取实时行情"""
        pass

class DataSourceFactory:
    """数据源工厂"""
    _sources = {}

    @classmethod
    def register(cls, name: str, source_class):
        """注册数据源"""
        cls._sources[name] = source_class

    @classmethod
    def create(cls, name: str, **kwargs):
        """创建数据源实例"""
        if name not in cls._sources:
            raise ValueError(f"Unknown data source: {name}")
        return cls._sources[name](**kwargs)
EOF
```

### Phase 4: 清理重复目录（20分钟）

```bash
# 备份需要评估的目录
mkdir -p temp_backup/evaluation
mv manager temp_backup/evaluation/ 2>/dev/null
mv factory temp_backup/evaluation/ 2>/dev/null
mv interfaces temp_backup/evaluation/ 2>/dev/null
mv data_sources temp_backup/evaluation/ 2>/dev/null
mv data_access temp_backup/evaluation/ 2>/dev/null
mv visualization temp_backup/evaluation/ 2>/dev/null
mv reporting temp_backup/evaluation/ 2>/dev/null
mv inside temp_backup/evaluation/ 2>/dev/null

# 如果确认无用，后续可删除
```

### Phase 5: 更新导入路径（需手动）

创建兼容层，在根目录保留关键文件的符号引用：

```python
# 在根目录创建 compat.py
"""
向后兼容层
保持旧的导入路径可用
"""
import sys
from pathlib import Path

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# 重新导出关键类
from src.core.classification import DataClassification, DataStorageStrategy
from src.storage.access.data_access import *
from src.monitoring.monitoring_service import *

__all__ = [
    'DataClassification',
    'DataStorageStrategy',
    # ... 其他导出
]
```

### Phase 6: 验证和测试（30分钟）

```bash
# 检查新结构
tree src/ -L 3

# 运行测试
python -m pytest tests/ -v

# 测试主要功能
python main.py

# 检查导入
python -c "from src.core.classification import DataClassification; print('OK')"
```

---

## ⚠️ 风险和缓解

### 风险1: 导入路径破坏
**概率**: 高
**影响**: 中
**缓解**:
- 保留根目录的原始文件（复制而非移动）
- 创建兼容层
- 逐步迁移导入

### 风险2: 测试失败
**概率**: 中
**影响**: 高
**缓解**:
- 在迁移前运行完整测试套件
- 逐步迁移，每步验证
- Git备份随时可回滚

### 风险3: Web应用依赖破坏
**概率**: 低
**影响**: 中
**缓解**:
- Web目录保持独立，不重组
- 只更新Web对核心模块的引用

---

## 📈 预期成果

### 目录数量

| 指标 | 当前 | 重组后 | 改善 |
|------|------|--------|------|
| 顶层目录 | 30+ | 10-12 | -60% |
| 总目录深度 | 不一致 | 3层稳定 | 标准化 |
| 根目录.py文件 | 20+ | 2-3 | -85% |

### 代码组织

- ✅ 核心业务逻辑集中在src/core/
- ✅ 数据访问统一在src/storage/
- ✅ 适配器清晰分类在src/adapters/
- ✅ ML和策略独立在ml_strategy/
- ✅ Web应用独立在web/

### 可维护性

- ✅ 新开发者能快速理解目录结构
- ✅ 明确的职责划分
- ✅ 减少目录混乱和重复

---

## 🎯 决策点

### 应该做

1. ✅ 创建清晰的src/目录结构
2. ✅ 整合重复的适配器相关目录
3. ✅ 将业务模块集中到ml_strategy/
4. ✅ 保持向后兼容

### 可选

1. ⚠️ 迁移visualization到web/
2. ⚠️ 删除examples/（如果过时）
3. ⚠️ 合并manager/到src/core/

### 不应该做

1. ❌ 破坏性地移动文件（应复制）
2. ❌ 重组web/目录（独立应用）
3. ❌ 立即删除旧目录（先备份评估）
4. ❌ 修改所有导入路径（逐步进行）

---

## 📋 执行检查清单

### Day 4 (今天)
- [ ] 创建src/目录结构
- [ ] 复制核心文件到src/
- [ ] 整合ml_strategy/目录
- [ ] 创建适配器基类
- [ ] 测试新导入路径

### Day 5 (明天)
- [ ] 移动重复目录到temp_backup/
- [ ] 创建向后兼容层
- [ ] 更新关键导入路径
- [ ] 运行完整测试套件
- [ ] 验证Web应用正常

---

## 🔄 回滚计划

如遇问题:

```bash
# 方案1: 删除新创建的src/
rm -rf src/

# 方案2: 恢复备份目录
mv temp_backup/evaluation/* .

# 方案3: Git回滚
git reset --hard backup-before-refactor-2025-10-19
```

---

## 📝 注意事项

1. **保守原则**: 宁可多保留，不轻易删除
2. **兼容优先**: 保持向后兼容比完美结构更重要
3. **渐进迁移**: 不要一次性改完所有导入
4. **测试驱动**: 每步都要验证功能正常
5. **文档同步**: 更新CLAUDE.md和README.md

---

**制定日期**: 2025-10-19
**预计执行时间**: 2天
**风险等级**: 🟡 中等（有缓解措施）
**是否需要用户确认**: ✅ 是

---

*下一步: 等待用户确认后开始执行*
