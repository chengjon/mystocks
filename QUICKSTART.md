# MyStocks 快速开始指南

**版本**: v2.1
**更新日期**: 2025-10-15
**预计完成时间**: 15分钟

本指南将帮助您快速启动 MyStocks 量化交易数据管理系统,并体验 v2.1 版本的 TDX 实时行情功能。

---

## 📋 前置要求

### 必需软件
- Python 3.8+
- Node.js 16+
- Git

### 可选软件
- Redis (用于缓存,提升性能)
- Docker & Docker Compose (用于容器化部署)

### 系统要求
- 操作系统: Linux / macOS / Windows (WSL2)
- 内存: 至少 4GB
- 磁盘: 至少 2GB 可用空间

---

## 🚀 5分钟快速启动 (Web界面)

### Step 1: 克隆项目
```bash
cd /opt/claude
git clone <your-repo-url> mystocks_spec
cd mystocks_spec
git checkout 005-tdx-web-tdx
```

### Step 2: 启动后端服务
```bash
cd web/backend

# 安装依赖
pip install -r requirements.txt

# 启动服务 (固定端口 8000)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

等待看到以下输出:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### Step 3: 启动前端服务
**打开新终端窗口**:
```bash
cd web/frontend

# 安装依赖 (首次运行)
npm install

# 启动开发服务器 (固定端口 3000)
npm run dev
```

等待看到以下输出:
```
VITE v5.4.20  ready in 734 ms

➜  Local:   http://localhost:3000/
```

### Step 4: 访问系统
1. 打开浏览器访问: **http://localhost:3000**
2. 使用默认账号登录:
   - **用户名**: `admin`
   - **密码**: `admin123`
3. 点击左侧菜单 **"市场行情"** > **"TDX行情"**
4. 输入股票代码 (如: `600519` 贵州茅台) 开始体验!

---

## 🎯 功能演示 (3分钟)

### 演示1: 查看实时股票行情
1. 在 TDX 行情页面输入: `600519`
2. 系统将显示:
   - 实时价格、涨跌幅
   - 五档买卖盘口
   - 成交量
   - K线图表

### 演示2: 切换K线周期
1. 点击周期按钮: `1m` / `5m` / `15m` / `30m` / `1h` / `1d`
2. K线图将自动更新显示对应周期数据

### 演示3: 查看指数行情
1. 页面顶部自动显示三大指数:
   - 上证指数 (000001)
   - 深证成指 (399001)
   - 创业板指 (399006)

### 演示4: 开启自动刷新
1. 勾选 "自动刷新" 复选框
2. 系统每5秒自动更新行情数据

---

## 🔧 进阶配置 (可选)

### 配置环境变量
创建 `.env` 文件 (如需使用完整数据库功能):
```bash
cd /opt/claude/mystocks_spec

cat > .env << 'EOF'
# MySQL配置 (参考数据)
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_PORT=3306
MYSQL_DATABASE=mystocks

# PostgreSQL配置 (衍生数据)
POSTGRESQL_HOST=localhost
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=your_password
POSTGRESQL_PORT=5432
POSTGRESQL_DATABASE=mystocks

# TDengine配置 (时序数据)
TDENGINE_HOST=localhost
TDENGINE_USER=root
TDENGINE_PASSWORD=taosdata
TDENGINE_PORT=6041
TDENGINE_DATABASE=mystocks

# Redis配置 (缓存)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
EOF
```

### 初始化数据库 (如需使用后台数据存储)
```bash
# 创建所有表结构
python -c "
from unified_manager import MyStocksUnifiedManager
manager = MyStocksUnifiedManager()
manager.initialize_system()
print('✅ 系统初始化完成!')
"
```

---

## 📊 API 测试 (开发者)

### 获取认证Token
```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

echo "Token: $TOKEN"
```

### 测试实时行情API
```bash
# 获取贵州茅台实时行情
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/tdx/quote/600519" | jq
```

### 测试K线数据API
```bash
# 获取日K线数据
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/tdx/kline?symbol=600519&period=1d&start_date=2025-10-01&end_date=2025-10-15" | jq
```

### 测试健康检查
```bash
# 无需认证
curl "http://localhost:8000/api/tdx/health" | jq
```

### 查看API文档
访问: **http://localhost:8000/api/docs**

---

## 🐛 常见问题排查

### 问题1: 端口被占用
```bash
# 检查端口占用
lsof -i :3000  # 前端
lsof -i :8000  # 后端

# 清理占用进程
pkill -f vite      # 清理前端
pkill -f uvicorn   # 清理后端
```

### 问题2: 前端显示空白页
```bash
# 检查浏览器控制台错误
# 检查前端日志
tail -f /tmp/frontend.log

# 重启前端
cd web/frontend
pkill -f vite
npm run dev
```

### 问题3: 后端API报错
```bash
# 查看后端日志
cd web/backend
tail -f server.log

# 或查看终端实时日志
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 问题4: TDX连接失败
```bash
# 测试TDX适配器
cd /opt/claude/mystocks_spec
python test_tdx_mvp.py

# 查看TDX服务器配置
cat utils/tdx_server_config.py

# 系统会自动尝试38个备用服务器,通常能自动恢复
```

### 问题5: 认证失败 401/403
```bash
# Token可能过期 (默认30分钟),重新登录获取新token
# 或检查请求头是否包含: Authorization: Bearer <token>
```

---

## 📂 项目目录结构

```
mystocks_spec/
├── web/                          # Web系统 (v2.1)
│   ├── backend/                  # FastAPI后端
│   │   ├── app/
│   │   │   ├── api/tdx.py       # TDX API路由
│   │   │   ├── services/tdx_service.py  # TDX服务
│   │   │   └── schemas/tdx_schemas.py   # TDX数据模型
│   │   └── main.py              # 应用入口
│   ├── frontend/                 # Vue3前端
│   │   └── src/views/TdxMarket.vue  # TDX行情页面
│   ├── PORTS.md                  # 端口配置规则
│   └── TDX_SETUP_COMPLETE.md    # 部署文档
│
├── adapters/                     # 数据源适配器
│   ├── tdx_adapter.py           # TDX适配器 (v2.1)
│   ├── akshare_adapter.py       # Akshare适配器
│   └── data_source_manager.py   # 数据源管理器
│
├── core.py                       # 核心管理模块
├── unified_manager.py            # 统一管理器
├── monitoring.py                 # 监控系统
│
├── test_tdx_mvp.py              # TDX功能测试
├── test_tdx_api.py              # TDX API测试
│
├── CHANGELOG_v2.1.md            # 版本更新日志
├── QUICKSTART.md                # 本文件
└── README.md                     # 项目主文档
```

---

## 🎓 学习路径

### 新手用户 (5分钟)
1. ✅ 按照 "5分钟快速启动" 启动系统
2. ✅ 体验 TDX 实时行情功能
3. ✅ 查看三大指数监控
4. 📖 阅读 `web/README.md`

### 开发者 (30分钟)
1. ✅ 完成新手步骤
2. ✅ 测试所有 API 接口
3. ✅ 查看 API 文档: http://localhost:8000/api/docs
4. 📖 阅读 `CHANGELOG_v2.1.md` 了解架构
5. 📖 阅读 `adapters/README_TDX.md` 了解TDX适配器
6. 🔧 运行测试脚本: `python test_tdx_api.py`

### 系统管理员 (1小时)
1. ✅ 完成开发者步骤
2. ✅ 配置生产环境 `.env` 文件
3. ✅ 初始化所有数据库
4. ✅ 配置 Docker 部署
5. 📖 阅读 `CLAUDE.md` 了解系统架构
6. 🔧 运行系统演示: `python system_demo.py`

---

## 📈 性能指标

### TDX 实时行情系统 (v2.1)
- ⚡ 健康检查响应: < 50ms
- ⚡ 实时行情查询: < 100ms
- ⚡ K线数据查询: < 150ms (500条以内)
- 🔌 支持并发用户: 50+
- 🔄 自动重连: 支持 (38个备用服务器)

---

## 🔗 相关资源

### 文档
- [完整更新日志](./CHANGELOG_v2.1.md)
- [Web系统文档](./web/README.md)
- [TDX适配器文档](./adapters/README_TDX.md)
- [端口配置规则](./web/PORTS.md)
- [项目架构说明](./CLAUDE.md)

### 测试脚本
- `test_tdx_mvp.py` - TDX基础功能测试
- `test_tdx_multiperiod.py` - 多周期K线测试
- `test_tdx_api.py` - API接口完整测试
- `system_demo.py` - 系统完整演示

### 开发命令
```bash
# 系统初始化
python -c "from unified_manager import MyStocksUnifiedManager; manager = MyStocksUnifiedManager(); manager.initialize_system()"

# 运行测试
python test_tdx_api.py

# 查看数据库状态
python check_mysql_tables.py
python check_tdengine_tables.py

# 验证表结构
python -c "from core import ConfigDrivenTableManager; mgr = ConfigDrivenTableManager(); mgr.validate_all_table_structures()"
```

---

## 🎉 下一步

### 立即尝试
- [ ] 在 TDX 行情页面输入您关注的股票代码
- [ ] 尝试不同的K线周期切换
- [ ] 开启自动刷新观察实时变化
- [ ] 查看三大指数的实时表现

### 深入学习
- [ ] 查看完整 API 文档
- [ ] 运行所有测试脚本
- [ ] 阅读系统架构文档
- [ ] 配置自己的数据库环境

### 生产部署
- [ ] 配置 HTTPS 证书
- [ ] 设置反向代理 (Nginx)
- [ ] 配置 Redis 缓存
- [ ] 配置日志轮转
- [ ] 设置系统监控告警

---

## 📝 开发规范 (Developer Guidelines)

### 文档元数据规范

所有MD文档必须在文件开头包含以下元数据标记:

```markdown
**创建人**: [Claude/JohnC/Spec-Kit/团队成员名]
**版本**: [语义化版本号，如1.0.0]
**批准日期**: [YYYY-MM-DD]
**最后修订**: [YYYY-MM-DD]
**本次修订内容**: [简要描述本次修改的内容]
```

**示例**:
```markdown
**创建人**: JohnC & Claude
**版本**: 2.1.0
**批准日期**: 2025-10-15
**最后修订**: 2025-10-16
**本次修订内容**: 添加TDX实时行情功能说明和快速开始指南
```

**使用原则**:
- 创建新文档时必须添加完整的5个字段
- 修改文档时必须更新"最后修订"和"本次修订内容"
- 版本号遵循语义化版本规范(MAJOR.MINOR.PATCH)
- 批准日期为文档正式发布日期
- 本次修订内容应简洁明了，突出核心变更

### Python头注释规范

所有Python文件必须包含标准头部注释（文件开头，在所有import之前）:

```python
'''
# -*- coding: utf-8 -*-  # Python 3.8+可省略
# 功能：[简要描述文件用途，1-2句话]
# 作者：JohnC (ninjas@sina.com) & Claude
# 日期：YYYY-MM-DD
# 版本：v2.1.0
# 依赖：[关键依赖或指向requirements.txt]
# 注意事项：[重要约束或使用限制]
# 版权：© 2025 All rights reserved.
'''
```

**示例**:
```python
'''
# -*- coding: utf-8 -*-
# 功能：通达信TDX数据源适配器，提供实时行情和多周期K线数据获取
# 作者：JohnC (ninjas@sina.com) & Claude
# 日期：2025-10-15
# 版本：v2.1.0
# 依赖：pandas, pytdx, numpy (详见requirements.txt)
# 注意事项：需要网络连接访问TDX服务器，支持自动故障转移
# 版权：© 2025 All rights reserved.
'''

import pandas as pd
from pytdx.hq import TdxHq_API
```

**注释语言规范**:
- **技术术语**: 保留英文 (如API、DataFrame、Token、Cache、Exception、Factory、Manager等)
- **描述性内容**: 使用中文 (功能说明、参数解释、注意事项等)
- **示例**: "从Redis Cache中获取股票实时行情数据"

**Docstring规范** (类和函数):
```python
def get_kline_data(symbol: str, period: str = "1d") -> pd.DataFrame:
    """
    获取K线数据

    Args:
        symbol: 股票代码，如'600519'或'600519.SH'
        period: K线周期，支持 1m/5m/15m/30m/1h/1d (默认: 1d)

    Returns:
        DataFrame包含: symbol, timestamp, open, high, low, close, volume

    Raises:
        ConnectionError: TDX服务器连接失败
        ValueError: 股票代码格式不正确

    Example:
        >>> df = get_kline_data('600519', '1d')
        >>> print(df.head())
    """
    pass
```

---

## 📞 获取帮助

### 遇到问题?
1. 查看 "常见问题排查" 章节
2. 检查相关日志文件
3. 参考 `CHANGELOG_v2.1.md` 中的已知问题
4. 运行测试脚本诊断问题

### 系统状态检查
```bash
# 后端健康检查
curl http://localhost:8000/api/tdx/health

# 前端访问检查
curl http://localhost:3000

# 进程检查
ps aux | grep uvicorn  # 后端进程
ps aux | grep vite     # 前端进程

# 端口检查
lsof -i :3000  # 前端端口
lsof -i :8000  # 后端端口
```

---

**祝您使用愉快! 🎊**

*MyStocks v2.1 - 专业的量化交易数据管理系统*
