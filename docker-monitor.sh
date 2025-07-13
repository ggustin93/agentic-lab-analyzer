#!/bin/bash

# =============================================================================
# Docker Resource Monitor - Health Document Analyzer
# =============================================================================
# Monitors Docker resource usage and alerts when thresholds are exceeded
# Can be run manually or scheduled via cron
# =============================================================================

# Configuration
WARNING_THRESHOLD=75    # Percentage of disk usage to trigger warning
CRITICAL_THRESHOLD=90   # Percentage of disk usage to trigger critical alert
LOG_FILE="/tmp/docker-monitor.log"

# Function to display colored output
print_info() {
    echo -e "\n📊 $1"
}

print_warning() {
    echo -e "\n⚠️  WARNING: $1"
}

print_critical() {
    echo -e "\n🚨 CRITICAL: $1"
}

print_success() {
    echo -e "\n✅ $1"
}

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Function to check Docker disk usage
check_disk_usage() {
    # Get disk usage information
    local usage_info=$(docker system df --format "table {{.Type}}\t{{.TotalCount}}\t{{.Size}}\t{{.Reclaimable}}" 2>/dev/null)
    
    print_info "Current Docker Resource Usage:"
    echo "$usage_info"
    
    # Extract total size and calculate percentage (simplified)
    local total_size=$(docker system df --format "{{.Size}}" | head -1 2>/dev/null || echo "0B")
    local size_gb=$(echo "$total_size" | sed 's/[^0-9.]//g' | cut -d. -f1)
    
    # Simple threshold check based on total containers and images
    local container_count=$(docker ps -a --format "{{.ID}}" | wc -l)
    local image_count=$(docker images --format "{{.ID}}" | wc -l)
    local total_objects=$((container_count + image_count))
    
    log_message "Docker usage check: $total_objects total objects, $container_count containers, $image_count images"
    
    # Alert based on object count (simplified monitoring)
    if [ "$total_objects" -gt 50 ]; then
        print_critical "Too many Docker objects detected ($total_objects total)"
        print_critical "Consider running: ./docker-cleanup.sh"
        log_message "CRITICAL: High object count detected - $total_objects objects"
        return 2
    elif [ "$total_objects" -gt 30 ]; then
        print_warning "Docker object count is getting high ($total_objects total)"
        print_warning "Consider running cleanup soon"
        log_message "WARNING: Moderate object count - $total_objects objects"
        return 1
    else
        print_success "Docker resource usage is healthy ($total_objects objects)"
        log_message "INFO: Resource usage normal - $total_objects objects"
        return 0
    fi
}

# Function to show detailed breakdown
show_detailed_info() {
    print_info "Detailed Docker Information:"
    
    echo ""
    echo "🐳 Containers:"
    docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Size}}" 2>/dev/null || echo "No containers found"
    
    echo ""
    echo "🖼️  Images:"
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" 2>/dev/null || echo "No images found"
    
    echo ""
    echo "🔗 Networks:"
    docker network ls 2>/dev/null || echo "No networks found"
    
    echo ""
    echo "💾 Volumes:"
    docker volume ls 2>/dev/null || echo "No volumes found"
}

# Function to suggest cleanup actions
suggest_cleanup() {
    local status=$1
    
    case $status in
        2)
            echo ""
            echo "🛠️  IMMEDIATE ACTION REQUIRED:"
            echo "   1. Run: ./docker-cleanup.sh"
            echo "   2. Consider aggressive cleanup if needed"
            echo "   3. Remove unnecessary images: docker image prune -a"
            ;;
        1)
            echo ""
            echo "💡 RECOMMENDED ACTIONS:"
            echo "   1. Run: ./docker-cleanup.sh"
            echo "   2. Remove unused containers: docker container prune"
            echo "   3. Monitor usage regularly"
            ;;
        0)
            echo ""
            echo "💡 MAINTENANCE TIPS:"
            echo "   • Run weekly cleanup: ./docker-cleanup.sh"
            echo "   • Use: docker-compose down --remove-orphans"
            echo "   • Monitor: ./docker-monitor.sh"
            ;;
    esac
}

# Function to check if cleanup script exists
check_cleanup_script() {
    if [ ! -f "./docker-cleanup.sh" ]; then
        print_warning "Cleanup script not found in current directory"
        echo "Make sure you're in the project root directory"
    fi
}

# Main execution
main() {
    echo "🔍 Docker Resource Monitor - Health Document Analyzer"
    echo "===================================================="
    echo "Timestamp: $(date)"
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_critical "Docker is not running"
        log_message "ERROR: Docker not running"
        exit 1
    fi
    
    # Create log file if it doesn't exist
    touch "$LOG_FILE"
    
    # Check cleanup script availability
    check_cleanup_script
    
    # Perform monitoring
    check_disk_usage
    local status=$?
    
    # Show detailed information if requested
    if [ "$1" = "--detailed" ] || [ "$1" = "-d" ]; then
        show_detailed_info
    fi
    
    # Suggest cleanup actions
    suggest_cleanup $status
    
    echo ""
    echo "📋 Log file: $LOG_FILE"
    echo "📅 Last 5 entries:"
    tail -5 "$LOG_FILE" 2>/dev/null || echo "No log entries yet"
    
    exit $status
}

# Handle help option
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Docker Resource Monitor"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -d, --detailed    Show detailed Docker information"
    echo "  -h, --help       Show this help message"
    echo ""
    echo "Exit codes:"
    echo "  0 - Normal usage"
    echo "  1 - Warning threshold exceeded"
    echo "  2 - Critical threshold exceeded"
    echo ""
    echo "Examples:"
    echo "  $0                Monitor Docker usage"
    echo "  $0 --detailed     Monitor with detailed breakdown"
    echo ""
    exit 0
fi

# Run main function
main "$@"