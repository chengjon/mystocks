# MyStocks Web 管理界面

## 项目概述
基于 MyStocks 量化交易数据管理系统的 Web 可视化管理界面，提供数据查询、技术分析、指标计算、实时行情监控等功能。

**当前版本**: v2.1 (2025-10-15)
**分支**: `005-tdx-web-tdx`
**状态**: ✅ 生产就绪

## 技术栈
- **后端**: FastAPI + Python 3.8+ + Uvicorn
- **前端**: Vue.js 3 + Element Plus + klinecharts
- **数据源**: TDX (通达信) + Akshare + Baostock
- **数据库**: MySQL/MariaDB (参考数据) + PostgreSQL+TimescaleDB (衍生数据) + TDengine (时序数据) + Redis (缓存)
- **认证**: JWT Token
- **部署**: Docker + Docker Compose

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- Redis (可选，用于缓存)
- Docker (可选，用于容器化部署)

### 端口配置规则 (v2.1)
**严格遵守以下端口配置** (详见 `web/PORTS.md`):
- **前端**: 固定端口 3000 (备用 3001)
- **后端**: 固定端口 8000
- **禁止随意更改端口号**

### 后端启动
```bash
cd web/backend

# 安装依赖
pip install -r requirements.txt

# 启动服务 (固定端口 8000)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 或使用后台运行
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > server.log 2>&1 &
```

### 前端启动
```bash
cd web/frontend

# 安装依赖
npm install

# 启动开发服务器 (固定端口 3000)
npm run dev

# 或使用后台运行
nohup npm run dev > /tmp/frontend.log 2>&1 &
```

### Docker 启动
```bash
cd web
docker-compose up -d
```

### 访问地址
- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/api/docs
- **默认登录**:
  - 用户名: `admin`
  - 密码: `admin123`

## 功能特性

### v2.1 新增功能 ⭐
- 🎯 **TDX (通达信) 实时行情**: 完整的实时股票和指数行情监控
- 📊 **多周期K线图**: 支持 1m/5m/15m/30m/1h/1d 六种周期
- 📈 **指数监控面板**: 实时显示上证指数、深证成指、创业板指
- 🔄 **自动刷新**: 可配置的5秒自动刷新功能
- 🔌 **智能故障转移**: TDX服务器自动切换,确保数据稳定性
- 🔒 **JWT认证**: 完整的用户认证和授权机制
- ⚡ **高性能**: 实时行情<100ms, K线查询<150ms

### 基础功能
- 📊 实时 K 线图表显示 (基于 klinecharts)
- 📈 技术指标计算和显示 (MA, MACD, RSI, BOLL等)
- 🔍 多维度数据筛选
- 📥 数据导出功能
- 👥 用户权限管理
- 🏷️ 股票分组管理
- 🔔 实时告警功能

## 项目结构
```
web/
├── backend/                      # FastAPI 后端
│   ├── app/
│   │   ├── api/                 # API 路由
│   │   │   ├── auth.py          # 用户认证
│   │   │   ├── data.py          # 数据查询
│   │   │   ├── indicators.py    # 技术指标
│   │   │   ├── market.py        # 市场数据
│   │   │   ├── system.py        # 系统管理
│   │   │   └── tdx.py           # TDX行情 (v2.1 新增)
│   │   ├── core/                # 核心配置
│   │   │   ├── config.py        # 配置管理
│   │   │   ├── security.py      # 安全认证
│   │   │   └── database.py      # 数据库连接
│   │   ├── services/            # 业务逻辑
│   │   │   ├── data_service.py  # 数据服务
│   │   │   └── tdx_service.py   # TDX服务 (v2.1 新增)
│   │   ├── schemas/             # 数据模型
│   │   │   ├── user.py          # 用户模型
│   │   │   └── tdx_schemas.py   # TDX模型 (v2.1 新增)
│   │   └── utils/               # 工具函数
│   └── main.py                   # 应用入口
├── frontend/                     # Vue3 前端
│   ├── src/
│   │   ├── views/               # 页面组件
│   │   │   ├── Login.vue        # 登录页
│   │   │   ├── Market.vue       # 市场行情
│   │   │   └── TdxMarket.vue    # TDX行情 (v2.1 新增)
│   │   ├── layout/              # 布局组件
│   │   │   └── index.vue        # 主布局 (v2.1 更新菜单)
│   │   ├── router/              # 路由配置
│   │   │   └── index.js         # 路由表 (v2.1 新增TDX路由)
│   │   ├── api/                 # API 调用
│   │   └── utils/               # 工具函数
│   └── vite.config.js           # Vite配置 (v2.1 修复代理)
├── PORTS.md                      # 端口配置规则 (v2.1 新增)
├── TDX_SETUP_COMPLETE.md        # TDX部署文档 (v2.1 新增)
└── docker-compose.yml            # 容器化配置
```

## API 接口文档 (v2.1)

### TDX 行情接口

#### 1. 健康检查
```bash
GET /api/tdx/health
# 无需认证
```

#### 2. 获取实时股票行情
```bash
GET /api/tdx/quote/{symbol}
Authorization: Bearer <token>

# 示例
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/tdx/quote/600519"
```

#### 3. 获取股票K线数据
```bash
GET /api/tdx/kline?symbol={code}&period={period}&start_date={date}&end_date={date}
Authorization: Bearer <token>

# 参数
# - symbol: 6位股票代码
# - period: 1m/5m/15m/30m/1h/1d
# - start_date: 开始日期 YYYY-MM-DD
# - end_date: 结束日期 YYYY-MM-DD

# 示例
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/tdx/kline?symbol=600519&period=1d&start_date=2025-10-01&end_date=2025-10-15"
```

#### 4. 获取指数实时行情
```bash
GET /api/tdx/index/quote/{symbol}
Authorization: Bearer <token>

# 示例 (上证指数)
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/tdx/index/quote/000001"
```

#### 5. 获取指数K线数据
```bash
GET /api/tdx/index/kline?symbol={code}&period={period}&start_date={date}&end_date={date}
Authorization: Bearer <token>
```

### 认证接口
```bash
# 登录获取token
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123

# 返回
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

## 使用指南

### TDX 行情使用
1. **登录系统**: http://localhost:3000
2. **导航到TDX行情**: 点击 "市场行情" > "TDX行情"
3. **查看实时行情**: 输入6位股票代码 (如: 600519)
4. **切换K线周期**: 点击周期按钮 (1m/5m/15m/30m/1h/1d)
5. **开启自动刷新**: 勾选"自动刷新"复选框 (5秒刷新)
6. **查看指数**: 页面顶部显示上证、深证、创业板指数

### 性能优化建议
- 实时行情建议5秒刷新间隔
- K线查询建议限制在1000条以内
- 生产环境建议配置Redis缓存
- 建议使用多个TDX服务器提高可用性

## 开发进度

### v2.1 (2025-10-15) ✅
- [x] TDX数据源集成
- [x] TDX实时行情API
- [x] TDX多周期K线API
- [x] TDX前端页面开发
- [x] 指数监控面板
- [x] JWT认证集成
- [x] 菜单结构优化
- [x] 端口配置规范化
- [x] API代理配置修复
- [x] 完整测试验证

### v1.0 基础功能
- [x] 项目结构创建
- [x] FastAPI 后端框架
- [x] Vue3 前端框架
- [x] 数据查询 API
- [x] K 线图表集成
- [x] 技术指标计算
- [x] 用户认证权限
- [x] 数据筛选导出
- [x] 本地部署测试

## 故障排查

### 前端无法访问
1. 检查端口占用: `lsof -i :3000`
2. 检查Vite进程: `ps aux | grep vite`
3. 清理旧进程: `pkill -f vite`
4. 重启前端: `cd web/frontend && npm run dev`

### 后端API报错
1. 检查后端日志: `tail -f web/backend/server.log`
2. 检查端口占用: `lsof -i :8000`
3. 验证TDX连接: `curl http://localhost:8000/api/tdx/health`
4. 重启后端: `cd web/backend && python -m uvicorn app.main:app --reload --port 8000`

### TDX连接失败
1. 检查服务器配置: `utils/tdx_server_config.py`
2. 测试TDX连接: `python test_tdx_mvp.py`
3. 查看后端日志中的TDX连接信息
4. 系统会自动尝试备用服务器 (共38个)

### API认证失败
1. 检查token是否过期 (默认30分钟)
2. 重新登录获取新token
3. 确保请求头包含: `Authorization: Bearer <token>`

## 版本历史

### v2.1 (2025-10-15)
- 新增TDX实时行情系统
- 完整的前后端集成
- 指数监控面板
- 多周期K线图表
- 端口配置规范化
- Bug修复和性能优化

### v1.0 (2025-09-01)
- 基础系统框架
- 用户认证系统
- 基本数据查询功能
- K线图表展示

## 相关文档
- [CHANGELOG v2.1](../CHANGELOG_v2.1.md) - 完整更新日志
- [TDX适配器文档](../adapters/README_TDX.md) - TDX技术细节
- [端口配置规则](./PORTS.md) - 端口使用规范
- [TDX部署文档](./TDX_SETUP_COMPLETE.md) - 部署完成报告
- [API测试脚本](../test_tdx_api.py) - API测试用例

## 技术支持
- 项目地址: /opt/claude/mystocks_spec
- 当前分支: 005-tdx-web-tdx
- 问题反馈: 请查看相关文档或检查日志文件
