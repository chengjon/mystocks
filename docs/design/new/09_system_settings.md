# 09 系统配置中心 (System Settings)

## 1. 页面概览
**功能定位**: 系统的后台控制室。管理全局参数、数据源接入与用户权限。
**视觉焦点**: 规整的表单与参数项。

## 2. 布局结构 (Tabbed Layout)

页面采用纵向 Tabs 布局，分为以下模块：

### 2.1 基础设置 (General)
*   **内容**:
    *   **交易日历**: 同步交易所节假日安排。
    *   **UI偏好**: 主题切换 (ArtDeco/Minimal), 字体大小。
    *   **通知渠道**: 配置邮件 SMTP, 钉钉 Webhook。

### 2.2 数据源管理 (Data Sources)
*   **内容**:
    *   **源优先级**: 拖拽排序 (e.g., AKShare > Tushare > Baostock).
    *   **Token管理**: 输入 Tushare 等平台的 API Token.
    *   **连通性测试**: "Check Connection" 按钮。
*   **API**:
    *   `GET/POST /api/v1/data/config` (需实现)

### 2.3 用户与权限 (Users & Auth)
*   **内容**:
    *   **用户列表**: 用户名, 角色 (Admin/Trader/Viewer), 最后登录.
    *   **修改密码**: 重置密码功能。
*   **API**: `GET /api/v1/auth/users` (仅管理员可见)

### 2.4 系统日志 (System Logs)
*   **内容**:
    *   查看后端应用日志 (stdout/stderr)。
    *   支持按关键词搜索与日志级别过滤。
*   **API**: `GET /api/v1/system/logs`

## 3. 交互设计
*   **保存反馈**: 修改配置后，右上角弹出 Toast 提示 "保存成功"。
*   **敏感信息**: API Token 等字段默认掩码显示 (******)，点击小眼睛图标查看。

## 4. API 映射汇总
| 组件区域 | 核心 API 端点 | 请求方式 | 备注 |
| :--- | :--- | :--- | :--- |
| 用户信息 | `/api/v1/auth/me` | GET | |
| 登出 | `/api/v1/auth/logout` | POST | |
