# MyStocks Web端启动经验总结

**生成时间**: 2026-01-16
**适用场景**: MyStocks量化交易系统web端启动问题排查
**经验来源**: 实际启动过程遇到的问题分析与解决

---

## 📋 核心问题总结

### 1. **后端PYTHONPATH配置问题** 🔴 关键问题
**问题描述**: 后端应用启动失败，提示"No module named 'src'"
**根本原因**: PYTHONPATH环境变量未正确设置
**影响程度**: 🚫 阻塞性问题，无法启动后端服务

**解决方案**:
```bash
# ❌ 错误的启动方式
cd /opt/claude/mystocks_spec/web/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# ✅ 正确的启动方式
cd /opt/claude/mystocks_spec
PYTHONPATH=/opt/claude/mystocks_spec/web/backend:/opt/claude/mystocks_spec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**经验教训**:
- 后端依赖src目录下的模块，必须设置正确的PYTHONPATH
- 建议在启动脚本中固定设置PYTHONPATH，避免环境依赖
- 项目结构复杂时，优先使用项目根目录启动而不是子目录

### 2. **端口占用冲突问题** 🟡 常见问题
**问题描述**: 端口8000已被占用，导致后端启动失败
**根本原因**: 其他进程或之前的实例仍在运行
**影响程度**: 🚫 阻塞性问题，服务无法启动

**解决方案**:
```bash
# 1. 检查端口占用
lsof -i :8000

# 2. 杀死占用进程
kill -9 <PID>

# 3. 或者使用不同端口
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

**预防措施**:
- 启动前检查端口可用性
- 使用进程管理工具(PM2)自动管理端口
- 建立端口分配规范，避免冲突

### 3. **前端依赖安装问题** 🟡 配置问题
**问题描述**: 前端TypeScript类型生成失败
**根本原因**: node_modules未正确安装或版本不匹配
**影响程度**: ⚠️ 功能受限，类型检查失效

**解决方案**:
```bash
# 确保依赖正确安装
cd /opt/claude/mystocks_spec/web/frontend
rm -rf node_modules package-lock.json
npm install

# 验证安装
npm run type-check
```

**经验教训**:
- 前端依赖管理严格，版本冲突可能导致编译失败
- 建议定期清理node_modules重新安装
- 使用package-lock.json确保依赖版本一致性

### 4. **前端开发服务器稳定性问题** 🟢 轻微问题
**问题描述**: Vite开发服务器偶尔启动失败或响应慢
**根本原因**: 端口自动选择逻辑或系统资源限制
**影响程度**: ⚠️ 用户体验影响，开发效率降低

**解决方案**:
```bash
# 使用固定端口启动
npm run dev -- --port 3000

# 或者检查可用端口
npm run dev  # 自动选择3020-3029范围内的可用端口
```

**经验教训**:
- Vite自动端口选择有时不可靠
- 开发环境建议使用固定端口
- 生产环境使用反向代理处理端口

### 5. **CORS跨域配置问题** 🟠 中等问题
**问题描述**: 前端无法调用后端API，浏览器报CORS错误
**根本原因**: CORS配置不包含前端端口或格式错误
**影响程度**: 🚫 阻塞性问题，前后端无法通信

**解决方案**:
```python
# web/backend/app/core/config.py
cors_origins_str: str = (
    "http://localhost:3000,http://localhost:3001,"
    "http://localhost:3020,http://localhost:3021,"
    # ... 其他端口
)

# 确保配置正确应用
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**预防措施**:
- 维护完整的端口白名单
- 使用环境变量动态配置允许的源
- 开发环境放宽限制，生产环境严格控制

---

## 🔧 最佳实践总结

### **启动流程标准化**

#### 推荐的启动顺序
```bash
# 1. 检查系统状态
./scripts/check-system-health.sh

# 2. 启动数据库服务
docker-compose -f config/docker-compose.postgresql.yml up -d

# 3. 启动后端服务
cd /opt/claude/mystocks_spec
PYTHONPATH=/opt/claude/mystocks_spec/web/backend:/opt/claude/mystocks_spec \
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 4. 启动前端服务
cd web/frontend
npm run dev -- --port 3000
```

#### 启动脚本模板
```bash
#!/bin/bash
# scripts/start-web-services.sh

set -e

echo "🚀 Starting MyStocks Web Services..."

# 检查依赖
command -v python3 >/dev/null 2>&1 || { echo "❌ Python3 not found"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ npm not found"; exit 1; }

# 设置环境变量
export PYTHONPATH="/opt/claude/mystocks_spec/web/backend:/opt/claude/mystocks_spec"

# 检查端口
if lsof -i :8000 >/dev/null 2>&1; then
    echo "⚠️  Port 8000 is in use, attempting to free it..."
    fuser -k 8000/tcp || true
fi

# 启动后端
echo "📡 Starting backend service..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# 等待后端启动
sleep 5
if ! curl -s http://localhost:8000/health >/dev/null; then
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# 启动前端
echo "🌐 Starting frontend service..."
cd web/frontend
npm run dev -- --port 3000 &
FRONTEND_PID=$!

# 等待前端启动
sleep 10
if ! curl -s http://localhost:3000 >/dev/null; then
    echo "❌ Frontend failed to start"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 1
fi

echo "✅ All services started successfully!"
echo "📊 Backend: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/api/docs"

# 保存进程ID
echo "$BACKEND_PID $FRONTEND_PID" > .service_pids

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; rm -f .service_pids" EXIT
wait
```

### **监控和健康检查**

#### 服务健康检查脚本
```bash
#!/bin/bash
# scripts/health-check.sh

SERVICES=(
    "Backend API:http://localhost:8000/health"
    "Frontend App:http://localhost:3000"
    "API Docs:http://localhost:8000/api/docs"
)

echo "🔍 MyStocks Services Health Check"
echo "=================================="

for service in "${SERVICES[@]}"; do
    name=$(echo $service | cut -d: -f1)
    url=$(echo $service | cut -d: -f2-)

    if curl -s --max-time 5 "$url" >/dev/null; then
        echo "✅ $name: Healthy"
    else
        echo "❌ $name: Unhealthy ($url)"
    fi
done
```

### **故障排查指南**

#### 快速诊断清单
1. **端口检查**: `netstat -tlnp | grep -E ':(8000|3000)'`
2. **进程状态**: `ps aux | grep -E "(uvicorn|vite)"`
3. **日志查看**: `tail -f web/backend/*.log` 或 `tail -f web/frontend/*.log`
4. **网络连通**: `curl -I http://localhost:8000/health`
5. **依赖检查**: `python -c "import app.main"` 和 `npm list --depth=0`

#### 常见错误码处理
- **500 Internal Server Error**: 检查后端日志，可能是数据库连接或业务逻辑错误
- **404 Not Found**: 检查API路径是否正确，确认路由配置
- **CORS Error**: 检查CORS配置，确认前端端口在白名单中
- **Timeout**: 检查数据库连接或外部API调用超时

---

## 📊 性能优化建议

### **启动时间优化**
- 使用PM2管理进程，提供自动重启和日志轮转
- 前端预构建依赖，减少冷启动时间
- 使用多阶段构建，优化Docker镜像大小

### **运行时性能**
- 启用Gzip压缩减少网络传输
- 配置适当的缓存策略
- 监控内存使用，及时释放资源

### **开发体验优化**
- 配置热重载，提高开发效率
- 使用ESLint和Prettier保持代码质量
- 集成浏览器开发工具，方便调试

---

## 🎯 预防措施清单

### **环境配置**
- [ ] 确保PYTHONPATH正确设置
- [ ] 验证Node.js和npm版本兼容性
- [ ] 检查系统端口可用性
- [ ] 确认数据库服务正常运行

### **依赖管理**
- [ ] 定期更新package.json和requirements.txt
- [ ] 使用lock文件确保版本一致性
- [ ] 定期清理node_modules和Python缓存
- [ ] 检查依赖安全漏洞

### **监控告警**
- [ ] 设置服务健康检查告警
- [ ] 监控API响应时间和错误率
- [ ] 跟踪资源使用情况
- [ ] 建立故障自动恢复机制

---

## 📝 版本信息

| 组件 | 版本 | 状态 | 最后测试 |
|------|------|------|----------|
| **后端** | FastAPI 0.109+ | ✅ 正常 | 2026-01-16 |
| **前端** | Vue 3.4 + Vite | ✅ 正常 | 2026-01-16 |
| **数据库** | PostgreSQL 17.x | ✅ 正常 | 2026-01-16 |
| **Python** | 3.12+ | ✅ 兼容 | 2026-01-16 |
| **Node.js** | 16+ | ✅ 兼容 | 2026-01-16 |

---

**总结**: 通过本次启动过程，我们成功解决了PYTHONPATH配置、端口冲突、依赖管理等关键问题，建立了完整的web端启动和维护流程。建议将这些经验教训纳入项目文档，减少未来类似问题的发生。

**文档维护**: Claude Code AI
**最后更新**: 2026-01-16