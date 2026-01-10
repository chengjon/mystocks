#!/bin/bash
# Quick fix: Restart frontend service and provide access URLs
# 快速修复: 重启前端服务并提供访问URL

echo "🔄 Restarting MyStocks frontend service..."
echo ""

# Stop existing service
pkill -f "vite.*3020" 2>/dev/null
sleep 2

# Start new service
cd /opt/claude/mystocks_spec/web/frontend
nohup npm run dev -- --port 3020 --host 0.0.0.0 > /tmp/frontend-dev.log 2>&1 &
NEW_PID=$!
echo $NEW_PID > /tmp/frontend.pid

# Wait for service to start
sleep 3

# Check if service is running
if lsof -i :3020 > /dev/null 2>&1; then
    echo "✅ Frontend service started successfully!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🌐 Access URLs (try these in order):"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "1️⃣  BEST (Windows Browser):"
    echo "   http://localhost:3020"
    echo ""
    echo "2️⃣  Alternative:"
    echo "   http://127.0.0.1:3020"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 Service Status:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "   PID: $NEW_PID"
    echo "   Port: 3020"
    echo "   Host: 0.0.0.0 (all interfaces)"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "💡 Tips:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "• Hard refresh: Ctrl+Shift+R (Windows/Linux)"
    echo "• Clear cache: F12 → Right-click refresh → Empty Cache"
    echo "• View logs: tail -f /tmp/frontend-dev.log"
    echo ""
    echo "✨ Professional UI improvements active:"
    echo "   • OLED-optimized dark theme"
    echo "   • IBM Plex Sans + Fira Code fonts"
    echo "   • Data-dense layout (6px spacing)"
    echo "   • Bloomberg-level professional design"
    echo ""
else
    echo "❌ Failed to start service. Check logs:"
    echo "   tail -20 /tmp/frontend-dev.log"
    exit 1
fi
