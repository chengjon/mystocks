#!/bin/bash

###############################################################################
# MyStocks Frontend - PM2 Stop Script
# Phase 3: Bloomberg Terminal Style Deployment
#
# Usage:
#   ./stop.sh [options]
#
# Options:
#   --delete     Remove PM2 process completely (not just stop)
#   --logs       Show logs before stopping
###############################################################################

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="mystocks-frontend"
DELETE_FLAG=false
SHOW_LOGS=false

# Parse arguments
while [[ "$#" -gt 0 ]]; do
  case $1 in
    --delete) DELETE_FLAG=true ;;
    --logs) SHOW_LOGS=true ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      echo "Usage: $0 [--delete] [--logs]"
      exit 1
      ;;
  esac
  shift
done

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   MyStocks Frontend - PM2 Stop Script                     ║${NC}"
echo -e "${BLUE}║   Phase 3: Bloomberg Terminal Style Verification          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if PM2 is running
if ! command -v pm2 &> /dev/null; then
  echo -e "${RED}✗ PM2 is not installed${NC}"
  exit 1
fi

# Show logs if requested
if [ "$SHOW_LOGS" = true ]; then
  echo -e "${YELLOW}Showing recent logs...${NC}"
  pm2 logs $APP_NAME --lines 50 --nostream
  echo ""
fi

# Check if app is running
if ! pm2 list | grep -q "$APP_NAME.*online"; then
  echo -e "${YELLOW}⚠ $APP_NAME is not running${NC}"

  if [ "$DELETE_FLAG" = true ]; then
    if pm2 list | grep -q "$APP_NAME.*stopped"; then
      echo -e "${YELLOW}Removing stopped process...${NC}"
      pm2 delete $APP_NAME
      pm2 save
      echo -e "${GREEN}✓ Process removed${NC}"
    fi
  fi

  echo -e "${YELLOW}No action taken${NC}"
  exit 0
fi

echo -e "${YELLOW}Stopping $APP_NAME...${NC}"

# Stop the application
pm2 stop $APP_NAME

# Wait a moment
sleep 1

# Check if stopped
if pm2 list | grep -q "$APP_NAME.*stopped"; then
  echo -e "${GREEN}✓ Application stopped${NC}"

  # Delete if requested
  if [ "$DELETE_FLAG" = true ]; then
    echo -e "${YELLOW}Removing process from PM2...${NC}"
    pm2 delete $APP_NAME
    pm2 save
    echo -e "${GREEN}✓ Process removed${NC}"
  else
    pm2 save
  fi

  echo ""
  echo -e "${BLUE}Current PM2 status:${NC}"
  pm2 list
else
  echo -e "${RED}✗ Failed to stop application${NC}"
  echo -e "${YELLOW}Try: pm2 stop $APP_NAME --force${NC}"
  exit 1
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✓ MyStocks Frontend stopped successfully                 ║${NC}"
echo -e "${GREEN}║                                                             ║${NC}"
echo -e "${GREEN}║  Restart: ./start.sh                                       ║${NC}"
echo -e "${GREEN}║  PM2:     pm2 list                                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
