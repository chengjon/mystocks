# Chrome DevTools MCP Integration Guide

**Version**: v2.0 (Concise Edition)
**Last Updated**: 2026-01-27
**Purpose**: Quick reference for Chrome DevTools MCP usage with OpenCode/Claude Code

---

## Quick Start (Working Solutions)

### Option 1: Direct HTTP API (Recommended)

Chrome DevTools MCP server is running on port 9222. Use HTTP API directly:

```bash
# Check Chrome status
curl -s http://localhost:9222/json

# Create new tab
PAGE_ID=$(curl -s -X PUT http://localhost:9222/json/new | python3 -c "import sys, json; print(json.loads(sys.stdin.read())['id'])")
echo "Tab ID: $PAGE_ID"

# Navigate to URL
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"id":1,"method":"Page.navigate","params":{"url":"http://localhost:3000"}}' \
  http://localhost:9222/devtools/page/$PAGE_ID

# Take screenshot
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"id":2,"method":"Page.captureScreenshot"}' \
  http://localhost:9222/devtools/page/$PAGE_ID > /tmp/screenshot.png

# Close tab
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"id":3,"method":"Page.close"}' \
  http://localhost:9222/devtools/page/$PAGE_ID
```

### Option 2: Playwright MCP (Alternative)

If Playwright MCP is loaded:

```bash
# Navigate
claude mcp playwright navigate -m "http://localhost:3000"

# Click element
claude mcp playwright click -m "Login Button" -e "selector=.login-button"
```

---

## Essential Commands Reference

### Basic Operations

| Task | Command |
|------|---------|
| List pages | `curl -s http://localhost:9222/json` |
| Create tab | `curl -s -X PUT http://localhost:9222/json/new` |
| Navigate | See Quick Start above |
| Screenshot | See Quick Start above |
| Close tab | See Quick Start above |
| Get page HTML | `curl -s http://localhost:9222/devtools/page/$PAGE_ID/content` |

### MyStocks Testing Example

```bash
#!/bin/bash
# Test MyStocks frontend

# 1. Check frontend is running
if ! lsof -i :3000 > /dev/null 2>&1; then
  echo "❌ Frontend not running. Start with:"
  echo "   cd /opt/claude/mystocks_spec/web/frontend && npm run dev"
  exit 1
fi

# 2. Create tab and navigate
PAGE_ID=$(curl -s -X PUT http://localhost:9222/json/new | python3 -c "import sys, json; print(json.loads(sys.stdin.read())['id'])")

curl -s -X POST -H "Content-Type: application/json" \
  -d '{"id":1,"method":"Page.navigate","params":{"url":"http://localhost:3000"}}' \
  http://localhost:9222/devtools/page/$PAGE_ID

# 3. Take screenshot
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"id":2,"method":"Page.captureScreenshot"}' \
  http://localhost:9222/devtools/page/$PAGE_ID > /tmp/mystocks-test.png

# 4. Cleanup
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"id":3,"method":"Page.close"}' \
  http://localhost:9222/devtools/page/$PAGE_ID

echo "✅ Test complete. Screenshot saved to /tmp/mystocks-test.png"
```

---

## MCP Skill Integration (Optional)

If you want to use `skill_mcp` tool to invoke Chrome DevTools MCP:

### Configuration

Edit `~/.config/claude/config.json`:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "-y",
        "chrome-devtools-mcp@latest",
        "--browser-url=http://localhost:9222"
      ],
      "type": "stdio",
      "scope": "user"
    }
  }
}
```

### Verification

```bash
# Check config exists
cat ~/.config/claude/config.json

# Restart OpenCode/Claude Code to reload config
# Then test with skill_mcp
```

**Note**: Direct HTTP API (Option 1) is faster and doesn't require config changes.

---

## Troubleshooting

### Chrome DevTools MCP not found via skill_mcp

**Problem**: `Error: MCP server "chrome-devtools" not found`

**Solution**: Use direct HTTP API (Option 1) instead. The MCP server is running but not registered in skill system config.

### Port 9222 not accessible

**Problem**: Connection refused on port 9222

**Solution**: Ensure Chrome is running with remote debugging:
```bash
# Check if Chrome is running with debugging
ps aux | grep chrome | grep remote-debugging

# If not, start Chrome with:
google-chrome --headless --remote-debugging-port=9222 \
  --remote-debugging-address=0.0.0.0 \
  --no-sandbox --disable-dev-shm-usage
```

### Frontend not running

**Problem**: `curl` to localhost:3000 fails

**Solution**: Start the frontend:
```bash
cd /opt/claude/mystocks_spec/web/frontend
npm run dev
```

### Screenshot fails in headless mode

**Problem**: Screenshots return empty or fail

**Solution**: Some operations require visible browser. Try without `--headless` flag:
```bash
google-chrome --remote-debugging-port=9222 \
  --remote-debugging-address=0.0.0.0 \
  --no-sandbox --disable-dev-shm-usage
```

---

## Common MyStocks Routes for Testing

| Route | Purpose |
|-------|---------|
| `/` | Home page |
| `/trade` | Trade management |
| `/portfolio` | Portfolio management |
| `/technical` | Technical analysis |
| `/market` | Market data |
| `/dashboard` | Dashboard |
| `/settings` | Settings |

Navigate to any route by updating the URL in the `Page.navigate` call:
```bash
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"id":1,"method":"Page.navigate","params":{"url":"http://localhost:3000/trade"}}' \
  http://localhost:9222/devtools/page/$PAGE_ID
```

---

## Known Limitations

1. **Single tab operation**: One tab at a time. Manage tabs manually.
2. **Port conflicts**: Port 9222 must be available.
3. **Headless mode**: Some features (screenshots) may need visible browser.
4. **No concurrent operations**: One operation at a time per tab.

---

## Summary

| Method | Use Case | Setup Required |
|--------|----------|----------------|
| **HTTP API** | Quick testing, automation | Chrome with remote debugging (port 9222) |
| **Playwright MCP** | Alternative when HTTP not suitable | Playwright MCP loaded in skill system |
| **MCP Skill Integration** | Long-term use with skill_mcp tool | Config file edit + restart |

**Recommendation**: Start with HTTP API (Option 1) - it's simple and works immediately.

---

## What Changed from v1.0

### Removed Redundancy
- Removed duplicate HTTP API examples (appearing 3+ times in original)
- Removed verbose problem analysis (7699 lines → ~200 lines)
- Removed MyStocks route validation tables (belongs in project docs)
- Removed tool list tables (reference official Chrome DevTools MCP docs)

### Improved Structure
- Quick Start at top (what works now)
- Essential commands reference (copy-paste ready)
- Optional MCP integration (if you need skill_mcp)
- Troubleshooting section (common issues)
- MyStocks routes (practical reference)

### Focus on Practical Solutions
- Direct HTTP API usage emphasized (works without config)
- Playwright MCP as alternative (already loaded)
- MCP integration kept optional (not required)

---

**Related Documentation**:
- Chrome DevTools MCP: https://github.com/modelcontextprotocol/servers
- OpenCode MCP System: Check OpenCode documentation
- MyStocks Project: `/opt/claude/mystocks_spec/CLAUDE.md`
