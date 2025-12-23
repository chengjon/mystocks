# MyStocks项目tmux和lnav集成指南

## 概述

本文档介绍了如何在MyStocks项目中使用tmux和lnav来提升开发和监控效率。tmux用于会话管理，lnav用于日志分析。

## 目录结构

```
config/
├── tmux.conf                 # tmux配置文件
└── lnav/
    ├── mystocks_log.json     # MyStocks日志格式定义
    ├── mystocks_config.json  # lnav配置文件
    └── formats/
        └── mystocks_log.json # 日志格式定义

scripts/
├── dev/
│   └── tmux_session.sh       # tmux会话管理脚本
└── monitoring/
    └── mystocks_monitor.sh   # 系统监控一体化脚本
```

## tmux集成

### 1. 配置文件

`config/tmux.conf` 提供了为MyStocks项目优化的tmux配置：
- Vim风格的面板切换 (hjkl)
- 快速窗口和面板管理
- 状态栏显示系统信息
- 鼠标支持

### 2. 使用方法

#### 应用配置
```bash
# 复制配置文件到用户目录
cp config/tmux.conf ~/.tmux.conf

# 或者在当前会话中加载配置
tmux source-file config/tmux.conf
```

#### 启动开发会话
```bash
# 使用预设脚本启动开发会话
./scripts/dev/tmux_session.sh start

# 或者手动创建会话
./scripts/dev/tmux_session.sh start my_custom_session
```

#### 会话管理命令
```bash
# 列出所有会话
./scripts/dev/tmux_session.sh list

# 连接到会话
./scripts/dev/tmux_session.sh attach

# 关闭会话
./scripts/dev/tmux_session.sh kill
```

### 3. 会话布局

预设的MyStocks开发会话包含以下窗口和面板：

1. **databases窗口**: 数据库监控
   - 左侧面板: TDengine状态
   - 右侧面板: PostgreSQL状态

2. **services窗口**: 服务监控
   - 上方左侧面板: 后端服务
   - 上方右侧面板: 前端服务
   - 下方面板: GPU服务

3. **logs窗口**: 日志监控
   - lnav日志分析器

4. **dev窗口**: 开发环境
   - 开发和测试命令

### 4. 快捷键

在tmux会话中使用以下快捷键：

- `Ctrl+a` + `h/j/k/l`: 在面板间切换
- `Ctrl+a` + `|`: 垂直分割面板
- `Ctrl+a` + `-`: 水平分割面板
- `Ctrl+a` + `c`: 创建新窗口
- `Ctrl+a` + `n/p`: 切换窗口
- `Ctrl+a` + `[`: 进入复制模式
- `Ctrl+a` + `]`: 粘贴

## lnav集成

### 1. 日志格式支持

MyStocks项目使用loguru记录日志，包括标准格式和JSON格式。lnav配置文件支持这两种格式：

- **标准格式**: `2024-12-19 10:30:45.123 | INFO | module:function:123 - 消息`
- **JSON格式**: 结构化JSON日志

### 2. 使用方法

#### 基本日志查看
```bash
# 查看所有日志文件
./scripts/monitoring/mystocks_monitor.sh logs

# 或者直接使用lnav
lnav logs/
```

#### 高级查询
在lnav中可以使用以下查询：

1. **错误过滤**:
   ```
   :filter-in ERROR
   ```

2. **模块过滤**:
   ```
   :filter-in data_access
   ```

3. **时间过滤**:
   ```
   :filter-in 2024-12-19
   ```

4. **自定义查询**:
   ```
   :error_only
   :slow_operations
   :today_logs
   ```

### 3. 自定义视图

lnav配置中定义了以下视图：

- **Errors**: 仅显示错误和严重级别日志
- **Warnings**: 仅显示警告级别日志
- **Performance**: 显示性能相关日志

### 4. 颜色配置

日志级别使用不同颜色显示：
- ERROR: 红色
- WARNING: 黄色
- INFO: 绿色
- DEBUG: 蓝色

## 一体化监控脚本

`scripts/monitoring/mystocks_monitor.sh` 提供了完整的监控解决方案：

### 使用方法
```bash
# 启动监控会话
./scripts/monitoring/mystocks_monitor.sh start

# 查看日志统计
./scripts/monitoring/mystocks_monitor.sh stats

# 使用lnav分析日志
./scripts/monitoring/mystocks_monitor.sh logs

# 检查系统状态
./scripts/monitoring/mystocks_monitor.sh check
```

## 最佳实践

### 1. 开发工作流
1. 启动tmux会话: `./scripts/monitoring/mystocks_monitor.sh start`
2. 在不同面板中运行数据库、服务和监控
3. 使用lnav实时查看和分析日志

### 2. 问题排查
1. 使用lnav的过滤功能快速定位错误
2. 利用自定义查询分析特定类型的日志
3. 查看性能视图识别慢操作

### 3. 团队协作
1. 使用tmux会话共享功能进行结对编程
2. 统一使用相同的配置文件确保一致性
3. 通过脚本简化环境搭建过程

## 故障排除

### 1. tmux问题
- **问题**: 无法连接到会话
  **解决**: 检查会话是否存在 `tmux list-sessions`

- **问题**: 面板布局混乱
  **解决**: 重新加载配置 `tmux source-file ~/.tmux.conf`

### 2. lnav问题
- **问题**: 日志格式无法识别
  **解决**: 检查日志文件格式是否与配置匹配

- **问题**: 查询不返回结果
  **解决**: 检查查询语法和日志内容

## 扩展和定制

### 1. 定制tmux配置
编辑 `config/tmux.conf` 来满足个人偏好：
- 修改快捷键
- 调整状态栏显示
- 添加自定义脚本

### 2. 扩展lnav功能
在 `config/lnav/` 目录中添加：
- 新的日志格式定义
- 自定义查询和视图
- 脚本扩展功能

### 3. 集成到CI/CD
将监控脚本集成到自动化流程中：
- 部署时自动启动监控会话
- 定期分析日志并生成报告
- 设置告警机制
