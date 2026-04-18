#!/bin/bash
# ensure_browsers.sh — Align browser and driver versions, clean old caches
# Run before any browser-based testing to guarantee a clean, consistent state.
#
# Usage:
#   bash scripts/ensure_browsers.sh          # clean + check
#   bash scripts/ensure_browsers.sh --fix    # clean + install missing drivers
#   bash scripts/ensure_browsers.sh --list   # list all available browsers
#
# What it does:
#   1. Removes old Playwright browser versions (keeps highest)
#   2. Removes old Puppeteer Chrome versions (keeps highest)
#   3. Verifies ChromeDriver matches system Chrome
#   4. Reports final browser/driver status

set -euo pipefail

FIX_MODE=false
LIST_MODE=false
case "${1:-}" in
    --fix)  FIX_MODE=true ;;
    --list) LIST_MODE=true ;;
esac

# --- Helpers ---

log()  { echo "[$(date '+%H:%M:%S')] $*"; }
warn() { echo "[$(date '+%H:%M:%S')] WARN: $*"; }
ok()   { echo "[$(date '+%H:%M:%S')]   OK: $*"; }

freed_bytes=0
add_freed() { freed_bytes=$((freed_bytes + $1)); }

human_size() {
    local bytes=$1
    if   (( bytes >= 1073741824 )); then echo "$((bytes / 1073741824)) GiB"
    elif (( bytes >= 1048576 ));     then echo "$((bytes / 1048576)) MiB"
    elif (( bytes >= 1024 ));        then echo "$((bytes / 1024)) KiB"
    else echo "${bytes} bytes"
    fi
}

dir_size() {
    du -sb "$1" 2>/dev/null | awk '{print $1}'
}

# --- Step 1: Clean Playwright cache ---

clean_playwright() {
    log "Step 1: Cleaning Playwright browser cache..."
    local pw_dir="/root/.cache/ms-playwright"
    [[ -d "$pw_dir" ]] || { ok "No Playwright cache"; return; }

    # Find latest chromium version directory
    local latest=""
    for d in "$pw_dir"/chromium-*/; do
        [[ -d "$d" ]] || continue
        local ver
        ver=$(basename "$d" | sed 's/chromium-//')
        if [[ -z "$latest" || "$ver" > "$latest" ]]; then
            latest="$ver"
        fi
    done

    # Remove old chromium versions
    for d in "$pw_dir"/chromium-*/; do
        [[ -d "$d" ]] || continue
        local ver
        ver=$(basename "$d" | sed 's/chromium-//')
        if [[ "$ver" != "$latest" ]]; then
            local sz
            sz=$(dir_size "$d")
            rm -rf "$d"
            add_freed "$sz"
            warn "Removed old Playwright chromium-$ver ($(human_size "$sz"))"
        fi
    done

    # Remove old headless shell versions
    for d in "$pw_dir"/chromium_headless_shell-*/; do
        [[ -d "$d" ]] || continue
        local ver
        ver=$(basename "$d" | sed 's/chromium_headless_shell-//')
        if [[ "$ver" != "$latest" ]]; then
            local sz
            sz=$(dir_size "$d")
            rm -rf "$d"
            add_freed "$sz"
            warn "Removed old Playwright chromium_headless_shell-$ver ($(human_size "$sz"))"
        fi
    done

    ok "Kept Playwright chromium-$latest"
}

# --- Step 2: Clean Puppeteer cache ---

clean_puppeteer() {
    log "Step 2: Cleaning Puppeteer browser cache..."
    local pp_dir="/root/.cache/puppeteer/chrome"
    [[ -d "$pp_dir" ]] || { ok "No Puppeteer cache"; return; }

    local latest=""
    for d in "$pp_dir"/linux-*/; do
        [[ -d "$d" ]] || continue
        local ver
        ver=$(basename "$d" | sed 's/linux-//')
        if [[ -z "$latest" || "$ver" > "$latest" ]]; then
            latest="$ver"
        fi
    done

    for d in "$pp_dir"/linux-*/; do
        [[ -d "$d" ]] || continue
        local ver
        ver=$(basename "$d" | sed 's/linux-//')
        if [[ "$ver" != "$latest" ]]; then
            local sz
            sz=$(dir_size "$d")
            rm -rf "$d"
            add_freed "$sz"
            warn "Removed old Puppeteer chrome $ver ($(human_size "$sz"))"
        fi
    done

    ok "Kept Puppeteer chrome $latest"
}

# --- Step 3: Verify ChromeDriver alignment ---

check_chromedriver() {
    log "Step 3: Checking ChromeDriver alignment..."

    # Detect system Chrome version
    local chrome_ver=""
    if command -v google-chrome &>/dev/null; then
        chrome_ver=$(google-chrome --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+\.\d+' | head -1)
    elif command -v chromium &>/dev/null; then
        chrome_ver=$(chromium --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+\.\d+' | head -1)
    fi

    if [[ -z "$chrome_ver" ]]; then
        warn "No system Chrome/Chromium detected"
        return
    fi

    local major_ver="${chrome_ver%%.*}"

    # Check ChromeDriver
    local driver_path=""
    local driver_ver=""
    if command -v chromedriver &>/dev/null; then
        driver_path=$(command -v chromedriver)
        driver_ver=$(chromedriver --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+\.\d+' | head -1)
    fi

    if [[ -z "$driver_ver" ]]; then
        warn "ChromeDriver not installed for Chrome $chrome_ver"
        if $FIX_MODE; then
            log "Installing ChromeDriver for Chrome $major_ver..."
            # Try npm-based install first (most reliable in WSL)
            if command -v npm &>/dev/null; then
                npm install -g "chromedriver@$major_ver" 2>/dev/null && \
                    ok "Installed ChromeDriver via npm" || \
                    warn "npm install failed, trying apt..."
            fi
            # Fallback: snap
            if command -v snap &>/dev/null && [[ -z "$driver_ver" ]]; then
                sudo snap install chromium-chromedriver 2>/dev/null && \
                    ok "Installed chromium-chromedriver via snap" || true
            fi
        else
            warn "Run with --fix to install: bash scripts/ensure_browsers.sh --fix"
        fi
        return
    fi

    local driver_major="${driver_ver%%.*}"
    if [[ "$driver_major" == "$major_ver" ]]; then
        ok "ChromeDriver $driver_ver matches Chrome $chrome_ver"
    else
        warn "ChromeDriver $driver_ver (major $driver_major) mismatches Chrome $chrome_ver (major $major_ver)"
        if $FIX_MODE; then
            log "Reinstalling ChromeDriver..."
            npm install -g "chromedriver@$major_ver" 2>/dev/null || true
        fi
    fi
}

# --- Step 4: Report ---

report() {
    log "=== Browser Status Report ==="

    # System Chrome
    if command -v google-chrome &>/dev/null; then
        ok "System: $(google-chrome --version 2>/dev/null)"
    fi
    if command -v chromium &>/dev/null; then
        ok "System: $(chromium --version 2>/dev/null)"
    fi

    # ChromeDriver
    if command -v chromedriver &>/dev/null; then
        ok "Driver: $(chromedriver --version 2>/dev/null | head -1)"
    else
        warn "ChromeDriver: not installed"
    fi

    # Playwright
    local pw_dir="/root/.cache/ms-playwright"
    for d in "$pw_dir"/chromium-*/; do
        [[ -d "$d" ]] || continue
        local chrome_bin
        chrome_bin=$(find "$d" -name "chrome" -type f 2>/dev/null | head -1)
        if [[ -x "$chrome_bin" ]]; then
            local pw_ver
            pw_ver=$("$chrome_bin" --version 2>/dev/null || echo "unknown")
            ok "Playwright: $pw_ver"
        fi
    done

    # Puppeteer
    local pp_dir="/root/.cache/puppeteer/chrome"
    for d in "$pp_dir"/linux-*/; do
        [[ -d "$d" ]] || continue
        local chrome_bin
        chrome_bin=$(find "$d" -name "chrome" -type f 2>/dev/null | head -1)
        if [[ -x "$chrome_bin" ]]; then
            local pp_ver
            pp_ver=$("$chrome_bin" --version 2>/dev/null || echo "unknown")
            ok "Puppeteer: $pp_ver"
        fi
    done

    echo ""
    if (( freed_bytes > 0 )); then
        log "Freed $(human_size "$freed_bytes") of old browser caches"
    else
        log "No old caches to clean"
    fi
}

# --- List mode: table of all available browsers ---

list_browsers() {
    local driver_ver=""
    if command -v chromedriver &>/dev/null; then
        driver_ver=$(chromedriver --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+\.\d+' | head -1)
    fi

    printf "%-28s %-24s %-24s %s\n" "BROWSER" "VERSION" "DRIVER" "PATH"
    printf "%-28s %-24s %-24s %s\n" "--------" "-------" "------" "----"

    # System Google Chrome
    if command -v google-chrome &>/dev/null; then
        local ver
        ver=$(google-chrome --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+\.\d+' | head -1)
        printf "%-28s %-24s %-24s %s\n" "Google Chrome" "${ver:-n/a}" "${driver_ver:-not installed}" "$(command -v google-chrome)"
    fi

    # System Chromium
    if command -v chromium &>/dev/null; then
        local ver
        ver=$(chromium --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+\.\d+' | head -1)
        printf "%-28s %-24s %-24s %s\n" "Chromium (snap)" "${ver:-n/a}" "${driver_ver:-not installed}" "$(command -v chromium)"
    fi

    # Playwright browsers
    local pw_dir="/root/.cache/ms-playwright"
    for d in "$pw_dir"/chromium-*/; do
        [[ -d "$d" ]] || continue
        local chrome_bin ver
        chrome_bin=$(find "$d" -name "chrome" -type f 2>/dev/null | head -1)
        ver=""
        [[ -x "$chrome_bin" ]] && ver=$("$chrome_bin" --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+\.\d+' | head -1)
        printf "%-28s %-24s %-24s %s\n" "Playwright Chromium" "${ver:-n/a}" "-" "$d"
    done

    for d in "$pw_dir"/firefox-*/; do
        [[ -d "$d" ]] || continue
        local bin ver
        bin=$(find "$d" -name "firefox" -type f 2>/dev/null | head -1)
        ver=""
        [[ -x "$bin" ]] && ver=$("$bin" --version 2>/dev/null | grep -oP '\d+.*' | head -1)
        printf "%-28s %-24s %-24s %s\n" "Playwright Firefox" "${ver:-n/a}" "-" "$d"
    done

    for d in "$pw_dir"/webkit-*/; do
        [[ -d "$d" ]] || continue
        local bin ver=""
        bin=$(find "$d" -name "MiniBrowser" -o -name "WebKitWebView" -type f 2>/dev/null | head -1)
        printf "%-28s %-24s %-24s %s\n" "Playwright WebKit" "${ver:-cached}" "-" "$d"
    done

    # Puppeteer browsers
    local pp_dir="/root/.cache/puppeteer/chrome"
    for d in "$pp_dir"/linux-*/; do
        [[ -d "$d" ]] || continue
        local chrome_bin ver
        chrome_bin=$(find "$d" -name "chrome" -type f 2>/dev/null | head -1)
        ver=""
        [[ -x "$chrome_bin" ]] && ver=$("$chrome_bin" --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+\.\d+' | head -1)
        printf "%-28s %-24s %-24s %s\n" "Puppeteer Chrome" "${ver:-n/a}" "-" "$d"
    done
}

# --- Main ---

if $LIST_MODE; then
    list_browsers
    exit 0
fi

clean_playwright
clean_puppeteer
check_chromedriver
report
