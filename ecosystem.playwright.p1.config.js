module.exports = {
  "apps": [
    {
      "name": "p1-test-analysis",
      "script": "/root/miniconda3/envs/stock/bin/python",
      "args": "/tmp/test_analysis_playwright.py",
      "interpreter": "none",
      "cwd": "/opt/claude/mystocks_spec",
      "error_file": "/var/log/pm2/p1-analysis-error.log",
      "out_file": "/var/log/pm2/p1-analysis-out.log",
      "log_date_format": "YYYY-MM-DD HH:mm:ss Z",
      "merge_logs": true,
      "env": {
        "PYTHONUNBUFFERED": "1",
        "PLAYWRIGHT_BROWSERS_PATH": "/root/.cache/ms-playwright"
      },
      "autorestart": false,
      "max_memory_restart": "500M",
      "kill_timeout": 300000
    },
    {
      "name": "p1-test-industryconceptanalysis",
      "script": "/root/miniconda3/envs/stock/bin/python",
      "args": "/tmp/test_industryconceptanalysis_playwright.py",
      "interpreter": "none",
      "cwd": "/opt/claude/mystocks_spec",
      "error_file": "/var/log/pm2/p1-industryconceptanalysis-error.log",
      "out_file": "/var/log/pm2/p1-industryconceptanalysis-out.log",
      "log_date_format": "YYYY-MM-DD HH:mm:ss Z",
      "merge_logs": true,
      "env": {
        "PYTHONUNBUFFERED": "1",
        "PLAYWRIGHT_BROWSERS_PATH": "/root/.cache/ms-playwright"
      },
      "autorestart": false,
      "max_memory_restart": "500M",
      "kill_timeout": 300000
    },
    {
      "name": "p1-test-technicalanalysis",
      "script": "/root/miniconda3/envs/stock/bin/python",
      "args": "/tmp/test_technicalanalysis_playwright.py",
      "interpreter": "none",
      "cwd": "/opt/claude/mystocks_spec",
      "error_file": "/var/log/pm2/p1-technicalanalysis-error.log",
      "out_file": "/var/log/pm2/p1-technicalanalysis-out.log",
      "log_date_format": "YYYY-MM-DD HH:mm:ss Z",
      "merge_logs": true,
      "env": {
        "PYTHONUNBUFFERED": "1",
        "PLAYWRIGHT_BROWSERS_PATH": "/root/.cache/ms-playwright"
      },
      "autorestart": false,
      "max_memory_restart": "500M",
      "kill_timeout": 300000
    },
    {
      "name": "p1-test-indicatorlibrary",
      "script": "/root/miniconda3/envs/stock/bin/python",
      "args": "/tmp/test_indicatorlibrary_playwright.py",
      "interpreter": "none",
      "cwd": "/opt/claude/mystocks_spec",
      "error_file": "/var/log/pm2/p1-indicatorlibrary-error.log",
      "out_file": "/var/log/pm2/p1-indicatorlibrary-out.log",
      "log_date_format": "YYYY-MM-DD HH:mm:ss Z",
      "merge_logs": true,
      "env": {
        "PYTHONUNBUFFERED": "1",
        "PLAYWRIGHT_BROWSERS_PATH": "/root/.cache/ms-playwright"
      },
      "autorestart": false,
      "max_memory_restart": "500M",
      "kill_timeout": 300000
    },
    {
      "name": "p1-test-strategymanagement",
      "script": "/root/miniconda3/envs/stock/bin/python",
      "args": "/tmp/test_strategymanagement_playwright.py",
      "interpreter": "none",
      "cwd": "/opt/claude/mystocks_spec",
      "error_file": "/var/log/pm2/p1-strategymanagement-error.log",
      "out_file": "/var/log/pm2/p1-strategymanagement-out.log",
      "log_date_format": "YYYY-MM-DD HH:mm:ss Z",
      "merge_logs": true,
      "env": {
        "PYTHONUNBUFFERED": "1",
        "PLAYWRIGHT_BROWSERS_PATH": "/root/.cache/ms-playwright"
      },
      "autorestart": false,
      "max_memory_restart": "500M",
      "kill_timeout": 300000
    },
    {
      "name": "p1-test-backtestanalysis",
      "script": "/root/miniconda3/envs/stock/bin/python",
      "args": "/tmp/test_backtestanalysis_playwright.py",
      "interpreter": "none",
      "cwd": "/opt/claude/mystocks_spec",
      "error_file": "/var/log/pm2/p1-backtestanalysis-error.log",
      "out_file": "/var/log/pm2/p1-backtestanalysis-out.log",
      "log_date_format": "YYYY-MM-DD HH:mm:ss Z",
      "merge_logs": true,
      "env": {
        "PYTHONUNBUFFERED": "1",
        "PLAYWRIGHT_BROWSERS_PATH": "/root/.cache/ms-playwright"
      },
      "autorestart": false,
      "max_memory_restart": "500M",
      "kill_timeout": 300000
    },
    {
      "name": "p1-test-trademanagement",
      "script": "/root/miniconda3/envs/stock/bin/python",
      "args": "/tmp/test_trademanagement_playwright.py",
      "interpreter": "none",
      "cwd": "/opt/claude/mystocks_spec",
      "error_file": "/var/log/pm2/p1-trademanagement-error.log",
      "out_file": "/var/log/pm2/p1-trademanagement-out.log",
      "log_date_format": "YYYY-MM-DD HH:mm:ss Z",
      "merge_logs": true,
      "env": {
        "PYTHONUNBUFFERED": "1",
        "PLAYWRIGHT_BROWSERS_PATH": "/root/.cache/ms-playwright"
      },
      "autorestart": false,
      "max_memory_restart": "500M",
      "kill_timeout": 300000
    },
    {
      "name": "p1-test-taskmanagement",
      "script": "/root/miniconda3/envs/stock/bin/python",
      "args": "/tmp/test_taskmanagement_playwright.py",
      "interpreter": "none",
      "cwd": "/opt/claude/mystocks_spec",
      "error_file": "/var/log/pm2/p1-taskmanagement-error.log",
      "out_file": "/var/log/pm2/p1-taskmanagement-out.log",
      "log_date_format": "YYYY-MM-DD HH:mm:ss Z",
      "merge_logs": true,
      "env": {
        "PYTHONUNBUFFERED": "1",
        "PLAYWRIGHT_BROWSERS_PATH": "/root/.cache/ms-playwright"
      },
      "autorestart": false,
      "max_memory_restart": "500M",
      "kill_timeout": 300000
    },
    {
      "name": "p1-test-settings",
      "script": "/root/miniconda3/envs/stock/bin/python",
      "args": "/tmp/test_settings_playwright.py",
      "interpreter": "none",
      "cwd": "/opt/claude/mystocks_spec",
      "error_file": "/var/log/pm2/p1-settings-error.log",
      "out_file": "/var/log/pm2/p1-settings-out.log",
      "log_date_format": "YYYY-MM-DD HH:mm:ss Z",
      "merge_logs": true,
      "env": {
        "PYTHONUNBUFFERED": "1",
        "PLAYWRIGHT_BROWSERS_PATH": "/root/.cache/ms-playwright"
      },
      "autorestart": false,
      "max_memory_restart": "500M",
      "kill_timeout": 300000
    }
  ]
}