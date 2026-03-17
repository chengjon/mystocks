# MyStocks 量化交易平台

**完整的全栈量化交易系统** - 集成前端、后端、数据库和监控的完整解决方案

## 🚀 快速开始

### 一键启动（推荐）
```bash
# 克隆项目（如果还没有）
git clone <repository-url>
cd mystocks-spec

# 一键启动所有服务
./run_platform.sh
```

启动成功后访问：
- 🌐 **前端界面**: http://localhost:3000
- 🔧 **后端API**: http://localhost:8000
- 📖 **API文档**: http://localhost:8000/docs

### 手动启动

#### 1. 启动数据库
```bash
# 使用Docker启动TDengine
docker run -d \
  --name mystocks-tdengine \
  -p 6030:6030 \
  -p 6041:6041 \
  tdengine/tdengine:3.0.4.0

# 或使用本地安装的TDengine
sudo systemctl start taosd
```

#### 2. 启动后端
```bash
cd web/backend

# 创建虚拟环境（如果还没有）
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 启动FastAPI服务器
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. 启动前端
```bash
cd web/frontend

# 安装依赖（如果还没有）
npm install

# 启动开发服务器
npm run dev -- --port 3000
```

## 📋 系统架构

### 技术栈
- **前端**: Vue 3 + TypeScript + Element Plus + ArtDeco 组件库
- **后端**: FastAPI + Python 3.12 + Uvicorn
- **数据库**: TDengine (时序数据) + PostgreSQL (结构化数据)
- **缓存**: Redis (可选)
- **监控**: Prometheus + Grafana

### 核心功能模块

#### 🎯 ArtDeco 设计系统
- 9个精心设计的Art Deco风格页面
- 52个专业组件库
- 金色装饰主题，A股配色标准
- 响应式桌面优先设计

#### 📊 量化交易功能
- **Dashboard**: 实时市场概览和资金流向
- **Market Data**: 多维度市场数据分析
- **Market Quotes**: Level 2十档报价和K线图表
- **Trading Management**: 交易信号和订单管理
- **Data Analysis**: 技术指标和筛选条件
- **Backtest**: 策略回测和参数优化
- **Risk Management**: 风险评估和监控
- **Stock Management**: 自选股池管理
- **Settings**: 系统配置和个性化

#### 🔧 API 生态系统
- 469个REST API端点
- JWT认证和权限管理
- 实时WebSocket支持
- 统一的响应格式
- 完整的错误处理

## 🎨 ArtDeco 设计特色

### 视觉设计理念
- **Art Deco美学**: 几何装饰，金色强调，奢华感
- **金融专业性**: A股红涨绿跌配色标准
- **现代化交互**: 平滑动画，戏剧性过渡

### 组件库特性
- **52个专业组件**: 基础、专用、高级、核心四大类
- **类型安全**: 完整的TypeScript支持
- **主题一致性**: 统一的设计语言和交互模式
- **性能优化**: 懒加载和组件缓存

## 🔧 配置说明

### 环境变量

#### 前端配置 (`web/frontend/.env.development`)
```bash
# API配置
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=10000
VITE_API_RETRY_ATTEMPTS=3

# 应用配置
VITE_APP_ENV=development
VITE_APP_TITLE=MyStocks Development
VITE_DEBUG=true
VITE_LOG_LEVEL=debug
```

#### 后端配置 (`web/backend/.env`)
```bash
# 数据库配置
DATABASE_URL=taos://root:your-tdengine-password@localhost:6030/mystocks

# 应用配置
DEBUG=true
SECRET_KEY=your-secret-key-here

# CORS配置（已内置）
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,...
```

### 端口分配
| 服务 | 端口范围 | 默认端口 | 用途 |
|------|----------|----------|------|
| 前端 | 3000-3009 | 3000 | Vue开发服务器 |
| 后端 | 8000-8009 | 8000 | FastAPI服务器 |
| TDengine | 6030, 6041 | 6030 | 时序数据库 |
| PostgreSQL | 5432 | 5432 | 关系数据库 |
| Redis | 6379 | 6379 | 缓存服务 |

## 📖 使用指南

### 页面导航

平台包含9个主要功能页面：

1. **首页 (/)**
   - MyStocks指挥中心
   - 实时市场概览和资金流向

2. **市场数据 (/artdeco/market)**
   - 资金流向分析
   - ETF数据表
   - 概念板块追踪
   - 龙虎榜数据

3. **行情报价 (/artdeco/market-quotes)**
   - 十档Level 2报价
   - 实时K线图表
   - 技术指标分析
   - 成交明细

4. **量化交易 (/artdeco/trading)**
   - 交易信号监控
   - 订单管理
   - 持仓分析
   - 收益归因

5. **数据分析 (/artdeco/analysis)**
   - 技术指标选择器
   - 股票筛选条件
   - 对比分析
   - 自定义公式

6. **策略回测 (/artdeco/backtest)**
   - 模块化策略构建
   - 回测配置
   - GPU加速计算
   - 参数优化

7. **风险管理 (/artdeco/risk)**
   - 风险评估仪表盘
   - VaR分析
   - 风险指标监控

8. **股票管理 (/artdeco/stock-management)**
   - 自选股池管理
   - 股票搜索和筛选
   - 实时行情监控

9. **系统设置 (/artdeco/settings)**
   - 数据源配置
   - 主题设置
   - 通知管理

### API 使用

#### 认证流程
```bash
# 1. 获取CSRF token
GET /api/auth/csrf-token

# 2. 用户登录
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded
X-CSRF-Token: <csrf-token>

username=admin&password=your-password

# 3. 使用JWT token调用API
GET /api/market/realtime/600519
Authorization: Bearer <jwt-token>
```

#### 核心API端点

**市场数据**:
- `GET /api/market/realtime/{symbol}` - 实时行情
- `GET /api/market/kline` - K线数据
- `GET /api/market/fund-flow` - 资金流向

**交易管理**:
- `GET /api/trading/signals` - 交易信号
- `POST /api/trading/orders` - 下单
- `GET /api/trading/positions` - 持仓查询

**策略回测**:
- `POST /api/backtest/run` - 执行回测
- `GET /api/backtest/results/{id}` - 获取结果

## 🔍 故障排除

### 常见问题

#### 端口冲突
```bash
# 检查端口占用
lsof -i :3000
lsof -i :8000

# 杀死进程
kill -9 <PID>

# 或使用自定义端口
BACKEND_PORT=8001 FRONTEND_PORT=3001 ./run_platform.sh
```

#### 数据库连接失败
```bash
# 检查TDengine状态
sudo systemctl status taosd

# 检查容器状态
docker ps | grep tdengine

# 查看数据库日志
docker logs mystocks-tdengine
```

#### 前端构建失败
```bash
cd web/frontend

# 清理缓存
rm -rf node_modules package-lock.json
npm install

# 检查环境变量
cat .env.development
```

#### API调用失败
```bash
# 检查后端健康状态
curl http://localhost:8000/health

# 查看后端日志
tail -f web/backend/backend.log

# 检查CORS配置
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS http://localhost:8000/api/market/realtime/600519
```

### 日志位置
- **后端日志**: `web/backend/backend.log`
- **前端日志**: `web/frontend/frontend.log`
- **数据库日志**: `/var/log/taos/` 或 `docker logs mystocks-tdengine`

## 📊 性能监控

### 指标监控
- **API响应时间**: < 300ms (目标)
- **页面加载时间**: < 3秒 (目标)
- **内存使用**: < 2GB (总计)
- **数据库查询**: < 100ms (平均)

### 健康检查
```bash
# 平台整体健康检查
curl http://localhost:8000/health

# 数据库连接检查
curl "http://localhost:6030/rest/sql" \
  -H "Authorization: Basic cm9vdDp0YW9zZGF0YQ==" \
  -d "sql=show databases"

# 前端可用性检查
curl -s http://localhost:3000 | grep -q "MyStocks" && echo "Frontend OK"
```

## 🔐 安全说明

### 认证安全
- JWT token自动过期和刷新
- CSRF保护所有POST请求
- 密码加密存储
- 会话管理

### API安全
- 请求频率限制
- 输入验证和清理
- SQL注入防护
- XSS防护

### 数据安全
- 敏感数据加密
- 安全的数据库连接
- 日志脱敏处理

## 🛠️ 开发指南

### 项目结构
```
mystocks-spec/
├── web/
│   ├── frontend/          # Vue前端应用
│   │   ├── src/
│   │   │   ├── views/artdeco-pages/  # 9个ArtDeco页面
│   │   │   ├── components/artdeco/   # 52个组件库
│   │   │   ├── api/                  # API客户端
│   │   │   └── router/               # 路由配置
│   └── backend/          # FastAPI后端应用
│       ├── app/
│       │   ├── api/                  # 469个API端点
│       │   ├── core/                 # 配置和中间件
│       │   └── services/             # 业务逻辑
│       └── requirements.txt
├── run_platform.sh       # 一键启动脚本
└── README.md            # 本文档
```

### 开发环境设置
```bash
# 1. 安装Python依赖
cd web/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. 安装Node.js依赖
cd ../frontend
npm install

# 3. 配置环境变量
cp .env.example .env.development
# 编辑环境变量...

# 4. 启动开发环境
./run_platform.sh
```

## 📈 路线图

### 已完成功能 ✅
- [x] ArtDeco设计系统 (52组件，9页面)
- [x] 完整API生态 (469端点)
- [x] 双数据库架构 (TDengine + PostgreSQL)
- [x] 全栈集成脚本
- [x] 实时数据处理
- [x] 量化交易算法

### 进行中功能 🚧
- [ ] 生产环境部署优化
- [ ] 性能监控仪表盘
- [ ] 用户权限管理系统

### 计划功能 📋
- [ ] 移动端适配
- [ ] AI策略推荐
- [ ] 多市场数据源
- [ ] 高级风险模型

## 🤝 贡献指南

### 代码规范
- **前端**: ESLint + Prettier, TypeScript严格模式
- **后端**: Black格式化, mypy类型检查, pytest测试
- **提交**: 清晰的commit消息，遵循Conventional Commits

### 测试要求
- **单元测试**: > 80% 覆盖率
- **集成测试**: 所有API端点
- **E2E测试**: 关键用户流程

## 📞 支持与反馈

### 问题反馈
1. 检查[故障排除](#故障排除)部分
2. 查看[API文档](http://localhost:8000/docs)
3. 提交Issue到项目仓库

### 社区资源
- 📖 [详细文档](./docs/)
- 🎯 [API参考](./docs/api/)
- 🔧 [开发指南](./docs/guides/)

---

**🎉 欢迎使用MyStocks量化交易平台！**

**启动命令**: `./run_platform.sh`

**访问地址**:
- 前端: http://localhost:3000
- API: http://localhost:8000
- 文档: http://localhost:8000/docs