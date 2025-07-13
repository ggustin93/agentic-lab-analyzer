# Development Scripts

This directory contains utility scripts for development, testing, and maintenance of the Health Document Analyzer project.

## Shell Scripts

### Development
- **`dev-start.sh`** - Complete development environment startup with automatic cleanup
- **`validate-setup.sh`** - Validates project configuration and dependencies
- **`test-docker.sh`** - Tests Docker build and service connectivity

### Docker Management  
- **`docker-cleanup.sh`** - Comprehensive Docker resource cleanup script
- **`docker-monitor.sh`** - Monitor Docker resource usage with alerts

### Dependency Management
- **`fix-dependencies.sh`** - Fixes npm dependency conflicts and lock file issues

## Node.js Scripts

### Utilities
- **`check-deps.js`** - Analyzes package.json for problematic dependencies and version conflicts

## Usage

Make scripts executable before running:
```bash
chmod +x scripts/*.sh
```

### Quick Start Development
```bash
# Start development environment
./scripts/dev-start.sh

# Validate setup before starting
./scripts/validate-setup.sh

# Check for dependency issues
node scripts/check-deps.js
```

### Docker Management
```bash
# Clean up Docker resources
./scripts/docker-cleanup.sh

# Monitor Docker usage
./scripts/docker-monitor.sh --detailed

# Test Docker builds
./scripts/test-docker.sh
```

### Troubleshooting
```bash
# Fix dependency conflicts
./scripts/fix-dependencies.sh
```

## Integration with Package.json

These scripts are integrated into the main package.json for easy access:

```bash
# Start development with cleanup
npm run dev:start

# Validate project setup  
npm run validate

# Docker cleanup
npm run docker:clean

# Monitor Docker resources
npm run docker:monitor
```

See the main package.json file for the complete list of available scripts.