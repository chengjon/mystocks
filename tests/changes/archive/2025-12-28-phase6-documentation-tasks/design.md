# Design: Phase 6 Documentation Architecture

**Change ID**: `phase6-documentation-tasks`
**Last Updated**: 2025-12-28

## 🎯 Design Goals

1. **完整性**: 覆盖所有系统功能和 API 端点
2. **一致性**: 统一文档风格和格式
3. **可维护性**: 文档与代码同步更新
4. **可用性**: 便于用户快速查找和使用

## 📁 Documentation Structure

```
docs/
├── api/                          # API 文档
│   ├── API_INDEX.md             # API 文档索引
│   ├── DATA_MODELS.md           # 数据模型文档
│   ├── ERROR_CODES.md           # 错误码参考
│   └── openapi.json             # OpenAPI Schema (自动生成)
│
├── guides/                       # 用户指南
│   ├── DEPLOYMENT.md            # 部署指南
│   ├── TROUBLESHOOTING.md       # 故障排查手册
│   ├── USER_GUIDE.md            # 用户使用指南
│   └── QUICKSTART.md            # 快速开始指南
│
├── architecture/                 # 架构文档
│   ├── ARCHITECTURE.md          # 系统架构说明
│   └── SYSTEM_DIAGRAM.png       # 系统架构图
│
└── standards/                    # 开发规范
    ├── CODING_STANDARDS.md      # 代码规范
    └── GIT_WORKFLOW.md          # Git 工作流

README.md                         # 项目主文档 (根目录)
CHANGELOG.md                      # 发布说明 (根目录)
openspec/project.md               # 项目规范 (根目录)
```

## 📝 Documentation Standards

### 1. Markdown 格式规范

```markdown
# 标题 (H1) - 仅用于页面主标题

## 二级标题 - 主要章节

### 三级标题 - 子章节

#### 四级标题 - 小节

**加粗** 用于强调关键概念
`代码` 用于代码片段和命令
> 引用 用于注意事项和提示
```

### 2. 代码示例规范

```markdown
```bash
# Shell 命令示例
npm run dev

```python
# Python 代码示例
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}
```
```

### 3. API 文档规范

每个 API 端点需包含：

```markdown
## HTTP 方法 /api/endpoint

### Description
端点的功能描述

### Parameters
| Name | Type | Required | Description |
|------|------|----------|-------------|
| param1 | string | Yes | 参数说明 |

### Request Body (if applicable)
```json
{
  "key": "value"
}
```

### Response
```json
{
  "code": 200,
  "data": {},
  "msg": "success"
}
```

### Error Codes
- `400`: Bad Request
- `401`: Unauthorized
- `500`: Internal Server Error
```

## 🔄 Documentation Maintenance Strategy

### 1. 代码即文档

- FastAPI 自动生成 OpenAPI Schema
- Docstring 自动提取为 API 文档
- 使用类型注解增强文档可读性

### 2. 文档更新触发条件

| 触发条件 | 文档更新 |
|---------|---------|
| 新增 API 端点 | API_INDEX.md, openapi.json |
| 修改数据模型 | DATA_MODELS.md |
| 新增错误类型 | ERROR_CODES.md |
| 部署配置变更 | DEPLOYMENT.md |
| 架构变更 | ARCHITECTURE.md |

### 3. 文档审查流程

1. **提交前**: 运行文档检查脚本
2. **合并前**: Code Review 包含文档审查
3. **发布前**: 全量文档验证

## 🛠️ Tools and Automation

### 1. 文档生成工具

| 工具 | 用途 |
|------|------|
| FastAPI (get_openapi) | 生成 OpenAPI Schema |
| Swagger UI | 在线 API 文档 |
| ReDoc | 替代 API 文档界面 |
| Markdownlint | Markdown 格式检查 |

### 2. 验证命令

```bash
# 生成 OpenAPI Schema
python3 -c "
from fastapi.openapi.utils import get_openapi
from app.main import app
import json

schema = get_openapi(
    title=app.title,
    version=app.version,
    routes=app.routes
)
with open('docs/api/openapi.json', 'w') as f:
    json.dump(schema, f, indent=2)
"

# 检查文档完整性
python3 scripts/dev/validate_documentation.py

# Markdown 格式检查
npx markdownlint docs/**/*.md
```

## 📊 Documentation Metrics

| 指标 | 目标值 |
|------|-------|
| API 端点文档覆盖率 | 100% |
| 数据模型文档覆盖率 | 100% |
| 错误码文档覆盖率 | 100% |
| 部署步骤验证通过率 | 100% |
| 文档更新延迟 | ≤ 1 个版本周期 |

## 🔒 Security Considerations

1. **敏感信息**: 确保文档中不包含敏感信息（如密码、密钥）
2. **访问控制**: API 文档应包含认证说明
3. **示例数据**: 使用示例数据而非真实生产数据

## 🚀 Future Enhancements

1. **多语言支持**: 英文文档翻译
2. **交互式文档**: Swagger UI 集成认证模拟
3. **版本化文档**: API 版本历史记录
4. **搜索功能**: 文档全文搜索
5. **自动化测试**: API 文档与测试用例同步
