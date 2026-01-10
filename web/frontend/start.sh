#!/bin/bash

###############################################################################
# MyStocks Frontend - PM2 Start Script
# Phase 3: Bloomberg Terminal Style Deployment
#
# Usage:
#   ./start.sh [options]
#
# Options:
#   --no-build   Skip build step (use existing dist)
#   --dev        Start in development mode (npm run dev)
#   --verbose    Enable verbose logging
###############################################################################

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
APP_NAME="mystocks-frontend"
PORT=8080
LOG_DIR="$SCRIPT_DIR/logs"
BUILD_FLAG=true

# Parse arguments
while [[ "$#" -gt 0 ]]; do
  case $1 in
    --no-build) BUILD_FLAG=false ;;
    --dev)
      echo -e "${YELLOW}Starting in development mode...${NC}"
      npm run dev
      exit 0
      ;;
    --verbose) set -x ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      echo "Usage: $0 [--no-build] [--dev] [--verbose]"
      exit 1
      ;;
  esac
  shift
done

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   MyStocks Frontend - PM2 Deployment Start Script        ║${NC}"
echo -e "${BLUE}║   Phase 3: Bloomberg Terminal Style Verification          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Check prerequisites
echo -e "${YELLOW}[1/6] Checking prerequisites...${NC}"

# Check Node.js version
if ! command -v node &> /dev/null; then
  echo -e "${RED}✗ Node.js is not installed${NC}"
  exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
  echo -e "${RED}✗ Node.js version must be 16 or higher (current: $(node -v))${NC}"
  exit 1
fi
echo -e "${GREEN}✓ Node.js $(node -v)${NC}"

# Check npm
if ! command -v npm &> /dev/null; then
  echo -e "${RED}✗ npm is not installed${NC}"
  exit 1
fi
echo -e "${GREEN}✓ npm $(npm -v)${NC}"

# Check pm2
if ! command -v pm2 &> /dev/null; then
  echo -e "${YELLOW}⚠ PM2 not found, installing...${NC}"
  npm install -g pm2
fi
echo -e "${GREEN}✓ PM2 $(pm2 -v)${NC}"

# Check if serve is installed
if ! npm list -g serve &> /dev/null; then
  echo -e "${YELLOW}⚠ serve not found, installing...${NC}"
  npm install -g serve
fi
echo -e "${GREEN}✓ serve installed${NC}"

echo ""

# Step 2: Install dependencies
echo -e "${YELLOW}[2/6] Installing dependencies...${NC}"
if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules" ]; then
  npm ci
  echo -e "${GREEN}✓ Dependencies installed${NC}"
else
  echo -e "${GREEN}✓ Dependencies already up to date${NC}"
fi
echo ""

# Step 3: Build project
if [ "$BUILD_FLAG" = true ]; then
  echo -e "${YELLOW}[3/6] Building project...${NC}"

  # Check if dist exists
  if [ -d "dist" ]; then
    echo -e "${YELLOW}⚠ Removing old dist directory...${NC}"
    rm -rf dist
  fi

  # Build
  npm run build

  if [ ! -d "dist" ]; then
    echo -e "${RED}✗ Build failed: dist directory not created${NC}"
    exit 1
  fi

  echo -e "${GREEN}✓ Build completed${NC}"
else
  echo -e "${YELLOW}[3/6] Skipping build (using existing dist)...${NC}"
  if [ ! -d "dist" ]; then
    echo -e "${RED}✗ dist directory not found. Run without --no-build first.${NC}"
    exit 1
  fi
fi
echo ""

# Step 4: Create logs directory
echo -e "${YELLOW}[4/6] Setting up logging...${NC}"
mkdir -p "$LOG_DIR"
echo -e "${GREEN}✓ Logs directory created: $LOG_DIR${NC}"
echo ""

# Step 5: Check if port is available
echo -e "${YELLOW}[5/6] Checking port $PORT...${NC}"
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
  echo -e "${YELLOW}⚠ Port $PORT is already in use${NC}"

  # Check if it's our app
  if pm2 list | grep -q "$APP_NAME.*online"; then
    echo -e "${YELLOW}⚠ $APP_NAME is already running. Restarting...${NC}"
    pm2 reload ecosystem.config.js --env production
    echo -e "${GREEN}✓ Application reloaded${NC}"
    echo ""
    echo -e "${BLUE}[6/6] Showing logs (Ctrl+C to exit)...${NC}"
    pm2 logs $APP_NAME --lines 50
    exit 0
  else
    echo -e "${RED}✗ Port $PORT is occupied by another process${NC}"
    echo -e "${YELLOW}Run: lsof -i :$PORT to see what's using it${NC}"
    exit 1
  fi
fi
echo -e "${GREEN}✓ Port $PORT is available${NC}"
echo ""

# Step 6: Start application
echo -e "${YELLOW}[6/6] Starting application with PM2...${NC}"

# Stop existing instances (if any)
if pm2 list | grep -q "$APP_NAME.*online\|stopped"; then
  echo -e "${YELLOW}⚠ Stopping existing instance...${NC}"
  pm2 stop $APP_NAME 2>/dev/null || true
  pm2 delete $APP_NAME 2>/dev/null || true
fi

# Start with PM2
pm2 start ecosystem.config.js --env production

# Wait for startup
sleep 3

# Check status
if pm2 list | grep -q "$APP_NAME.*online"; then
  echo -e "${GREEN}✓ Application started successfully${NC}"
  echo ""

  # Save PM2 process list
  pm2 save

  # Show status
  echo -e "${BLUE}Application Status:${NC}"
  pm2 list | grep "$APP_NAME"
  echo ""

  # Show logs
  echo -e "${BLUE}Recent logs (Ctrl+C to exit):${NC}"
  pm2 logs $APP_NAME --lines 30 --nostream
else
  echo -e "${RED}✗ Application failed to start${NC}"
  echo -e "${YELLOW}Check logs: pm2 logs $APP_NAME${NC}"
  exit 1
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  🎉 MyStocks Frontend started successfully!                ║${NC}"
echo -e "${GREEN}║                                                             ║${NC}"
echo -e "${GREEN}║  Access: http://localhost:$PORT                           ║${NC}"
echo -e "${GREEN}║  PM2:    pm2 list                                          ║${NC}"
echo -e "${GREEN}║  Logs:   pm2 logs $APP_NAME                               ║${NC}"
echo -e "${GREEN}║  Stop:   ./stop.sh                                         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
