module.exports = {
  apps: [
    {
      name: 'mystocks-backend',
      script: 'python3',
      args: `-m uvicorn app.main:app --host 0.0.0.0 --port ${process.env.BACKEND_PORT || 8000}`,
      cwd: './web/backend',
      min_uptime: '10s',
      restart_delay: 5000,
      max_restarts: 10,
      env: {
        PYTHONPATH: '/opt/claude/mystocks_spec/web/backend', 
        VITE_APP_MODE: 'mock',
        PORT: process.env.BACKEND_PORT || 8000
      }
    },
    {
      name: 'mystocks-frontend',
      script: 'npm',
      args: `run dev -- --port ${process.env.FRONTEND_PORT || 3020} --host 0.0.0.0 --strictPort`,
      cwd: './web/frontend',
      env: {
        FRONTEND_PORT: process.env.FRONTEND_PORT || 3020,
        VITE_PORT: process.env.FRONTEND_PORT || 3020, 
        PORT: process.env.FRONTEND_PORT || 3020
      }
    }
  ]
};
