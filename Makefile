# =============================================================================
# Health Document Analyzer - Docker Management Makefile
# =============================================================================
# Provides convenient commands for Docker resource management
# Helps prevent memory saturation during development
# =============================================================================

.PHONY: help clean start monitor setup dev-clean dev-up test-all

# Default target
help:
	@echo "🚀 Health Document Analyzer - Docker Management"
	@echo "=============================================="
	@echo ""
	@echo "Available commands:"
	@echo ""
	@echo "🧹 Cleanup Commands:"
	@echo "  make clean          - Full Docker cleanup (recommended weekly)"
	@echo "  make dev-clean      - Quick cleanup for development"
	@echo ""
	@echo "🚀 Development Commands:"
	@echo "  make start          - Clean start of the application"
	@echo "  make dev-up         - Start in development mode with cleanup"
	@echo ""
	@echo "📊 Monitoring Commands:"
	@echo "  make monitor        - Check Docker resource usage"
	@echo "  make monitor-detail - Detailed Docker resource breakdown"
	@echo ""
	@echo "🧪 Testing Commands:"
	@echo "  make test-all       - Run all tests in Docker"
	@echo ""
	@echo "⚙️  Setup Commands:"
	@echo "  make setup          - Make scripts executable and setup environment"
	@echo ""
	@echo "💡 Best Practices:"
	@echo "  • Run 'make clean' weekly to prevent memory issues"
	@echo "  • Use 'make start' instead of 'docker-compose up'"
	@echo "  • Monitor usage with 'make monitor'"
	@echo "  • Always use '--remove-orphans' flag"

# Make scripts executable
setup:
	@echo "⚙️  Setting up Docker management scripts..."
	@chmod +x docker-cleanup.sh
	@chmod +x dev-start.sh 
	@chmod +x docker-monitor.sh
	@echo "✅ Scripts are now executable"
	@echo ""
	@echo "💡 You can now use:"
	@echo "   • make clean     - for full cleanup"
	@echo "   • make start     - for clean development start"
	@echo "   • make monitor   - for resource monitoring"

# Full cleanup - prevents memory saturation
clean:
	@echo "🧹 Performing full Docker cleanup..."
	@chmod +x docker-cleanup.sh
	@./docker-cleanup.sh

# Quick development cleanup
dev-clean:
	@echo "🔄 Quick development cleanup..."
	@docker-compose down --remove-orphans --volumes 2>/dev/null || true
	@docker image prune -f 2>/dev/null || true
	@docker network prune -f 2>/dev/null || true
	@echo "✅ Quick cleanup completed"

# Clean start of the application
start: dev-clean
	@echo "🚀 Starting Health Document Analyzer with clean environment..."
	@chmod +x dev-start.sh
	@./dev-start.sh

# Development mode with automatic cleanup
dev-up: dev-clean
	@echo "🔧 Starting in development mode..."
	@docker-compose up --build --remove-orphans

# Monitor Docker resource usage
monitor:
	@echo "📊 Checking Docker resource usage..."
	@chmod +x docker-monitor.sh
	@./docker-monitor.sh

# Detailed monitoring
monitor-detail:
	@echo "📊 Detailed Docker resource monitoring..."
	@chmod +x docker-monitor.sh
	@./docker-monitor.sh --detailed

# Run all tests in Docker
test-all: dev-clean
	@echo "🧪 Running all tests in Docker environment..."
	@docker-compose run --rm --no-deps demo npm run test:docker
	@docker-compose run --rm cypress
	@echo "✅ All tests completed"

# Stop everything and cleanup
stop:
	@echo "🛑 Stopping all containers and cleaning up..."
	@docker-compose down --remove-orphans --volumes
	@echo "✅ All containers stopped"

# Development cycle - clean, start, and monitor
dev: clean start monitor

# Production build with cleanup
build: dev-clean
	@echo "🏗️  Building production images..."
	@docker-compose build --no-cache
	@echo "✅ Production build completed"

# Emergency cleanup - removes everything Docker related to the project
emergency-clean:
	@echo "🚨 EMERGENCY CLEANUP - Removing all project Docker resources..."
	@docker-compose down --remove-orphans --volumes --rmi all 2>/dev/null || true
	@docker system prune -a -f --volumes 2>/dev/null || true
	@echo "✅ Emergency cleanup completed"

# Show current status
status:
	@echo "📊 Current Docker Status:"
	@echo ""
	@echo "🐳 Running Containers:"
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || echo "No running containers"
	@echo ""
	@echo "💾 Disk Usage:"
	@docker system df || echo "Cannot get disk usage"
	@echo ""
	@echo "🔗 Project Networks:"
	@docker network ls --filter name=agentic-lab-analyzer || echo "No project networks"

# Install dependencies and setup
install: setup
	@echo "📦 Installing frontend dependencies..."
	@npm install
	@echo "📦 Installing backend dependencies..."
	@cd backend && pip install -r requirements.txt
	@echo "✅ Dependencies installed"

# Show Docker information
info:
	@echo "ℹ️  Docker System Information:"
	@docker info | head -20
	@echo ""
	@echo "📊 Resource Usage:"
	@make monitor