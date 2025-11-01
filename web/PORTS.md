# MyStocks Web 端口配置规则

**创建人**: Claude
**版本**: 2.1.0
**批准日期**: 2025-10-15
**最后修订**: 2025-10-16
**本次修订内容**: 端口配置说明

---

## 端口分配标准

### 前端服务 (Vite)
- **主端口**: 3000
- **备用端口**: 3001
- **配置文件**: `web/frontend/vite.config.js`

### 后端服务 (FastAPI)
- **固定端口**: 8000
- **配置文件**: `web/backend/app/main.py`

## 规则

1. **前端必须使用端口3000**,如果3000被占用则使用3001
2. **后端必须使用端口8000**
3. **禁止随意更改端口**
4. **启动服务前必须检查端口占用情况**
5. **如果端口被占用,先停止占用进程,而不是换端口**

## 访问地址

- 前端: http://localhost:3000
- 后端: http://localhost:8000
- API文档: http://localhost:8000/api/docs

## 启动命令

```bash
# 后端
cd web/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端
cd web/frontend
npm run dev
```

## 端口冲突处理

如果端口被占用:

```bash
# 查找占用进程
lsof -i :3000
lsof -i :8000

# 停止进程
kill -9 <PID>
```
