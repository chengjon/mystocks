# Swagger UI 本地化方案 - 快速参考

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或专题文档，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


> ✅ **状态**: 已完全解决并验证
> 📅 **完成时间**: 2025-11-10
> 🎯 **问题**: WSL2 环境 CDN 被墙
> 💡 **解决方案**: swagger-ui-py 静态文件 + FastAPI 原生 HTML 生成

---

## 🚀 快速验证

### 访问 Swagger UI
```
http://172.26.26.12:8000/api/docs
http://localhost:8000/api/docs
```

### 访问 ReDoc (备用)
```
http://172.26.26.12:8000/api/redoc
http://localhost:8000/api/redoc
```

### OpenAPI 规范
```
http://172.26.26.12:8000/openapi.json
```

---

## 📋 实施摘要

### 方案架构
```
┌─────────────────────────────────────────┐
│  浏览器请求 /api/docs                      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  FastAPI 自定义端点                        │
│  get_swagger_ui_html()                   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  返回 HTML 页面                           │
│  引用本地静态文件:                          │
│  /swagger-ui-static/swagger-ui-bundle.js│
│  /swagger-ui-static/swagger-ui.css      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  StaticFiles 中间件                       │
│  从 swagger-ui-py 包提供静态文件            │
└─────────────────────────────────────────┘
```

### 核心代码 (main.py)

**导入**:
```python
import os
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
```

**挂载静态文件**:
```python
import swagger_ui
swagger_ui_path = os.path.join(os.path.dirname(swagger_ui.__file__), "static")
app.mount("/swagger-ui-static", StaticFiles(directory=swagger_ui_path), name="swagger-ui-static")
```

**自定义端点**:
```python
@app.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{openapi_config['title']} - Swagger UI",
        swagger_js_url="/swagger-ui-static/swagger-ui-bundle.js",
        swagger_css_url="/swagger-ui-static/swagger-ui.css",
        swagger_favicon_url="/swagger-ui-static/favicon-32x32.png",
    )
```

---

## ✅ 验证清单

- [x] Swagger UI 页面可访问
- [x] 所有静态资源从本地加载
- [x] 无外部 CDN 依赖
- [x] OpenAPI 规范正确生成 (204 endpoints)
- [x] 服务稳定运行，无错误日志
- [x] 支持 localhost 和 WSL2 IP 访问

---

## 🔧 依赖包

```txt
swagger-ui-py>=25.7.0
```

**当前版本**: `swagger-ui-py==25.7.1`

**包含内容**:
- swagger-ui-bundle.js (1.4MB)
- swagger-ui.css (152KB)
- swagger-ui-standalone-preset.js (224KB)
- favicon 图标

---

## 📊 关键特性

### ✅ 优势
1. **完全本地化**: 零外部依赖
2. **快速加载**: 无网络延迟
3. **FastAPI 兼容**: 使用原生 HTML 生成器
4. **稳定可靠**: 不受 CDN 影响
5. **版本可控**: 通过 pip 管理

### ⚠️ 避免的错误
1. ❌ **不要使用** `from swagger_ui import api_doc`
2. ❌ **不要调用** `api_doc(app, ...)`
3. ✅ **必须禁用** FastAPI 默认 docs: `docs_url=None`
4. ✅ **必须手动挂载** 静态文件目录

---

## 🐛 故障排查

### 问题: 看到 AssertionError from swagger-ui-py

**原因**: 旧的 `api_doc()` 路由仍在应用中

**解决方案**:
```bash
# 完全重启服务 (不是 reload)
pkill -f "uvicorn app.main:app"
cd /opt/claude/mystocks_spec/web/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
```

### 问题: 静态文件 404

**检查**:
```bash
# 验证 swagger-ui-py 已安装
pip show swagger-ui-py

# 验证静态文件路径
python3 -c "import swagger_ui; print(swagger_ui.__file__)"
```

### 问题: 页面空白

**检查浏览器控制台** (F12):
- 查看 Network 标签
- 确认所有资源都从 `/swagger-ui-static/` 加载
- 确认无 CORS 错误

---

## 📚 详细文档

- **完整实施报告**: `SWAGGER_UI_FINAL_SOLUTION.md`
- **第一阶段报告**: `SWAGGER_UI_LOCAL_SOLUTION_SUCCESS.md`
- **CDN 诊断**: `SWAGGER_UI_CDN_SOLUTION.md`

---

## 💡 生产部署

### Docker 部署

**Dockerfile**:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ app/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 启动命令

**开发环境**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**生产环境**:
```bash
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

---

## 🎯 技术要点

### FastAPI 静态文件挂载
- 使用 `app.mount()` 挂载整个目录
- 自动处理 MIME 类型
- 支持 HTTP 缓存头

### FastAPI Swagger UI 自定义
- 使用 `get_swagger_ui_html()` 生成 HTML
- 完全控制资源 URL
- `include_in_schema=False` 隐藏端点

### swagger-ui-py 包
- 包含完整 Swagger UI 5.x 静态文件
- 安装位置: `site-packages/swagger_ui/static/`
- 无需手动下载或管理文件

---

**最后更新**: 2025-11-10
**状态**: ✅ 生产就绪
**验证**: 已在 WSL2 环境完全验证
