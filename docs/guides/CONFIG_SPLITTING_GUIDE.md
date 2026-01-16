# MyStocks 配置拆分最佳实践

> **文档版本**: v1.0  
> **更新日期**: 2026-01-14  
> **适用范围**: 所有环境配置

---

## 📋 目录

1. [概述](#1-概述)
2. [配置分类](#2-配置分类)
3. [拆分原则](#3-拆分原则)
4. [配置结构](#4-配置结构)
5. [环境特定配置](#5-环境特定配置)
6. [敏感信息管理](#6-敏感信息管理)
7. [配置验证](#7-配置验证)
8. [最佳实践](#8-最佳实践)

---

## 1. 概述

### 1.1 为什么需要配置拆分

| 问题 | 影响 | 解决方案 |
|------|------|----------|
| 配置分散 | 难以维护、易出错 | 集中管理 |
| 环境混杂 | 开发/测试/生产配置混乱 | 环境隔离 |
| 敏感信息泄露 | 安全风险 | 加密存储 |
| 硬编码值 | 修改需要改代码 | 配置外部化 |

### 1.2 配置管理目标

- ✅ **集中化**: 所有配置在统一位置管理
- ✅ **环境隔离**: 开发、测试、生产环境分离
- ✅ **安全性**: 敏感信息加密存储
- ✅ **可追溯**: 配置变更有记录可查
- ✅ **自动化**: 配置随环境自动加载

---

## 2. 配置分类

### 2.1 按用途分类

| 类别 | 说明 | 示例 |
|------|------|------|
| **数据库配置** | 数据库连接信息 | PostgreSQL、TDengine |
| **缓存配置** | 缓存服务器连接 | Redis 缓存 |
| **API 配置** | 外部服务凭证 | 数据源 API Key |
| **应用配置** | 应用运行时参数 | 日志级别、超时时间 |
| **功能开关** | 功能启用/禁用 | Feature Flags |
| **业务配置** | 业务规则参数 | 风险阈值、限流规则 |

### 2.2 按环境分类

| 环境 | 用途 | 配置特点 |
|------|------|----------|
| **development** | 本地开发 | 详细日志、宽松验证 |
| **testing** | 自动化测试 | 固定数据、快速执行 |
| **staging** | 预发布验证 | 生产配置副本 |
| **production** | 生产运行 | 严格安全、性能优化 |

### 2.3 按敏感度分类

| 敏感度 | 说明 | 示例 |
|--------|------|------|
| **公开** | 可公开的信息 | 应用名称、版本 |
| **内部** | 不应公开的信息 | 功能开关、日志级别 |
| **机密** | 敏感商业信息 | API Key、数据库密码 |
| **绝密** | 关键安全信息 | JWT Secret、加密密钥 |

---

## 3. 拆分原则

### 3.1 单一职责原则

```
❌ 错误：一个 config.yaml 包含所有配置
config/
└── config.yaml  # 2000+ 行，包含所有配置

✅ 正确：按功能拆分
config/
├── database/
│   ├── postgresql.yaml
│   └── tdengine.yaml
├── cache/
│   └── redis.yaml
├── api/
│   ├── akshare.yaml
│   └── tdx.yaml
└── app/
    ├── logging.yaml
    └── features.yaml
```

### 3.2 层次结构原则

```
config/
├── base/                    # 基础配置（所有环境通用）
│   ├── database.yaml
│   ├── logging.yaml
│   └── features.yaml
├── environments/            # 环境特定配置
│   ├── development.yaml
│   ├── testing.yaml
│   ├── staging.yaml
│   └── production.yaml
└── secrets/                 # 敏感信息（加密）
    ├── database.yaml.enc
    └── api.yaml.enc
```

### 3.3 配置继承原则

```
开发环境配置 = 基础配置 + 开发特定配置 + 开发密码
测试环境配置 = 基础配置 + 测试特定配置 + 测试密码
```

---

## 4. 配置结构

### 4.1 主配置文件结构

```yaml
# config/base/app.yaml
---
app:
  name: mystocks
  version: 3.0.0
  environment: ${APP_ENV:development}
  
logging:
  level: ${LOG_LEVEL:INFO}
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file:
    enabled: true
    path: ${LOG_PATH:logs/app.log}
    max_size: 100MB
    backup_count: 5

features:
  gpu_enabled: ${GPU_ENABLED:false}
  cache_enabled: ${CACHE_ENABLED:true}
  debug_mode: ${DEBUG_MODE:false}

rate_limiting:
  enabled: true
  requests_per_minute: 60
  burst_size: 10
```

### 4.2 数据库配置

```yaml
# config/base/database.yaml
---
postgresql:
  host: ${POSTGRESQL_HOST:192.168.123.104}
  port: ${POSTGRESQL_PORT:5438}
  database: ${POSTGRESQL_DATABASE:mystocks}
  username: ${POSTGRESQL_USER:postgres}
  password: ${POSTGRESQL_PASSWORD:}  # 从 secrets 读取
  pool:
    min_size: 5
    max_size: 20
    max_overflow: 10
    timeout: 30s

tdengine:
  host: ${TDENGINE_HOST:192.168.123.104}
  port: ${TDENGINE_PORT:6030}
  username: ${TDENGINE_USER:root}
  password: ${TDENGINE_PASSWORD:}  # 从 secrets 读取
  database: ${TDENGINE_DATABASE:market_data}
  pool:
    min_size: 2
    max_size: 10

redis:
  host: ${REDIS_HOST:192.168.123.104}
  port: ${REDIS_PORT:6379}
  password: ${REDIS_PASSWORD:}  # 从 secrets 读取
  db: ${REDIS_DB:0}
  key_prefix: ${REDIS_KEY_PREFIX:mystocks:}
  pool:
    max_connections: 50
```

### 4.3 数据源配置

```yaml
# config/base/data_sources.yaml
---
data_sources:
  akshare:
    enabled: true
    priority: 1
    rate_limit:
      requests_per_minute: 60
      burst: 10
    retry:
      max_attempts: 3
      delay: 1s
      backoff: 2

  baostock:
    enabled: true
    priority: 2
    rate_limit:
      requests_per_minute: 30
      burst: 5

  tdx:
    enabled: true
    priority: 0  # 最高优先级
    servers:
      - host: 192.168.123.104
        port: 7709
        timeout: 30s

  tushare:
    enabled: false  # 需要 API Key
    priority: 3
    token_env: TUSHARE_TOKEN
```

### 4.4 功能开关配置

```yaml
# config/base/features.yaml
---
features:
  # 核心功能
  trading_enabled: true
  backtest_enabled: true
  realtime_enabled: true
  
  # 高级功能
  gpu_acceleration: ${GPU_ENABLED:false}
  ml_strategies: false
  
  # 监控功能
  performance_monitoring: true
  alert_enabled: true
  
  # 实验功能
  experimental_charts: false
  new_indicators: false

feature_flags:
  use_v3_api: true
  use_caching_v2: false
  enable_websocket: true
```

---

## 5. 环境特定配置

### 5.1 开发环境

```yaml
# config/environments/development.yaml
---
app:
  debug: true
  environment: development

logging:
  level: DEBUG
  console:
    enabled: true
    format: colored

features:
  use_mock_data: true
  cache_enabled: false  # 开发时关闭缓存便于调试

data_sources:
  akshare:
    enabled: true
    mock: true  # 使用模拟数据

# 开发环境覆盖
postgresql:
  pool:
    min_size: 1
    max_size: 5
    timeout: 60s
```

### 5.2 测试环境

```yaml
# config/environments/testing.yaml
---
app:
  debug: false
  environment: testing
  test_mode: true

logging:
  level: WARNING
  file:
    enabled: false  # 测试时不生成日志文件

features:
  use_mock_data: true
  cache_enabled: true

# 测试数据库使用内存或临时数据库
postgresql:
  host: localhost
  port: 5433
  database: mystocks_test

# 测试数据源使用 mock
data_sources:
  all:
    mock: true
```

### 5.3 预发布环境

```yaml
# config/environments/staging.yaml
---
app:
  debug: false
  environment: staging

logging:
  level: INFO
  file:
    enabled: true
    path: /var/log/mystocks/staging/

features:
  use_mock_data: false
  cache_enabled: true

# 生产配置副本
postgresql:
  host: ${STAGING_PG_HOST}
  # 其他配置与生产相同

data_sources:
  akshare:
    enabled: true
    mock: false
```

### 5.4 生产环境

```yaml
# config/environments/production.yaml
---
app:
  debug: false
  environment: production
  environment_name: ${ENV_NAME:prod}

logging:
  level: WARNING
  format: json
  file:
    enabled: true
    path: /var/log/mystocks/prod/
    max_size: 500MB
    backup_count: 10
  sentry:
    enabled: true
    dsn: ${SENTRY_DSN}

features:
  use_mock_data: false
  cache_enabled: true
  rate_limiting:
    strict_mode: true

postgresql:
  pool:
    min_size: 10
    max_size: 50
    max_overflow: 20
    timeout: 15s
  ssl:
    enabled: true
    mode: require

tdengine:
  pool:
    min_size: 5
    max_size: 20
```

---

## 6. 敏感信息管理

### 6.1 敏感配置清单

| 配置项 | 敏感度 | 处理方式 |
|--------|--------|----------|
| 数据库密码 | 绝密 | 加密存储、环境变量 |
| API Token | 绝密 | 加密存储、环境变量 |
| JWT Secret | 绝密 | 加密存储、密钥管理服务 |
| 加密密钥 | 绝密 | 硬件安全模块 |
| 内部配置 | 机密 | 版本控制忽略 |

### 6.2 环境变量方式

```bash
# .env 文件（添加到 .gitignore）
# =====================
# 敏感配置 - 不要提交到版本控制
# =====================

# 数据库
POSTGRESQL_PASSWORD=your_secure_password
TDENGINE_PASSWORD=your_secure_password
REDIS_PASSWORD=your_secure_password

# API Keys
TUSHARE_TOKEN=your_api_token
DATA_SOURCE_API_KEY=your_api_key

# 安全
JWT_SECRET_KEY=your-jwt-secret-key-min-32-chars
ENCRYPTION_KEY=your-encryption-key

# 外部服务
SENTRY_DSN=https://xxx@sentry.io/xxx
```

### 6.3 加密配置方式

```python
# config/secrets_manager.py
import os
import yaml
from cryptography.fernet import Fernet

class SecretsManager:
    def __init__(self, key=None):
        self.key = key or os.getenv('CONFIG_ENCRYPTION_KEY')
        if not self.key:
            # 生成新密钥（首次运行时）
            self.key = Fernet.generate_key()
            print(f"⚠️ 新加密密钥已生成，请保存: {self.key.decode()}")
        self.fernet = Fernet(self.key)
    
    def encrypt(self, data: str) -> bytes:
        return self.fernet.encrypt(data.encode())
    
    def decrypt(self, data: bytes) -> str:
        return self.fernet.decrypt(data).decode()
    
    def load_secrets(self, file_path: str) -> dict:
        """加载并解密配置文件"""
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
        decrypted_data = self.fernet.decrypt(encrypted_data)
        return yaml.safe_load(decrypted_data)
```

### 6.4 配置模板

```yaml
# config/secrets/template.yaml.example
# 配置模板 - 敏感值用占位符表示
# 不要填写真实值，运行时从环境变量或加密存储读取
---
# =====================
# 敏感配置模板
# =====================
# 请勿填写真实值，使用环境变量或加密存储
# =====================

# 数据库密码
postgresql:
  password: ${POSTGRESQL_PASSWORD}  # 从环境变量读取

# API Token
data_sources:
  tushare:
    token: ${TUSHARE_TOKEN}  # 从环境变量读取

# 安全密钥
security:
  jwt_secret: ${JWT_SECRET_KEY}  # 从环境变量读取
  encryption_key: ${ENCRYPTION_KEY}  # 从环境变量读取
```

---

## 7. 配置验证

### 7.1 验证规则

```python
# config/validator.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from pathlib import Path

class DatabaseConfig(BaseModel):
    host: str = Field(..., min_length=1)
    port: int = Field(..., ge=1, le=65535)
    database: str = Field(..., min_length=1)
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    pool: dict = Field(default_factory=dict)
    
    @validator('password')
    def password_not_empty(cls, v):
        if not v:
            raise ValueError('密码不能为空')
        return v

class RedisConfig(BaseModel):
    host: str = Field(..., min_length=1)
    port: int = Field(..., ge=1, le=65535)
    password: Optional[str] = None
    key_prefix: str = Field(default="")

class AppConfig(BaseModel):
    app: dict
    postgresql: DatabaseConfig
    tdengine: DatabaseConfig
    redis: Optional[RedisConfig] = None
    features: dict = Field(default_factory=dict)
```

### 7.2 验证脚本

```bash
#!/bin/bash
# 配置文件验证脚本

echo "=== 配置文件验证 ==="

# 检查必需文件存在
for file in config/base/app.yaml \
           config/base/database.yaml \
           config/environments/${APP_ENV:-development}.yaml; do
    if [ -f "$file" ]; then
        echo "✅ $file 存在"
    else
        echo "❌ $file 不存在"
        exit 1
    fi
done

echo ""
echo "=== YAML 语法检查 ==="
for file in config/**/*.yaml; do
    python3 -c "import yaml; yaml.safe_load(open('$file'))"
    if [ $? -eq 0 ]; then
        echo "✅ $(basename $file) 语法正确"
    else
        echo "❌ $(basename $file) 语法错误"
        exit 1
    fi
done

echo ""
echo "=== 必需环境变量检查 ==="
for var in POSTGRESQL_HOST TDENGINE_HOST POSTGRESQL_DATABASE; do
    if [ -n "${!var}" ]; then
        echo "✅ $var 已设置"
    else
        echo "⚠️ $var 未设置"
    fi
done

echo ""
echo "=== 敏感配置检查 ==="
# 检查配置文件是否包含明文密码
if grep -r "password:.*[A-Za-z0-9]" config/base/*.yaml 2>/dev/null | grep -v "^#" | grep -v "\${" > /dev/null; then
    echo "⚠️ 发现可能明文密码，请使用环境变量"
    grep -r "password:" config/base/*.yaml | grep -v "^#" | grep -v "\${"
fi

echo ""
echo "=== 验证完成 ==="
```

### 7.3 CI/CD 验证

```yaml
# .github/workflows/config-validation.yml
name: Config Validation

on:
  push:
    paths:
      - 'config/**'
  pull_request:
    paths:
      - 'config/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install pyyaml pydantic

      - name: Validate configurations
        run: |
          python scripts/validate_configs.py
          echo "配置验证通过" >> $GITHUB_STEP_SUMMARY

      - name: Check for plaintext secrets
        run: |
          if grep -rE "password.*['\"][^'\"]+['\"]" config/base/ 2>/dev/null | \
              grep -v "^#" | grep -v "\${" > /dev/null; then
            echo "⚠️ 发现可能明文密码" >> $GITHUB_STEP_SUMMARY
            exit 1
          fi
```

---

## 8. 最佳实践

### 8.1 配置管理清单

| 实践 | 说明 | 状态 |
|------|------|------|
| **12-Factor App** | 配置外部化，存储在环境变量中 | ☐ |
| **环境隔离** | 开发、测试、生产配置分离 | ☐ |
| **敏感信息保护** | 密码、密钥不存储在代码中 | ☐ |
| **配置版本控制** | 跟踪配置变更历史 | ☐ |
| **配置验证** | 启动时验证配置有效性 | ☐ |
| **默认值** | 提供合理的默认值 | ☐ |
| **文档** | 记录每个配置项的用途 | ☐ |

### 8.2 目录结构模板

```
config/
├── README.md                          # 配置说明文档
├── base/                              # 基础配置（所有环境通用）
│   ├── app.yaml                       # 应用主配置
│   ├── database.yaml                  # 数据库配置
│   ├── cache.yaml                     # 缓存配置
│   ├── data_sources.yaml              # 数据源配置
│   ├── features.yaml                  # 功能开关配置
│   └── logging.yaml                   # 日志配置
├── environments/                      # 环境特定配置
│   ├── development.yaml               # 开发环境
│   ├── testing.yaml                   # 测试环境
│   ├── staging.yaml                   # 预发布环境
│   └── production.yaml                # 生产环境
├── secrets/                           # 敏感配置（加密）
│   ├── .gitignore                     # 忽略加密密钥
│   └── template.yaml.example          # 敏感配置模板
└── scripts/
    ├── load_config.py                 # 配置加载脚本
    ├── validate_configs.py            # 配置验证脚本
    └── encrypt_secrets.py             # 加密脚本
```

### 8.3 配置加载示例

```python
# config/loader.py
import os
import yaml
from pathlib import Path
from functools import lru_cache

class ConfigLoader:
    """配置加载器，支持环境隔离和敏感信息保护"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.env = os.getenv("APP_ENV", "development")
    
    def load(self) -> dict:
        """加载完整配置"""
        config = {}
        
        # 1. 加载基础配置
        base_dir = self.config_dir / "base"
        for file in base_dir.glob("*.yaml"):
            config.update(self._load_file(file))
        
        # 2. 加载环境特定配置
        env_file = self.config_dir / "environments" / f"{self.env}.yaml"
        if env_file.exists():
            config.update(self._load_file(env_file))
        
        # 3. 加载敏感配置
        secrets_file = self.config_dir / "secrets" / f"{self.env}.yaml.enc"
        if secrets_file.exists():
            config.update(self._load_encrypted_file(secrets_file))
        
        # 4. 解析环境变量
        config = self._resolve_env_vars(config)
        
        return config
    
    def _load_file(self, file_path: Path) -> dict:
        """加载 YAML 文件"""
        with open(file_path) as f:
            return yaml.safe_load(f) or {}
    
    def _load_encrypted_file(self, file_path: Path) -> dict:
        """加载并解密配置文件"""
        from .secrets_manager import SecretsManager
        manager = SecretsManager()
        return manager.load_secrets(file_path)
    
    def _resolve_env_vars(self, config: dict) -> dict:
        """解析配置中的环境变量引用"""
        import re
        
        def resolve_value(value):
            if isinstance(value, str):
                # 匹配 ${VAR_NAME:default} 格式
                match = re.match(r'\$\{(\w+)(?::([^}]*))?\}', value)
                if match:
                    var_name = match.group(1)
                    default = match.group(2) or ""
                    return os.getenv(var_name, default)
            return value
        
        return {k: resolve_value(v) for k, v in config.items()}


@lru_cache()
def get_config() -> dict:
    """获取配置的全局单例"""
    loader = ConfigLoader()
    return loader.load()


# 使用示例
if __name__ == "__main__":
    config = get_config()
    print(f"环境: {config['app']['environment']}")
    print(f"数据库: {config['postgresql']['host']}")
```

### 8.4 常见问题处理

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 配置不生效 | 环境变量未加载 | 检查 env 文件加载顺序 |
| 密码泄露 | 明文存储在 YAML | 使用加密存储或环境变量 |
| 配置冲突 | 环境配置覆盖错误 | 检查配置继承关系 |
| 启动失败 | 必需配置缺失 | 添加配置验证 |
| 难以追踪 | 配置分散 | 使用集中配置管理 |

---

## 📚 相关文档

- [环境变量配置示例](#6-敏感信息管理)
- [基础设施检查手册](./INFRASTRUCTURE_CHECKLIST.md)
- [故障排除手册](./TROUBLESHOOTING.md)

---

*最后更新: 2026-01-14*
