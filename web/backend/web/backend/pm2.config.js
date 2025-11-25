module.exports = {
  apps: [
    {
      name: "mystocks-backend",
      script: "/root/miniconda3/envs/stock/bin/uvicorn",
      args: "app.main:app --host 0.0.0.0 --port 8000",
      cwd: "/opt/claude/mystocks_spec/web/backend",
      instances: 1,
      max_restarts: 5,
      restart_delay: 2000,
      env: {
        USE_MOCK_DATA: "false",
        PYTHONPATH: ".",
        BACKEND_HOST: "0.0.0.0",
        BACKEND_PORT: "8000"
      },
      log_file: "/opt/claude/mystocks_spec/web/backend/logs/pm2.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",
      interpreter: "python"
    }
  ]
}
