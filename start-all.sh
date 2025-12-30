#!/bin/bash

# UniLink Backend - Unified Startup Script
# Starts all three services: Main API, Chat Service, and Notification Service

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Directories
MAIN_DIR="$(pwd)/app"
CHAT_DIR="$(pwd)/chat-service"
NOTIF_DIR="$(pwd)/notification-service"

# Log files
LOG_DIR="$(pwd)/logs"
MAIN_LOG="$LOG_DIR/main.log"
CHAT_LOG="$LOG_DIR/chat.log"
NOTIF_LOG="$LOG_DIR/notification.log"

# PIDs
MAIN_PID=""
CHAT_PID=""
NOTIF_PID=""

# Print colored output
print_header() {
    echo -e "\n${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  $1${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_service() {
    echo -e "${MAGENTA}🔧 $1${NC}"
}

# Create log directory
mkdir -p "$LOG_DIR"

# Cleanup function
cleanup() {
    echo ""
    print_header "Shutting Down Services"
    
    if [ -n "$MAIN_PID" ]; then
        print_info "Stopping Main API (PID: $MAIN_PID)..."
        kill "$MAIN_PID" 2>/dev/null || true
    fi
    
    if [ -n "$CHAT_PID" ]; then
        print_info "Stopping Chat Service (PID: $CHAT_PID)..."
        kill "$CHAT_PID" 2>/dev/null || true
    fi
    
    if [ -n "$NOTIF_PID" ]; then
        print_info "Stopping Notification Service (PID: $NOTIF_PID)..."
        kill "$NOTIF_PID" 2>/dev/null || true
    fi
    
    print_success "All services stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT SIGTERM

# Check dependencies
check_dependencies() {
    print_header "Checking Dependencies"
    
    local missing=0
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        missing=1
    else
        print_success "Python 3 found: $(python3 --version)"
    fi
    
    if ! command -v go &> /dev/null; then
        print_error "Go is not installed"
        missing=1
    else
        print_success "Go found: $(go version)"
    fi
    
    if ! command -v mongod &> /dev/null; then
        print_error "MongoDB is not installed"
        missing=1
    else
        print_success "MongoDB found"
    fi
    
    if ! command -v redis-cli &> /dev/null; then
        print_error "Redis is not installed"
        missing=1
    else
        print_success "Redis found"
    fi
    
    if [ $missing -eq 1 ]; then
        exit 1
    fi
}

# Check if services are running
check_services() {
    print_header "Checking Required Services"
    
    # Check MongoDB
    if mongosh --eval "db.adminCommand('ping')" --quiet &> /dev/null; then
        print_success "MongoDB is running"
    else
        print_error "MongoDB is not running. Please start MongoDB first."
        print_info "Start with: mongod --dbpath /path/to/data"
        exit 1
    fi
    
    # Check Redis
    if redis-cli ping &> /dev/null; then
        print_success "Redis is running"
    else
        print_error "Redis is not running. Please start Redis first."
        print_info "Start with: redis-server"
        exit 1
    fi
}

# Check environment files
check_env_files() {
    print_header "Checking Environment Files"
    
    if [ ! -f "$MAIN_DIR/.env" ]; then
        print_error "Main API .env file not found"
        print_info "Copy .env.example to .env and configure it"
        exit 1
    fi
    print_success "Main API .env found"
    
    if [ ! -f "$CHAT_DIR/.env" ]; then
        print_error "Chat Service .env file not found"
        exit 1
    fi
    print_success "Chat Service .env found"
    
    if [ ! -f "$NOTIF_DIR/.env" ]; then
        print_error "Notification Service .env file not found"
        exit 1
    fi
    print_success "Notification Service .env found"
}

# Build notification service
build_notification_service() {
    print_header "Building Notification Service"
    
    cd "$NOTIF_DIR"
    
    print_info "Downloading Go dependencies..."
    go mod download
    
    print_info "Building notification service..."
    go build -o notification-service cmd/server/main.go
    
    if [ $? -eq 0 ]; then
        print_success "Notification service built successfully"
    else
        print_error "Failed to build notification service"
        exit 1
    fi
    
    cd - > /dev/null
}

# Start Main API
start_main_api() {
    print_service "Starting Main API (Port 3001)"
    
    cd "$MAIN_DIR"
    
    # Check if virtual environment exists
    if [ ! -d ".venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv .venv
    fi
    
    # Activate virtual environment and install dependencies
    source .venv/bin/activate
    pip install -q --upgrade pip
    pip install -q -r ../requirements.txt 2>&1 | grep -v "already satisfied" || true
    
    # Start the service
    nohup uvicorn main:app --host 0.0.0.0 --port 3001 > "$MAIN_LOG" 2>&1 &
    MAIN_PID=$!
    
    deactivate
    cd - > /dev/null
    
    print_success "Main API started (PID: $MAIN_PID)"
    print_info "Logs: $MAIN_LOG"
}

# Start Chat Service
start_chat_service() {
    print_service "Starting Chat Service (Port 4000)"
    
    cd "$CHAT_DIR"
    
    # Check if virtual environment exists
    if [ ! -d ".venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv .venv
    fi
    
    # Activate virtual environment and install dependencies
    source .venv/bin/activate
    pip install -q --upgrade pip
    
    # Install dependencies from pyproject.toml
    if [ -f "pyproject.toml" ]; then
        pip install -q -e . 2>&1 | grep -v "already satisfied" || true
    fi
    
    # Start the service
    nohup uvicorn main:app --host 0.0.0.0 --port 4000 > "$CHAT_LOG" 2>&1 &
    CHAT_PID=$!
    
    deactivate
    cd - > /dev/null
    
    print_success "Chat Service started (PID: $CHAT_PID)"
    print_info "Logs: $CHAT_LOG"
}

# Start Notification Service
start_notification_service() {
    print_service "Starting Notification Service (Port 8080)"
    
    cd "$NOTIF_DIR"
    
    # Start the service
    nohup ./notification-service > "$NOTIF_LOG" 2>&1 &
    NOTIF_PID=$!
    
    cd - > /dev/null
    
    print_success "Notification Service started (PID: $NOTIF_PID)"
    print_info "Logs: $NOTIF_LOG"
}

# Wait for service to be ready
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=0
    
    print_info "Waiting for $name to be ready..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            print_success "$name is ready"
            return 0
        fi
        
        sleep 1
        attempt=$((attempt + 1))
    done
    
    print_error "$name failed to start"
    return 1
}

# Display service status
show_status() {
    print_header "Service Status"
    
    echo -e "${CYAN}Service${NC}                  ${CYAN}Port${NC}  ${CYAN}Status${NC}      ${CYAN}URL${NC}"
    echo "────────────────────────────────────────────────────────────"
    
    if [ -n "$MAIN_PID" ] && ps -p $MAIN_PID > /dev/null; then
        echo -e "Main API                 3001  ${GREEN}Running${NC}     http://localhost:3001"
    else
        echo -e "Main API                 3001  ${RED}Stopped${NC}     -"
    fi
    
    if [ -n "$CHAT_PID" ] && ps -p $CHAT_PID > /dev/null; then
        echo -e "Chat Service             4000  ${GREEN}Running${NC}     http://localhost:4000"
    else
        echo -e "Chat Service             4000  ${RED}Stopped${NC}     -"
    fi
    
    if [ -n "$NOTIF_PID" ] && ps -p $NOTIF_PID > /dev/null; then
        echo -e "Notification Service     8080  ${GREEN}Running${NC}     http://localhost:8080"
    else
        echo -e "Notification Service     8080  ${RED}Stopped${NC}     -"
    fi
    
    echo ""
}

# Main execution
main() {
    clear
    
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║                                                      ║"
    echo "║           🚀 UniLink Backend Startup                ║"
    echo "║                                                      ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    check_dependencies
    check_services
    check_env_files
    build_notification_service
    
    print_header "Starting Services"
    
    start_main_api
    sleep 2
    
    start_chat_service
    sleep 2
    
    start_notification_service
    sleep 2
    
    print_header "Verifying Services"
    
    wait_for_service "http://localhost:3001/" "Main API"
    wait_for_service "http://localhost:4000/health" "Chat Service"
    wait_for_service "http://localhost:8080/health" "Notification Service"
    
    show_status
    
    print_header "All Services Running"
    
    print_info "Press Ctrl+C to stop all services"
    print_info "Logs are being written to: $LOG_DIR"
    
    echo ""
    echo -e "${GREEN}✨ UniLink Backend is ready!${NC}"
    echo ""
    
    # Keep the script running
    while true; do
        sleep 1
    done
}

# Run main
main