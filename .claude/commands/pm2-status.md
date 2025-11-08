# PM2 Status - 查看 PM2 服务状态

查看所有 PM2 管理的服务状态、日志、资源占用。

## 显示信息

1. 所有服务列表和状态
2. CPU 和内存使用情况
3. 运行时长和重启次数
4. 最近的日志输出

## 使用示例

```bash
# 查看所有服务状态
/pm2-status

# 执行以下命令：
pm2 status
pm2 monit
pm2 logs --lines 50
```

与 PM2 integration hooks 配合使用，提供后端可观测性。
