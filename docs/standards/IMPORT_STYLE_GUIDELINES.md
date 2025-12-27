# 导入规范指南 (Import Style Guidelines)

本文档定义了 MyStocks 项目的导入规范，确保代码的一致性和可维护性。

## 📋 导入原则

### 1. 导入顺序 (Import Order)

按照以下顺序组织导入语句：

1. **标准库导入** (Python 标准模块)
2. **第三方库导入** (外部依赖)
3. **本地应用导入** (项目内部模块)
4. **相对导入** (同包内的模块)

```python
# ✅ 正确的导入顺序

# 1. 标准库
import os
import sys
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# 2. 第三方库
import pandas as pd
import numpy as np
import pytest
from fastapi import APIRouter
import sqlalchemy as sa

# 3. 本地应用导入
from src.core import ConfigDrivenTableManager
from src.adapters.akshare_adapter import AkshareDataSource
from web.backend.app.api import routes

# 4. 相对导入 (仅在包内使用)
from .utils import helper_function
from ..models import BaseModel
```

### 2. 导入格式规范

#### 2.1 每行导入数

- **优先使用多行导入**：每个导入语句占一行
- **避免在一行中导入多个模块**

```python
# ✅ 推荐：每行一个导入
import os
import sys
import asyncio

# ❌ 避免：一行多个导入
import os, sys, asyncio
```

#### 2.2 分组导入

- **相关导入可以分组**：使用括号进行分组
- **按字母顺序排列**：便于查找和维护

```python
# ✅ 推荐：分组导入
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Union
)

from src.core import (
    ConfigDrivenTableManager,
    DataClassification,
    DatabaseTarget
)
```

### 3. 具体导入 vs 通配符导入

#### 3.1 禁止使用通配符导入

```python
# ❌ 严格禁止
from module import *
import *

# ✅ 推荐：明确导入
from module import specific_function, specific_class
import module
```

#### 3.2 优先使用具体导入

```python
# ✅ 推荐：导入具体需要的函数/类
from src.adapters.akshare_adapter import AkshareDataSource
from datetime import datetime, timedelta

# ✅ 可接受：导入整个模块（使用时模块名前缀）
import numpy as np
import pandas as pd
```

### 4. 导入别名规范

#### 4.1 标准别名

使用广泛接受的标准别名：

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlalchemy as sa
import requests
```

#### 4.2 自定义别名

```python
# ✅ 推荐：有意义的别名
from src.core.unified_manager import MyStocksUnifiedManager as UnifiedManager
from web.backend.app.api.technical.routes import technical_router

# ❌ 避免：无意义的别名
from src.core.unified_manager import MyStocksUnifiedManager as mgr
```

### 5. 条件导入和异常处理

#### 5.1 可选依赖的处理

```python
# ✅ 推荐：优雅处理可选依赖
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    plt = None

try:
    from src.gpu.core.hardware_abstraction import GPUResourceManager
    HAS_GPU = True
except ImportError:
    HAS_GPU = False
```

#### 5.2 版本兼容性处理

```python
# ✅ 推荐：处理版本差异
try:
    from typing import TypedDict  # Python 3.8+
except ImportError:
    from typing_extensions import TypedDict  # 兼容旧版本
```

### 6. 循环导入避免

#### 6.1 延迟导入

在函数或方法内部导入，避免模块间的循环依赖：

```python
# ✅ 推荐：延迟导入解决循环依赖
def some_function():
    from src.another_module import needed_function
    return needed_function()

class MyClass:
    def __init__(self):
        # 延迟导入
        from src.dependent_module import Dependency
        self.dependency = Dependency()
```

#### 6.2 接口抽象

使用接口或抽象基类避免循环导入：

```python
# ✅ 推荐：使用接口避免循环导入
from abc import ABC, abstractmethod
from typing import Protocol

class DataSourceProtocol(Protocol):
    def get_data(self) -> Dict[str, Any]: ...
```

### 7. 项目特定的导入模式

#### 7.1 数据库访问层

```python
# ✅ 推荐：数据库相关导入
from src.data_access import (
    TDengineDataAccess,
    PostgreSQLDataAccess
)
from src.storage.database import (
    DatabaseTableManager,
    DatabaseConnectionManager
)
```

#### 7.2 适配器模式

```python
# ✅ 推荐：适配器导入
from src.adapters.akshare_adapter import AkshareDataSource
from src.adapters.tdx_adapter import TdxDataSource
from src.interfaces import IDataSource
```

#### 7.3 配置模块

```python
# ✅ 推荐：配置导入
from src.core.config_loader import ConfigLoader
from src.core.data_storage_strategy import DataStorageStrategy
```

### 8. 导入优化建议

#### 8.1 减少导入开销

```python
# ✅ 推荐：延迟导入重型模块
def generate_report():
    import matplotlib.pyplot as plt  # 仅在需要时导入
    # ... 使用 plt 生成报告
```

#### 8.2 导入工具函数

```python
# ✅ 推荐：创建工具模块集中导入
# src/utils/imports.py
from .database import get_db_session
from .config import get_setting
from .logging import get_logger

# 使用时
from src.utils.imports import get_db_session, get_setting, get_logger
```

### 9. 代码审查检查点

在代码审查时检查以下导入相关问题：

- [ ] 导入顺序是否正确
- [ ] 是否使用了通配符导入 (`from module import *`)
- [ ] 是否有未使用的导入
- [ ] 是否存在循环导入
- [ ] 导入别名是否合理
- [ ] 可选依赖是否有适当的异常处理
- [ ] 是否符合项目特定的导入模式

### 10. 工具和自动化

#### 10.1 代码格式化工具

```bash
# 使用 isort 自动排序导入
pip install isort
isort src/ --profile black

# 结合 black 使用
black src/
isort src/
```

#### 10.2 Linting 配置

在 `pyproject.toml` 中配置：

```toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["src", "web"]
known_third_party = ["fastapi", "pydantic", "pandas", "numpy"]

[tool.pylint.messages_control]
disable = [
    "unused-import",  # 由其他工具处理
]
```

### 11. 常见问题和解决方案

#### 11.1 未使用的导入

```bash
# 使用 autoflake 自动移除未使用的导入
pip install autoflake
autoflake --remove-unused-variables --remove-all-unused-imports --recursive src/
```

#### 11.2 导入冲突

```python
# ✅ 推荐：使用别名解决导入冲突
from src.core.config import Config as CoreConfig
from web.config import Config as WebConfig

# 或者使用模块前缀
import src.core.config as core_config
import web.config as web_config
```

#### 11.3 性能考虑

- **避免在循环中导入**：将导入语句放在模块顶部
- **合理使用延迟导入**：仅在真正需要时导入重型模块
- **批量导入**：相关功能一起导入，减少导入语句数量

## 📝 总结

遵循这些导入规范将：

1. **提高代码可读性**：清晰的导入结构让代码更容易理解
2. **增强可维护性**：一致的导入模式减少维护成本
3. **避免常见问题**：防止循环导入和命名冲突
4. **支持工具自动化**：便于使用代码格式化和检查工具
5. **提升开发效率**：标准化的导入模式减少认知负担

所有新代码都应遵循这些规范，现有代码在重构时也应逐步符合这些标准。
