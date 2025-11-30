#!/bin/bash

################################################################################
# Port Allocation Supervisor Script for MyStocks Spec
# Purpose: Monitor and enforce port allocation rules
# Ports: Frontend 3000-3009, Backend 8000-8009
# Enforcement: MANDATORY
# Date: 2025-11-30
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_PORT_MIN=3000
FRONTEND_PORT_MAX=3009
BACKEND_PORT_MIN=8000
BACKEND_PORT_MAX=8009

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "${BLUE}${BOLD}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║       MyStocks Spec - Port Allocation Supervisor          ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_section() {
    echo -e "\n${BOLD}>>> $1${NC}\n"
}

check_port_occupied() {
    local port=$1
    lsof -i :$port > /dev/null 2>&1
    return $?
}

get_port_process() {
    local port=$1
    lsof -i :$port 2>/dev/null | tail -1 | awk '{print $1 " (PID: " $2 ")"}'
}

is_port_in_range() {
    local port=$1
    local min=$2
    local max=$3

    if [ $port -ge $min ] && [ $port -le $max ]; then
        return 0
    else
        return 1
    fi
}

################################################################################
# Main Checks
################################################################################

check_frontend_ports() {
    print_section "📱 Frontend Port Range Check (3000-3009)"

    local occupied_count=0
    local available=()

    for port in $(seq $FRONTEND_PORT_MIN $FRONTEND_PORT_MAX); do
        if check_port_occupied $port; then
            echo -e "  ${RED}❌${NC} Port $port: OCCUPIED"
            echo "    └─ Process: $(get_port_process $port)"
            occupied_count=$((occupied_count + 1))
        else
            echo -e "  ${GREEN}✅${NC} Port $port: Available"
            available+=($port)
        fi
    done

    echo ""
    if [ $occupied_count -eq 0 ]; then
        echo -e "${GREEN}Status: All frontend ports available${NC}"
        return 0
    else
        echo -e "${YELLOW}Status: $occupied_count frontend port(s) occupied${NC}"
        if [ ${#available[@]} -gt 0 ]; then
            echo -e "${GREEN}Available ports: ${available[@]}${NC}"
        fi
        return 1
    fi
}

check_backend_ports() {
    print_section "🔴 Backend Port Range Check (8000-8009)"

    local occupied_count=0
    local available=()

    for port in $(seq $BACKEND_PORT_MIN $BACKEND_PORT_MAX); do
        if check_port_occupied $port; then
            echo -e "  ${RED}❌${NC} Port $port: OCCUPIED"
            echo "    └─ Process: $(get_port_process $port)"
            occupied_count=$((occupied_count + 1))
        else
            echo -e "  ${GREEN}✅${NC} Port $port: Available"
            available+=($port)
        fi
    done

    echo ""
    if [ $occupied_count -eq 0 ]; then
        echo -e "${GREEN}Status: All backend ports available${NC}"
        return 0
    else
        echo -e "${YELLOW}Status: $occupied_count backend port(s) occupied${NC}"
        if [ ${#available[@]} -gt 0 ]; then
            echo -e "${GREEN}Available ports: ${available[@]}${NC}"
        fi
        return 1
    fi
}

check_config_compliance() {
    print_section "⚙️  Configuration File Compliance"

    local issues=0

    # Check .env file
    if [ -f ".env" ]; then
        echo -e "  ${GREEN}✅${NC} .env file exists"

        if grep -q "VITE_PORT" .env; then
            local port=$(grep "VITE_PORT" .env | cut -d'=' -f2)
            if is_port_in_range $port $FRONTEND_PORT_MIN $FRONTEND_PORT_MAX; then
                echo -e "    └─ VITE_PORT=$port ${GREEN}✅ (valid)${NC}"
            else
                echo -e "    └─ VITE_PORT=$port ${RED}❌ (out of range)${NC}"
                issues=$((issues + 1))
            fi
        else
            echo -e "    └─ ${YELLOW}⚠️  VITE_PORT not set${NC}"
        fi
    else
        echo -e "  ${YELLOW}⚠️  .env file not found${NC}"
    fi

    # Check playwright.config.js
    if [ -f "web/frontend/playwright.config.js" ]; then
        echo -e "  ${GREEN}✅${NC} playwright.config.js exists"

        if grep -q "baseURL" web/frontend/playwright.config.js; then
            echo -e "    └─ baseURL configured ${GREEN}✅${NC}"
        else
            echo -e "    └─ ${YELLOW}⚠️  baseURL not configured${NC}"
            issues=$((issues + 1))
        fi
    else
        echo -e "  ${YELLOW}⚠️  playwright.config.js not found${NC}"
    fi

    return $issues
}

check_running_services() {
    print_section "🏃 Running Services Check"

    echo "  Frontend Services (3000-3009):"
    local frontend_running=0
    for port in $(seq $FRONTEND_PORT_MIN $FRONTEND_PORT_MAX); do
        if check_port_occupied $port; then
            echo -e "    └─ ${GREEN}✅${NC} Port $port: $(get_port_process $port)"
            frontend_running=$((frontend_running + 1))
        fi
    done
    [ $frontend_running -eq 0 ] && echo -e "    └─ ${YELLOW}No services running${NC}"

    echo ""
    echo "  Backend Services (8000-8009):"
    local backend_running=0
    for port in $(seq $BACKEND_PORT_MIN $BACKEND_PORT_MAX); do
        if check_port_occupied $port; then
            echo -e "    └─ ${GREEN}✅${NC} Port $port: $(get_port_process $port)"
            backend_running=$((backend_running + 1))
        fi
    done
    [ $backend_running -eq 0 ] && echo -e "    └─ ${YELLOW}No services running${NC}"
}

print_recommendations() {
    print_section "💡 Recommendations"

    echo -e "${BOLD}If you're starting services:${NC}"
    echo ""
    echo -e "  ${GREEN}Frontend:${NC}"
    echo "    cd web/frontend && npm run dev -- --port 3000"
    echo "    or"
    echo "    VITE_PORT=3002 npm run dev  (if 3000 is occupied)"
    echo ""
    echo -e "  ${GREEN}Backend:${NC}"
    echo "    python -m uvicorn web.backend.app.main:app --port 8000"
    echo "    or"
    echo "    python -m uvicorn web.backend.app.main:app --port 8001  (if 8000 is occupied)"
    echo ""
    echo -e "${BOLD}If you need to free ports:${NC}"
    echo ""
    echo "    # Check which process is using the port"
    echo "    lsof -i :3000"
    echo ""
    echo "    # Kill the process (be careful!)"
    echo "    kill -9 <PID>"
}

print_summary() {
    print_section "📊 Summary"

    echo -e "${BOLD}Port Allocation Status:${NC}"
    echo "  • Frontend Range: 3000-3009"
    echo "  • Backend Range:  8000-8009"
    echo ""
    echo -e "${BOLD}Enforcement Level:${NC} 🔒 ${RED}MANDATORY${NC}"
    echo ""
    echo -e "${BOLD}Violations Escalation:${NC}"
    echo "  🟡 Level 1: Code review comment"
    echo "  🟠 Level 2: Merge blocked"
    echo "  🔴 Level 3: Team meeting"
}

################################################################################
# Main Execution
################################################################################

main() {
    print_header

    check_frontend_ports
    frontend_status=$?

    check_backend_ports
    backend_status=$?

    check_config_compliance

    check_running_services

    print_recommendations

    print_summary

    echo ""

    if [ $frontend_status -eq 0 ] && [ $backend_status -eq 0 ]; then
        echo -e "${GREEN}${BOLD}✅ All port allocation checks passed!${NC}"
        return 0
    else
        echo -e "${YELLOW}${BOLD}⚠️  Some ports are occupied. Use available ports from the ranges above.${NC}"
        return 1
    fi
}

# Run main
main
exit $?
