#!/bin/bash

# =============================================================================
# Development Startup Script with Automatic Cleanup
# =============================================================================
# Ensures clean Docker environment before starting development
# Prevents memory accumulation and orphaned containers
# =============================================================================

set -e

echo "🚀 Health Document Analyzer - Development Startup"
echo "=================================================="

# Function to display colored output
print_step() {
    echo -e "\n🔄 $1"
}

print_success() {
    echo -e "✅ $1"
}

print_error() {
    echo -e "❌ $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to perform quick cleanup before starting
quick_cleanup() {
    print_step "Performing quick cleanup before startup..."
    
    # Stop any existing containers for this project
    docker-compose down --remove-orphans --volumes 2>/dev/null || true
    
    # Remove dangling images to free up space
    docker image prune -f 2>/dev/null || true
    
    # Clean up unused networks
    docker network prune -f 2>/dev/null || true
    
    print_success "Quick cleanup completed"
}

# Function to show current Docker usage
show_usage() {
    print_step "Current Docker disk usage:"
    docker system df 2>/dev/null || true
}

# Function to start the application
start_application() {
    print_step "Starting Health Document Analyzer..."
    
    # Build and start with clean slate
    docker-compose up --build --remove-orphans "$@"
}

# Function to handle cleanup on exit
cleanup_on_exit() {
    echo ""
    print_step "Shutting down and cleaning up..."
    
    # Stop containers gracefully
    docker-compose down --remove-orphans || true
    
    print_success "Development session ended cleanly"
}

# Main execution
main() {
    echo "🔧 Preparing development environment..."
    
    check_docker
    show_usage
    quick_cleanup
    
    # Set up cleanup on script exit
    trap cleanup_on_exit EXIT INT TERM
    
    # Start the application
    start_application "$@"
}

# Run main function with all script arguments
main "$@"