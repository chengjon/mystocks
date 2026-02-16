module.exports = {
  apps: [
    {
      name: 'mystocks-backend',
      script: 'python3',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 8000',
      cwd: './web/backend',
      min_uptime: '10s',
      restart_delay: 5000,
      max_restarts: 10,
      env: {
        PYTHONPATH: '.', 
        VITE_APP_MODE: 'mock'
      }
    },
    {
      name: 'mystocks-frontend',
      script: 'npm',
      args: 'run dev',
      cwd: './web/frontend',
      env: {
        VITE_PORT: 3020, 
        PORT: 3020
      }
    }
  ]
};
