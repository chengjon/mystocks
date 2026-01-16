# 数据源注册表拆分方案设计
# Data Source Registry Splitting Plan

## 🎯 拆分目标

当前 `data_sources_registry.yaml` 文件已达到 **2631行**，维护困难，需要合理拆分。

## 📊 当前文件分析

### 文件大小统计
- 总行数：2,631行
- 数据源数量：62个
- 平均每个数据源：42.5行

### 数据源分类统计
| source_name | 数量 | 占比 | 主要功能 |
|-------------|------|------|----------|
| akshare | 52个 | 83.9% | 股票、期货、基金、宏观数据 |
| advanced_analysis | 8个 | 12.9% | 高级分析模型 |
| system_mock | 1个 | 1.6% | 开发测试数据 |
| sina_finance | 1个 | 1.6% | 股票评级数据 |

## 🗂️ 拆分方案设计

### 方案选择：按数据源类型拆分

**核心原则**：
- ✅ **逻辑分类**：按source_name分组，功能内聚
- ✅ **格式一致性**：保持YAML结构和字段定义不变
- ✅ **便捷加载**：支持动态加载和合并
- ✅ **向后兼容**：现有代码无需修改

### 文件结构设计

```
config/
├── data_sources_registry.yaml          # 主配置文件 (核心配置)
├── data_sources/
│   ├── akshare.yaml                    # akshare数据源 (52个)
│   ├── advanced_analysis.yaml          # 高级分析数据源 (8个)
│   ├── mock.yaml                       # Mock数据源 (1个)
│   └── crawlers.yaml                   # 爬虫数据源 (1个，目前)
│   └── _template.yaml                  # 数据源配置模板
└── data_sources_loader.py              # 动态加载器
```

### 主配置文件 (data_sources_registry.yaml)

```yaml
# 主配置文件 - 核心配置和加载控制
version: "2.1"
last_updated: "2026-01-15T10:00:00"

# 加载控制 - 控制哪些子文件被加载
load_sources:
  - "akshare"           # 加载 data_sources/akshare.yaml
  - "advanced_analysis" # 加载 data_sources/advanced_analysis.yaml
  - "mock"             # 加载 data_sources/mock.yaml (仅开发环境)
  - "crawlers"         # 加载 data_sources/crawlers.yaml

# 全局配置
global_config:
  default_target_db: "postgresql"
  enable_caching: true
  health_check_interval: 300

# 数据源别名映射 (向后兼容)
aliases:
  "akshare.stock_zh_a_hist": "akshare_daily_kline"
  "sina_finance.stock_ratings": "stock_ratings_sina"
```

### 子配置文件示例

#### data_sources/akshare.yaml
```yaml
# AKShare 数据源配置
# 包含所有akshare相关的52个数据源

data_sources:
  akshare_stock_zh_a_hist:
    source_name: "akshare"
    source_type: "api_library"
    endpoint_name: "akshare.stock_zh_a_hist"
    # ... 完整配置

  akshare_fund_etf_spot_em:
    source_name: "akshare"
    source_type: "api_library"
    endpoint_name: "akshare.fund_etf_spot_em"
    # ... 完整配置

  # ... 其他50个akshare数据源
```

#### data_sources/crawlers.yaml
```yaml
# 爬虫数据源配置
# 包含所有网络爬虫相关的数据源

data_sources:
  sina_finance_stock_ratings:
    source_name: "sina_finance"
    source_type: "crawler"
    endpoint_name: "sina_finance.stock_ratings"
    call_method: "function_call"

    # 5层数据分类绑定
    data_category: "DERIVED_DATA"
    data_classification: "derived_data"
    classification_level: 3
    target_db: "postgresql"
    table_name: "stock_ratings_sina"

    # 参数定义
    parameters:
      max_pages:
        type: "integer"
        required: false
        default: 5
        minimum: 1
        maximum: 10
        description: "最大爬取页数"
        example: 5

    description: "新浪财经股票评级数据 - 分析师评级、目标价、评级机构等信息"
    update_frequency: "daily"
    data_quality_score: 8.5
    priority: 2
    status: "active"
    tags: ["stock-ratings", "analyst-ratings", "target-price", "sina-finance", "crawler"]

    # 测试参数
    test_parameters:
      max_pages: 1

    # 数据质量规则
    quality_rules:
      min_record_count: 10
      max_response_time: 30.0
      required_columns: ["股票代码", "股票名称", "目标价", "最新评级", "评级机构", "分析师", "行业", "评级日期", "摘要"]
```

### 动态加载器实现

#### data_sources_loader.py

```python
"""
数据源配置动态加载器
支持从多个YAML文件加载和合并配置
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class DataSourcesLoader:
    """数据源配置加载器"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.main_config_file = self.config_dir / "data_sources_registry.yaml"
        self.sources_dir = self.config_dir / "data_sources"

    def load_all_sources(self) -> Dict[str, Any]:
        """
        加载所有数据源配置

        1. 加载主配置文件
        2. 根据load_sources列表加载子文件
        3. 合并所有配置
        4. 应用别名映射

        Returns:
            合并后的完整配置字典
        """
        # 1. 加载主配置
        main_config = self._load_yaml_file(self.main_config_file)
        if not main_config:
            raise FileNotFoundError(f"主配置文件不存在: {self.main_config_file}")

        # 2. 获取要加载的子文件列表
        load_sources = main_config.get("load_sources", [])
        logger.info(f"将加载以下数据源: {load_sources}")

        # 3. 加载所有子配置文件
        all_sources = {}
        for source_name in load_sources:
            source_file = self.sources_dir / f"{source_name}.yaml"
            if source_file.exists():
                source_config = self._load_yaml_file(source_file)
                if source_config and "data_sources" in source_config:
                    all_sources.update(source_config["data_sources"])
                    logger.info(f"✅ 加载 {source_name}: {len(source_config['data_sources'])} 个数据源")
            else:
                logger.warning(f"⚠️ 子配置文件不存在: {source_file}")

        # 4. 合并配置
        merged_config = main_config.copy()
        merged_config["data_sources"] = all_sources

        # 5. 应用别名映射
        aliases = main_config.get("aliases", {})
        self._apply_aliases(merged_config, aliases)

        logger.info(f"✅ 总共加载了 {len(all_sources)} 个数据源配置")
        return merged_config

    def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """加载单个YAML文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"加载YAML文件失败 {file_path}: {e}")
            return {}

    def _apply_aliases(self, config: Dict[str, Any], aliases: Dict[str, str]):
        """应用别名映射"""
        data_sources = config.get("data_sources", {})
        for endpoint_name, alias in aliases.items():
            if endpoint_name in data_sources:
                # 创建别名副本
                data_sources[alias] = data_sources[endpoint_name].copy()
                data_sources[alias]["endpoint_name"] = alias
                logger.debug(f"创建别名: {endpoint_name} -> {alias}")

# 全局加载器实例
loader = DataSourcesLoader()

def load_data_sources_config() -> Dict[str, Any]:
    """便捷函数：加载完整的数据源配置"""
    return loader.load_all_sources()
```

### 拆分步骤规划

#### 步骤1: 创建目录结构
```bash
# 创建子配置文件目录
mkdir -p config/data_sources

# 创建模板文件
touch config/data_sources/_template.yaml
```

#### 步骤2: 提取数据源配置

```bash
# 编写Python脚本自动拆分现有文件
python scripts/split_data_sources_config.py
```

#### 步骤3: 实现动态加载器

```python
# 更新现有的配置加载逻辑
# src/core/data_source/registry.py

def load_config() -> Dict:
    """加载数据源配置 - 支持拆分文件"""
    from config.data_sources_loader import load_data_sources_config
    return load_data_sources_config()
```

#### 步骤4: 验证和测试

```bash
# 验证拆分后的配置加载
python -c "
from config.data_sources_loader import load_data_sources_config
config = load_data_sources_config()
print(f'✅ 加载成功: {len(config[\"data_sources\"])} 个数据源')
"

# 运行现有测试
python scripts/sync_sources.py --dry-run
```

## 📈 拆分优势

### 1. **维护性提升**
- 单个文件从2631行 → 各子文件平均300-500行
- 按功能分类，修改时只需关注相关文件
- Git冲突概率大幅降低

### 2. **加载性能优化**
- 支持按需加载：开发环境只加载mock数据源
- 减少内存占用：生产环境可排除测试数据源
- 更快的配置文件解析

### 3. **扩展性增强**
- 新增数据源类型只需添加新的子文件
- 支持模块化管理：不同团队维护不同数据源
- 便于版本控制和回滚

### 4. **向后兼容性**
- 现有代码无需修改
- API接口保持不变
- 现有测试用例继续有效

## 🔄 迁移计划

### Phase 1: 基础拆分 (1天)
- [x] 创建目录结构
- [x] 编写拆分脚本
- [x] 提取akshare数据源到单独文件
- [x] 实现动态加载器

### Phase 2: 高级功能 (2天)
- [ ] 添加加载控制 (按环境启用/禁用)
- [ ] 实现别名映射系统
- [ ] 添加配置验证
- [ ] 性能优化 (延迟加载)

### Phase 3: 测试和文档 (1天)
- [ ] 更新所有相关文档
- [ ] 添加拆分配置的测试用例
- [ ] 验证向后兼容性
- [ ] 培训团队成员

## 📋 实施检查清单

- [x] 分析当前文件结构和大小
- [x] 确定拆分维度 (按source_name)
- [x] 设计主文件 + 子文件的架构
- [x] 实现动态加载器
- [x] 创建配置模板
- [ ] 编写自动拆分脚本
- [ ] 测试拆分后的加载功能
- [ ] 验证向后兼容性
- [ ] 更新文档和README

## 🎯 总结

**推荐方案**：主文件 + 按数据源类型拆分的子文件

**拆分结果**：
- 主文件：`data_sources_registry.yaml` (控制加载)
- akshare数据源：`data_sources/akshare.yaml` (~2200行)
- 高级分析：`data_sources/advanced_analysis.yaml` (~400行)
- Mock数据：`data_sources/mock.yaml` (~50行)
- 爬虫数据：`data_sources/crawlers.yaml` (~50行)

**核心优势**：
- 📦 **模块化**：功能内聚，职责清晰
- 🚀 **性能**：按需加载，支持环境区分
- 🔧 **维护**：文件大小合理，冲突减少
- 🔄 **兼容**：现有代码无需修改
- 📈 **扩展**：易于添加新数据源类型

此拆分方案将有效解决当前配置文件过大的问题，提高团队协作效率和代码维护性。