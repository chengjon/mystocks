# Port Configuration Guide

## Overview

This project supports flexible port configuration for both frontend and backend services, allowing easy switching between different port ranges without code changes.

## Port Allocation

### Frontend Ports: 3000-3009
- **Primary port**: 3000
- **Range**: 3000-3009 (10 ports available)
- **Usage**: Vue.js development server

### Backend Ports: 8000-8009
- **Primary port**: 8000
- **Range**: 8000-8009 (10 ports available)
- **Usage**: FastAPI server

## Configuration Methods

### 1. Using the Port Configuration Script (Recommended)

```bash
# Set custom ports (e.g., frontend 3001, backend 8001)
./set-ports.sh 3001 8001

# Set only frontend port (backend uses default 8000)
./set-ports.sh 3005

# Show help
./set-ports.sh --help
```

### 2. Manual Configuration via .env

Edit the `.env` file in the project root:

```bash
# Frontend configuration
FRONTEND_PORT_RANGE_START=3000
FRONTEND_PORT_RANGE_END=3009

# Backend configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_PORT_RANGE_START=8000
BACKEND_PORT_RANGE_END=8009

# API configuration
VITE_API_BASE_URL=http://localhost:8000

# CORS origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:3002
```

### 3. Environment Variables

You can also set environment variables when starting services:

```bash
# Frontend
FRONTEND_PORT=3003 npm run dev

# Backend
BACKEND_PORT=8003 python -m uvicorn app.main:app --host 0.0.0.0 --port 8003
```

## Starting Services

### Development Mode

```bash
# Terminal 1: Backend
cd /opt/claude/mystocks_spec
python -m uvicorn web.backend.app.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd /opt/claude/mystocks_spec/web/frontend
npm run dev -- --port 3000
```

### Using Make (if configured)

```bash
make start-frontend  # Starts frontend on configured port
make start-backend    # Starts backend on configured port
```

## Testing Configuration

### Playwright Tests

Playwright automatically uses the configured frontend port:

```bash
cd /opt/claude/mystocks_spec/web/frontend
npx playwright test  # Uses port from .env or environment variables
```

You can override for testing:

```bash
FRONTEND_PORT=3002 npx playwright test
```

### Health Checks

Check if services are running:

```bash
# Backend health
curl http://localhost:8000/health

# Frontend access
curl http://localhost:3000
```

## Data Source Configuration

The project supports three data modes, configured via environment variables:

### Real Data Mode (Current)
```bash
USE_MOCK_DATA=false
REAL_DATA_AVAILABLE=true
```

### Mock Data Mode
```bash
USE_MOCK_DATA=true
REAL_DATA_AVAILABLE=false
```

### Hybrid Mode (Fallback)
```bash
USE_MOCK_DATA=false
REAL_DATA_AVAILABLE=true
# Backend will fallback to mock data if real data fails
```

Check current data mode:
```bash
curl http://localhost:8000/api/data-quality/config/mode | jq .
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :3000

# Kill process
kill -9 <PID>

# Or use the port configuration script which handles this automatically
```

### CORS Issues

When changing ports, ensure the new frontend port is in the CORS origins list:

```bash
# Update CORS_ORIGINS to include all frontend ports you use
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:3002
```

### Environment Variables Not Loading

1. Ensure `.env` file exists in project root
2. Check that `python-dotenv` is installed in backend
3. For frontend, restart the dev server after changing .env

## Best Practices

1. **Use the port configuration script** - It handles all necessary updates
2. **Check port availability** - The script warns if ports are in use
3. **Keep ports in range** - Stay within 3000-3009 (frontend) and 8000-8009 (backend)
4. **Document custom ports** - Note any custom port assignments for your team
5. **Use consistent ports** - Once you pick ports for a project, stick with them

## Examples

### Setting up a Development Instance on Different Ports

```bash
# Quick setup for a new development instance
./set-ports.sh 3005 8005

# Start services
cd /opt/claude/mystocks_spec
python -m uvicorn web.backend.app.main:app --host 0.0.0.0 --port 8005 &
cd /opt/claude/mystocks_spec/web/frontend
npm run dev -- --port 3005 &

# Access
# Frontend: http://localhost:3005
# Backend API: http://localhost:8005
# API Docs: http://localhost:8005/docs
```

### Running Multiple Instances

```bash
# Instance 1
./set-ports.sh 3000 8000

# Instance 2 (in another terminal)
FRONTEND_PORT_RANGE_START=3001 BACKEND_PORT=8001 ./start-services.sh
```

## Related Files

- `/opt/claude/mystocks_spec/.env` - Main configuration file
- `/opt/claude/mystocks_spec/set-ports.sh` - Port configuration script
- `/opt/claude/mystocks_spec/web/frontend/vite.config.js` - Frontend Vite configuration
- `/opt/claude/mystocks_spec/web/frontend/playwright.config.js` - Playwright test configuration
- `/opt/claude/mystocks_spec/web/backend/app/core/config.py` - Backend configuration settings
