# API契约管理CLI工具使用指南

> **使用说明**:
> 本文件是 API 相关的参考文档或专题说明，不是当前 API 契约、当前实施基线或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`；若涉及 API 契约事实源，再以实际的 FastAPI 路由 + Pydantic Schema + `/openapi.json` 为准。
>
> 文内端点、命令、统计值和示例如未重新复核，应视为参考或历史材料，不得直接当作当前事实。


## 📖 概述

`api-contract-sync` 是一个强大的命令行工具，用于管理API契约的完整生命周期。

### 核心功能

- ✅ **版本管理**: 创建、查询、激活、删除契约版本
- ✅ **差异检测**: 对比版本变更，自动识别破坏性变更
- ✅ **契约验证**: OpenAPI规范校验和最佳实践检查
- ✅ **导入导出**: 在文件和数据库之间同步契约
- ✅ **美观输出**: 使用Rich库提供彩色、格式化的终端输出

---

## 🚀 安装

### 方法1: 使用pip安装 (推荐)

```bash
cd /opt/claude/mystocks_phase6_api_contract/scripts/cli
pip install -e .
```

安装后，可以直接使用 `api-contract-sync` 命令:

```bash
api-contract-sync --help
```

### 方法2: 直接运行脚本

```bash
# 添加执行权限 (已完成)
chmod +x scripts/cli/api_contract_sync.py

# 运行CLI
python scripts/cli/api_contract_sync.py --help
```

### 依赖安装

```bash
pip install -r scripts/cli/requirements.txt
```

**依赖项**:
- `click` - CLI框架
- `rich` - 终端UI美化
- `requests` - HTTP请求
- `PyYAML` - YAML文件支持

---

## 🔧 配置

### API服务器地址

默认连接到 `http://localhost:8020`

**方法1**: 环境变量
```bash
export API_CONTRACT_API_URL="http://localhost:8020"
```

**方法2**: 命令行选项
```bash
api-contract-sync --api-url "http://api-server:8020" list
```

---

## 📚 命令参考

### 1. 版本管理

#### 创建契约版本

```bash
# 基本用法
api-contract-sync create <name> <version> -s <spec_file>

# 完整示例
api-contract-sync create market-api 1.0.0 \
  -s openapi.yaml \
  -a "developer-team" \
  -d "初始版本" \
  -t stable -t v1 \
  -c abc123def456 \
  --activate
```

**参数说明**:

| 参数 | 说明 |
|------|------|
| `name` | 契约名称 (如: market-api, trade-api) |
| `version` | 版本号 (遵循SemVer: 1.0.0) |
| `-s, --spec` | OpenAPI规范文件路径 (必填) |
| `-a, --author` | 作者或团队名称 |
| `-d, --description` | 版本描述 |
| `-t, --tag` | 版本标签 (可多次使用) |
| `-c, --commit-hash` | Git commit hash |
| `--activate` | 创建后自动激活 |

**示例**:
```bash
# 从YAML文件创建契约
api-contract-sync create market-api 1.0.0 -s docs/api/contracts/market-api.yaml

# 创建并激活新版本
api-contract-sync create market-api 1.1.0 \
  -s openapi.yaml \
  -a "backend-team" \
  -d "新增实时行情接口" \
  --activate
```

---

#### 列出契约版本

```bash
# 列出所有版本
api-contract-sync list

# 按名称过滤
api-contract-sync list --name market-api

# 分页查询
api-contract-sync list --name market-api --limit 10 --offset 0
```

**输出示例**:
```
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ ID ┃ 名称                ┃ 版本     ┃ 作者        ┃ 激活 ┃ 创建时间           ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ 1  │ market-api          │ 1.0.0    │ dev-team    │ ✅   │ 2025-12-29 10:00:00 │
│ 2  │ market-api          │ 1.1.0    │ dev-team    │ ❌   │ 2025-12-29 12:00:00 │
│ 3  │ trade-api           │ 1.0.0    │ backend     │ ✅   │ 2025-12-29 11:00:00 │
└────┴──────────────────────┴──────────┴─────────────┴──────┴────────────────────┘
```

---

#### 显示版本详情

```bash
api-contract-sync show <version_id>

# 示例
api-contract-sync show 1
```

**交互式询问**: 是否显示完整的OpenAPI规范

---

#### 获取激活版本

```bash
api-contract-sync active <name>

# 示例
api-contract-sync active market-api
```

**用途**: 快速查看当前生效的契约版本

---

#### 激活版本

```bash
api-contract-sync activate <version_id>

# 示例
api-contract-sync activate 2
```

**激活流程**:
1. 将该契约的所有版本设置为非激活
2. 将指定版本设置为激活
3. 记录激活操作到审计日志

---

#### 删除版本

```bash
# 交互式确认
api-contract-sync delete <version_id>

# 强制删除 (跳过确认)
api-contract-sync delete <version_id> --force

# 示例
api-contract-sync delete 5 --force
```

**⚠️ 警告**: 删除操作不可逆，不能删除激活版本

---

### 2. 契约列表

#### 列出所有契约

```bash
api-contract-sync contracts
```

**输出示例**:
```
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ 契约名称              ┃ 激活版本  ┃ 版本总数 ┃ 最后更新           ┃ 标签         ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ market-api            │ 1.2.0     │ 5        │ 2025-12-29 14:20:00 │ stable, v1   │
│ trade-api             │ 2.0.0     │ 3        │ 2025-12-28 16:45:00 │ stable, v2   │
│ technical-api         │ 1.0.0     │ 1        │ 2025-12-29 09:00:00 │ beta         │
└───────────────────────┴───────────┴──────────┴────────────────────┴──────────────┘
```

---

### 3. 差异检测

#### 对比两个版本

```bash
# 基本用法
api-contract-sync diff <from_version_id> <to_version_id>

# 示例
api-contract-sync diff 1 2

# 以JSON格式输出
api-contract-sync diff 1 2 --json-output
```

**输出示例**:
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                        📊 差异检测结果                              ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 源版本: 1.0.0                                                       │
│ 目标版本: 1.1.0                                                     │
│ 总变更数: 15                                                        │
│ 破坏性变更: 2                                                       │
│ 非破坏性变更: 13                                                    │
│                                                                    │
│ 摘要: 检测到2个破坏性变更和13个非破坏性变更。主要变更: 删除了     │
│       /api/market/symbols 端点，新增了 /api/market/quote 端点。   │
└────────────────────────────────────────────────────────────────────┘

详细差异 (15 条):
┏━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 类型         ┃ 变更     ┃ 路径                            ┃ 说明                          ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ breaking     │ removed  │ paths./api/market/symbols        │ 删除API端点                   │
│ non-breaking │ added    │ paths./api/market/quote         │ 新增API端点                   │
│ non-breaking │ modified │ components.schemas.Symbol       │ 修改字段: symbol              │
└──────────────┴──────────┴─────────────────────────────────┴───────────────────────────────┘

⚠️  检测到破坏性变更，请谨慎评估影响！
```

---

### 4. 契约验证

#### 验证OpenAPI规范

```bash
# 基本验证
api-contract-sync validate <spec_file>

# 检查破坏性变更
api-contract-sync validate openapi.yaml --check-breaking

# 对比指定版本
api-contract-sync validate openapi.yaml --check-breaking --compare-to 1
```

**输出示例**:
```
✨ 验证成功
✅ 验证通过
错误: 0
警告: 2

验证结果 (3 条):

[error] STRUCTURE
  路径: info
  说明: OpenAPI规范缺少必需字段: info.title

[warning] BEST_PRACTICES
  路径: paths./api/market/symbols.get
  说明: 建议为所有端点添加operationId

[warning] BEST_PRACTICES
  路径: paths./api/market/symbols.get.responses.200
  说明: 建议为响应添加示例
```

---

### 5. 导入导出

#### 导出契约版本

```bash
# 导出为YAML
api-contract-sync export <version_id> -o <output_file> -f yaml

# 导出为JSON
api-contract-sync export <version_id> -o <output_file> -f json

# 示例
api-contract-sync export 1 -o openapi-v1.yaml -f yaml
```

**用途**:
- 备份契约版本
- 生成文档站点
- 分享给前端团队

---

#### 导入契约版本

```bash
# 导入文件
api-contract-sync import <name> <version> -f <file>

# 导入并激活
api-contract-sync import market-api 1.0.0 -f openapi.yaml --activate

# 示例
api-contract-sync import market-api 1.2.0 \
  -f docs/api/contracts/market-api.yaml \
  --activate
```

**支持的格式**:
- YAML (`.yaml`, `.yml`)
- JSON (`.json`)

---

### 6. 契约同步

```bash
# 代码到数据库
api-contract-sync sync market-api -s openapi.yaml -d code-to-db -v 1.3.0

# 数据库到代码
api-contract-sync sync market-api -s openapi.yaml -d db-to-code

# 同步并提交到Git
api-contract-sync sync market-api -s openapi.yaml --commit
```

**注意**: 当前版本返回模拟结果，实际同步逻辑需根据项目需求实现。

---

## 💡 使用场景

### 场景1: 发布新API版本

```bash
# 1. 更新OpenAPI规范文件
vim openapi.yaml

# 2. 验证规范
api-contract-sync validate openapi.yaml --check-breaking

# 3. 创建新版本
api-contract-sync create market-api 1.2.0 \
  -s openapi.yaml \
  -a "backend-team" \
  -d "新增技术指标接口"

# 4. 对比版本差异
api-contract-sync diff 1 2

# 5. 激活新版本
api-contract-sync activate 2
```

---

### 场景2: 审查API变更

```bash
# 1. 查看所有契约
api-contract-sync contracts

# 2. 对比版本
api-contract-sync diff 5 6

# 3. 如果有破坏性变更，评估影响
# 4. 决定是否激活新版本
api-contract-sync activate 6
```

---

### 场景3: 契约备份与恢复

```bash
# 导出当前激活版本
api-contract-sync active market-api  # 获取version_id
api-contract-sync export 3 -o backup/market-api-v1.2.0.yaml

# 恢复到指定版本
api-contract-sync import market-api 1.2.0 \
  -f backup/market-api-v1.2.0.yaml \
  --activate
```

---

### 场景4: CI/CD集成

```bash
#!/bin/bash
# ci.sh - CI流水线脚本

# 1. 验证OpenAPI规范
api-contract-sync validate openapi.yaml --check-breaking

if [ $? -ne 0 ]; then
    echo "❌ 契约验证失败"
    exit 1
fi

# 2. 创建新版本
VERSION=$(date +%Y.%m.%d)
api-contract-sync create market-api $VERSION \
  -s openapi.yaml \
  -a "CI/CD" \
  -d "自动发布"

# 3. 激活新版本
VERSION_ID=$(api-contract-sync list --name market-api --limit 1 | jq '.[0].id')
api-contract-sync activate $VERSION_ID

echo "✅ API契约发布成功"
```

---

## 🎯 最佳实践

### 1. 版本号规范

遵循 **Semantic Versioning** (SemVer):

- **MAJOR** (1.x.x): 破坏性变更
- **MINOR** (x.1.x): 新增功能，向后兼容
- **PATCH** (x.x.1): Bug修复

**示例**:
```bash
# 破坏性变更
api-contract-sync create market-api 2.0.0 -s openapi.yaml

# 新增功能
api-contract-sync create market-api 1.1.0 -s openapi.yaml

# Bug修复
api-contract-sync create market-api 1.0.1 -s openapi.yaml
```

---

### 2. 版本描述规范

使用清晰的变更说明:

```bash
# ✅ 好的描述
api-contract-sync create market-api 1.1.0 \
  -d "新增实时行情接口: /api/market/realtime"

# ❌ 不好的描述
api-contract-sync create market-api 1.1.0 \
  -d "update"
```

---

### 3. 标签使用规范

推荐标签:
- `stable`: 稳定版本
- `beta`: 测试版本
- `deprecated`: 已弃用版本
- `v1`, `v2`: 主要版本标记

```bash
api-contract-sync create market-api 1.0.0 \
  -t stable -t v1
```

---

### 4. Git集成

记录Git commit hash:

```bash
# 获取当前commit
COMMIT_HASH=$(git rev-parse --short HEAD)

# 创建契约版本
api-contract-sync create market-api 1.0.0 \
  -s openapi.yaml \
  -c $COMMIT_HASH \
  -a "$(git config user.name)"
```

---

### 5. 批量操作

使用shell脚本批量处理:

```bash
#!/bin/bash
# batch-activate.sh - 批量激活最新版本

for contract in market-api trade-api technical-api; do
    echo "处理契约: $contract"

    # 获取最新版本ID
    LATEST_ID=$(api-contract-sync list --name $contract --limit 1 | jq '.[0].id')

    # 激活
    api-contract-sync activate $LATEST_ID
done
```

---

## 🔍 故障排除

### 问题1: 无法连接到API服务器

**错误**: `❌ 无法连接到API服务器: http://localhost:8020`

**解决方案**:
```bash
# 1. 检查后端服务是否运行
curl http://localhost:8020/health

# 2. 启动后端服务
cd web/backend
python -m app.main

# 3. 检查防火墙设置
sudo ufw status
```

---

### 问题2: 文件格式不支持

**错误**: `❌ 不支持的文件格式: .txt`

**解决方案**: 使用 `.yaml`, `.yml`, 或 `.json` 格式

```bash
# 转换为YAML
python -c "import json, yaml; yaml.dump(json.load(open('spec.json')), open('spec.yaml', 'w'))"
```

---

### 问题3: 权限不足

**错误**: `HTTP错误: 403`

**解决方案**: 当前版本未实现权限控制，请检查:
- API服务器配置
- 认证中间件设置

---

## 📊 性能优化

### 1. 并发请求

使用 `xargs` 并行处理:

```bash
# 并发验证多个文件
ls openapi-*.yaml | xargs -P 4 -I {} api-contract-sync validate {}
```

---

### 2. 缓存结果

将常用查询保存到文件:

```bash
# 保存版本列表
api-contract-sync list --name market-api > versions.txt

# 后续使用
cat versions.txt
```

---

## 🔗 相关文档

- [API契约管理平台使用文档](./CONTRACT_MANAGEMENT_API.md)
- [OpenAPI 3.0规范](https://swagger.io/specification/)
- [Semantic Versioning](https://semver.org/)

---

## 📝 开发计划

### 未来功能

- [ ] 支持批量导入/导出
- [ ] 交互式向导模式
- [ ] 自动生成变更日志
- [ ] 集成Git hooks
- [ ] 支持多种认证方式

---

**Historical Document Version Snapshot**: v1.0.0
**Historical Last Updated Snapshot**: 2025-12-29
**Historical Maintainer Snapshot**: MyStocks Team
