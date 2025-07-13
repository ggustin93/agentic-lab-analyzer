#!/bin/bash

# =============================================================================
# Docker Cleanup Script - Health Document Analyzer
# =============================================================================
# Prevents memory saturation by cleaning up Docker resources
# Run this script regularly or before each development session
# =============================================================================

set -e  # Exit on any error

echo "🧹 Starting Docker cleanup for Health Document Analyzer..."
echo "========================================================"

# Function to display colored output
print_step() {
    echo -e "\n🔄 $1"
}

print_success() {
    echo -e "✅ $1"
}

print_warning() {
    echo -e "⚠️  $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to display disk usage before cleanup
show_initial_usage() {
    print_step "Current Docker disk usage:"
    docker system df || true
}

# Function to stop and remove project containers
cleanup_project_containers() {
    print_step "Stopping and removing project containers..."
    
    # Stop all containers for this project
    docker-compose down --remove-orphans --volumes || {
        print_warning "docker-compose down failed (maybe no containers running)"
    }
    
    # Remove any orphaned containers related to the project
    docker ps -a --filter "name=agentic-lab-analyzer" --format "{{.ID}}" | xargs -r docker rm -f || true
    docker ps -a --filter "name=health-document" --format "{{.ID}}" | xargs -r docker rm -f || true
    
    print_success "Project containers cleaned up"
}

# Function to remove dangling images
cleanup_dangling_images() {
    print_step "Removing dangling images..."
    
    dangling_images=$(docker images -f "dangling=true" -q)
    if [ -n "$dangling_images" ]; then
        echo "$dangling_images" | xargs docker rmi || true
        print_success "Dangling images removed"
    else
        print_success "No dangling images found"
    fi
}

# Function to clean up unused networks
cleanup_networks() {
    print_step "Removing unused networks..."
    docker network prune -f || true
    print_success "Unused networks cleaned up"
}

# Function to clean up unused volumes
cleanup_volumes() {
    print_step "Removing unused volumes..."
    docker volume prune -f || true
    print_success "Unused volumes cleaned up"
}

# Function to clean up build cache
cleanup_build_cache() {
    print_step "Removing build cache..."
    docker builder prune -f || true
    print_success "Build cache cleaned up"
}

# Function for aggressive cleanup (optional)
aggressive_cleanup() {
    read -p "🚨 Perform aggressive cleanup? This will remove ALL unused images, not just dangling ones (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_step "Performing aggressive cleanup..."
        
        # Remove all unused images (not just dangling)
        docker image prune -a -f || true
        
        # Remove all stopped containers
        docker container prune -f || true
        
        print_success "Aggressive cleanup completed"
    else
        print_success "Skipped aggressive cleanup"
    fi
}

# Function to display final disk usage
show_final_usage() {
    print_step "Docker disk usage after cleanup:"
    docker system df || true
}

# Function to display cleanup summary
show_summary() {
    echo ""
    echo "========================================================"
    echo "🎉 Docker cleanup completed successfully!"
    echo "========================================================"
    echo ""
    echo "📋 What was cleaned:"
    echo "   • Stopped and removed project containers"
    echo "   • Removed dangling images"
    echo "   • Cleaned up unused networks"
    echo "   • Cleaned up unused volumes" 
    echo "   • Cleared build cache"
    echo ""
    echo "💡 Tips for preventing memory issues:"
    echo "   • Run this script weekly: ./docker-cleanup.sh"
    echo "   • Always use: docker-compose down --remove-orphans"
    echo "   • Monitor usage: docker system df"
    echo "   • Set up cron job for automatic cleanup"
    echo ""
}

# Function to setup automatic cleanup (optional)
setup_cron() {
    read -p "📅 Set up weekly automatic cleanup via cron? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        SCRIPT_PATH=$(realpath "$0")
        CRON_JOB="0 2 * * 0 $SCRIPT_PATH > /tmp/docker-cleanup.log 2>&1"
        
        (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
        print_success "Cron job added: Weekly cleanup every Sunday at 2 AM"
        echo "   Log file: /tmp/docker-cleanup.log"
    else
        print_success "Skipped cron setup"
    fi
}

# Main execution flow
main() {
    echo "🚀 Health Document Analyzer - Docker Cleanup Tool"
    echo "=================================================="
    
    check_docker
    show_initial_usage
    
    cleanup_project_containers
    cleanup_dangling_images
    cleanup_networks
    cleanup_volumes
    cleanup_build_cache
    
    aggressive_cleanup
    
    show_final_usage
    show_summary
    
    setup_cron
}

# Handle script interruption
trap 'echo -e "\n❌ Cleanup interrupted by user"; exit 1' INT

# Run main function
main "$@"