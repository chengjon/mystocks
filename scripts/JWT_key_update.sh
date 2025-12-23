#!/bin/bash

# Script Name: JWT_key_update.sh
# Description: Automates the process of ensuring JWT_SECRET_KEY is set in .env,
#              then restarts and verifies MyStocks frontend and backend services.
# Version: 1.0
# Date: 2025-12-20

# Define project-specific paths and files
PROJECT_ROOT="/opt/claude/mystocks_spec"
ENV_FILE="$PROJECT_ROOT/.env"
STOCKS_SPEC_SCRIPT="$PROJECT_ROOT/scripts/stocks_spec.sh"

# Define color codes for better terminal output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print informational messages
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to print error messages and exit
print_error() {
    echo -e "${RED}❌ $1${NC}" >&2
    exit 1
}

# --- Step 1: Ensure JWT_SECRET_KEY is present in the .env file ---
print_info "Checking for JWT_SECRET_KEY in $ENV_FILE..."

# Check if the .env file exists
if [ ! -f "$ENV_FILE" ]; then
    print_warning ".env file not found at $ENV_FILE. Creating a new one."
    touch "$ENV_FILE"
fi

# Check if JWT_SECRET_KEY is already defined in .env
if grep -q "^JWT_SECRET_KEY=" "$ENV_FILE"; then
    print_warning "JWT_SECRET_KEY already exists in .env file. Skipping new key generation."
else
    # If not found, generate a new secure key
    print_info "JWT_SECRET_KEY not found. Generating a new secure key..."
    SECRET_KEY=$(openssl rand -hex 32)
    # Append the new key to the .env file
    echo "" >> "$ENV_FILE" # Add a newline for clean separation
    echo "# Added by JWT_key_update.sh script on $(date)" >> "$ENV_FILE"
    echo "JWT_SECRET_KEY=$SECRET_KEY" >> "$ENV_FILE"
    print_success "Successfully added JWT_SECRET_KEY to .env file."
fi

echo "" # Add a newline for better readability in output

# --- Step 2: Restart all services using stocks_spec.sh script ---
print_info "Restarting all services using $STOCKS_SPEC_SCRIPT..."

# Verify that stocks_spec.sh exists and is executable
if [ ! -f "$STOCKS_SPEC_SCRIPT" ]; then
    print_error "Could not find stocks_spec.sh script at $STOCKS_SPEC_SCRIPT. Please ensure it exists."
fi
if [ ! -x "$STOCKS_SPEC_SCRIPT" ]; then
    print_warning "$STOCKS_SPEC_SCRIPT is not executable. Attempting to make it executable."
    chmod +x "$STOCKS_SPEC_SCRIPT" || print_error "Failed to make $STOCKS_SPEC_SCRIPT executable."
fi

# Execute the restart command from stocks_spec.sh
bash "$STOCKS_SPEC_SCRIPT" -restart || print_error "Failed to restart services via stocks_spec.sh."

echo "" # Add a newline for better readability in output

# --- Step 3: Verify the final status of services ---
print_info "Waiting a few seconds for services to stabilize before checking status..."
sleep 5 # Give services a moment to fully start up

print_info "Checking the final status of services..."
bash "$STOCKS_SPEC_SCRIPT" -status # Display the status report from stocks_spec.sh

echo "" # Add a newline for better readability in output
print_success "JWT_key_update.sh script execution completed."
print_success "Please check the output above for service status and URLs."
