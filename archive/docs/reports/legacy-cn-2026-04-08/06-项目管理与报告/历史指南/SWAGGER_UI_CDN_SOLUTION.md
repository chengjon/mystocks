# Swagger UI CDN 访问问题解决方案

> **历史文档说明**:
> 本文件是某阶段的历史文档、过程记录或专题材料，不是当前基线、当前系统总览或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内描述、背景、结论和上下文如未重新复核，应视为历史快照，不得直接当作当前事实。


> **问题**: WSL2 环境下所有外部 CDN (jsdelivr, unpkg, bootcdn, staticfile) 均无法访问
> **根本原因**: CDN 的 HTTPS 连接被防火墙或网络策略阻止
> **解决方案**: 使用本地 Swagger UI 静态文件

---

## 📊 诊断结果

### ✅ 网络基础正常
- DNS 解析: ✅ 正常 (`cdn.jsdelivr.net` → `59.24.3.174`)
- 网络连通: ✅ 正常 (可 ping 通 8.8.8.8)
- HTTPS 连接: ✅ 正常 (可访问 baidu.com)

### ❌ CDN 访问失败
- `cdn.jsdelivr.net`: ❌ 连接超时
- `unpkg.com`: ❌ 连接超时
- `cdn.bootcdn.net`: ❌ 连接失败
- `cdn.staticfile.org`: ❌ 连接超时

**结论**: 特定 CDN 域名的 HTTPS 连接被阻止，需要本地化解决方案。

---

## 🎯 推荐解决方案

### 方案 1: 使用 Python 包安装（⭐⭐⭐⭐⭐ 最推荐）

**步骤 1**: 安装 `swagger-ui-py` 包

```bash
pip install swagger-ui-py
```

**步骤 2**: 修改 `app/main.py`

在文件开头添加导入：
```python
from swagger_ui import api_doc
```

在 `app = FastAPI(...)` 之后，添加：
```python
# 配置本地 Swagger UI（使用 swagger-ui-py 包）
api_doc(
    app,
    config_path='/openapi.json',
    url_prefix='/api/docs',
    title='MyStocks Web API - Swagger UI'
)
```

同时修改 FastAPI 初始化，禁用默认 Swagger UI：
```python
app = FastAPI(
    # ... 其他配置 ...
    docs_url=None,  # 禁用默认 Swagger UI
    redoc_url="/api/redoc",
    # ... 其他配置 ...
)
```

**步骤 3**: 重启服务
```bash
# 服务会自动重启（--reload 模式）
# 或手动重启：
pkill -f "uvicorn app.main:app"
cd /opt/claude/mystocks_spec/web/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
```

**优点**:
- ✅ 完全本地化，无需外部网络
- ✅ 版本管理清晰（通过 pip）
- ✅ 自动依赖管理
- ✅ 1 条命令即可完成

---

### 方案 2: 手动下载并配置静态文件（⭐⭐⭐⭐ 备选）

**如果方案 1 失败**，可以使用已安装的 Python 包中的 Swagger UI 文件。

**步骤 1**: 从已安装的包中提取 Swagger UI 文件

```bash
# 查找 swagger-ui-dist 包路径
python3 -c "import swagger_ui_dist; print(swagger_ui_dist.__file__)"

# 假设路径为: /root/miniconda3/envs/stock/lib/python3.12/site-packages/swagger_ui_dist

# 创建本地目录
mkdir -p /opt/claude/mystocks_spec/web/backend/app/static/swagger-ui

# 复制必需文件
cp /path/to/swagger-ui-dist/swagger-ui-bundle.js \
   /opt/claude/mystocks_spec/web/backend/app/static/swagger-ui/
cp /path/to/swagger-ui-dist/swagger-ui.css \
   /opt/claude/mystocks_spec/web/backend/app/static/swagger-ui/
cp /path/to/swagger-ui-dist/swagger-ui-standalone-preset.js \
   /opt/claude/mystocks_spec/web/backend/app/static/swagger-ui/
```

**步骤 2**: 修改 `app/main.py` 挂载静态文件

在文件开头添加导入：
```python
from fastapi.staticfiles import StaticFiles
from pathlib import Path
```

在创建 FastAPI app 后添加：
```python
# 挂载静态文件目录
swagger_ui_path = Path(__file__).parent / "static"
if swagger_ui_path.exists():
    app.mount("/static", StaticFiles(directory=str(swagger_ui_path)), name="static")
```

**步骤 3**: 修改 `app/openapi_config.py`

```python
"swagger_ui_parameters": {
    "defaultModelsExpandDepth": 2,
    "defaultModelExpandDepth": 2,
    "docExpansion": "list",
    "filter": True,
    "showExtensions": True,
    "showCommonExtensions": True,
    "syntaxHighlight.theme": "monokai",
    # 使用本地静态文件
    "swagger_js_url": "/static/swagger-ui/swagger-ui-bundle.js",
    "swagger_css_url": "/static/swagger-ui/swagger-ui.css",
    "swagger_ui_standalone_preset_url": "/static/swagger-ui/swagger-ui-standalone-preset.js",
},
```

---

### 方案 3: 临时解决方案 - 使用 ReDoc（⭐⭐⭐ 立即可用）

**无需任何修改**，直接使用备用 API 文档界面：

```
http://172.26.26.12:8000/api/redoc
```

**特点**:
- ✅ 立即可用
- ✅ 界面更适合阅读文档
- ❌ 无法直接测试 API（只读）

---

### 方案 4: 使用 Postman（⭐⭐⭐ 专业工具）

**步骤 1**: 下载 OpenAPI 规范

```bash
curl http://172.26.26.12:8000/openapi.json > mystocks-api.json
```

**步骤 2**: 在 Postman 中导入

1. 打开 Postman
2. Import → Upload Files → 选择 `mystocks-api.json`
3. 自动生成 204 个 API 端点

**步骤 3**: 配置环境变量

```
base_url: http://172.26.26.12:8000
jwt_token: (登录后获取)
csrf_token: (从 /api/csrf-token 获取)
```

---

## 🔧 网络问题排查（高级）

如果希望从根本上解决��络问题，可以尝试以下方法：

### 1. 配置 HTTP 代理

```bash
# 编辑 /etc/environment
sudo nano /etc/environment

# 添加代理配置
export http_proxy="http://proxy-server:port"
export https_proxy="http://proxy-server:port"
export no_proxy="localhost,127.0.0.1,172.26.26.12"

# 重启 WSL2
exit
# 在 PowerShell 中: wsl --shutdown
```

### 2. 修改 DNS 服务器

```bash
# 编辑 /etc/wsl.conf
sudo nano /etc/wsl.conf

# 添加以下内容
[network]
generateResolvConf = false

# 编辑 /etc/resolv.conf
sudo nano /etc/resolv.conf

# 使用国内 DNS
nameserver 223.5.5.5  # 阿里 DNS
nameserver 119.29.29.29  # 腾讯 DNS
nameserver 8.8.8.8  # Google DNS (备用)

# 重启 WSL2
```

### 3. 检查 Windows 防火墙

```powershell
# 在 Windows PowerShell (管理员) 中执行

# 检查防火墙规则
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*WSL*"}

# 如果需要，添加允许规则
New-NetFirewallRule -DisplayName "WSL2-HTTPS-OUT" `
  -Direction Outbound `
  -Protocol TCP `
  -RemotePort 443 `
  -Action Allow
```

---

## 📞 需要进一步帮助？

如果以上方案都无法解决问题，请提供以下信息：

1. **网络环境**: 公司网络？家庭网络？VPN？
2. **错误信息**: 浏览器 F12 控制台的具体错误
3. **Network 标签**: 哪些资源加载失败（截图）

---

**最后更新**: 2025-11-10
**推荐方案**: 方案 1 (pip install swagger-ui-py) - 最简单可靠
