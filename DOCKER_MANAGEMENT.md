# 🐳 Docker Management Guide

## Overview

This guide provides comprehensive Docker resource management tools to prevent memory saturation and maintain a clean development environment.

## 🛠️ Available Tools

### 1. Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `docker-cleanup.sh` | Full cleanup and maintenance | `./docker-cleanup.sh` |
| `dev-start.sh` | Clean development startup | `./dev-start.sh` |
| `docker-monitor.sh` | Resource usage monitoring | `./docker-monitor.sh` |

### 2. Makefile Commands

| Command | Description | Best For |
|---------|-------------|----------|
| `make setup` | Make scripts executable | First-time setup |
| `make clean` | Full Docker cleanup | Weekly maintenance |
| `make start` | Clean development start | Daily development |
| `make monitor` | Check resource usage | Regular monitoring |
| `make dev-clean` | Quick cleanup | Before coding sessions |

## 🚀 Quick Start

### First Time Setup
```bash
# Make scripts executable
make setup

# Start development with clean environment
make start
```

### Daily Development Workflow
```bash
# Start your development session
make start

# Monitor resources during development
make monitor

# Quick cleanup between sessions
make dev-clean
```

### Weekly Maintenance
```bash
# Full cleanup to prevent memory issues
make clean

# Check overall system health
make monitor-detail
```

## 📊 Memory Management Best Practices

### 1. Before Each Development Session
```bash
# Option A: Using Makefile (recommended)
make start

# Option B: Using docker-compose with best practices
docker-compose down --remove-orphans
docker-compose up --build --remove-orphans
```

### 2. Regular Monitoring
```bash
# Quick check
make monitor

# Detailed analysis
make monitor-detail

# Check Docker system usage
docker system df
```

### 3. Weekly Cleanup
```bash
# Full automated cleanup
make clean

# Manual system-wide cleanup (if needed)
docker system prune -a -f --volumes
```

## 🔍 Understanding Resource Usage

### Warning Signs
- **High container count**: >30 containers
- **Many dangling images**: Shows as "dangling" in `docker images`
- **Large build cache**: Visible in `docker system df`
- **Unused networks/volumes**: Accumulate over time

### Monitoring Commands
```bash
# System overview
docker system df

# Detailed breakdown
make monitor-detail

# Container status
docker ps -a

# Image analysis
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
```

## 🧹 Cleanup Strategies

### 1. Conservative Cleanup (Default)
```bash
make clean
```
**Removes:**
- Stopped containers
- Dangling images
- Unused networks
- Unused volumes
- Build cache

### 2. Aggressive Cleanup (When Needed)
```bash
# Run the cleanup script and choose aggressive option
./docker-cleanup.sh

# Or manually
docker system prune -a -f --volumes
```
**Removes:**
- All unused images (not just dangling)
- All stopped containers
- All unused networks and volumes
- All build cache

### 3. Emergency Cleanup
```bash
make emergency-clean
```
**Removes:**
- Everything related to the project
- Use only when system is severely constrained

## ⚙️ Automation Options

### 1. Cron Job Setup
The cleanup script can set up automatic weekly cleanup:
```bash
./docker-cleanup.sh
# Choose 'y' when prompted for cron setup
```

### 2. Git Hooks
Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
make dev-clean
```

### 3. IDE Integration
Add to your IDE's run configurations:
```bash
# Pre-launch command
make dev-clean

# Post-launch command  
make monitor
```

## 🚨 Troubleshooting

### Problem: Out of Disk Space
```bash
# Emergency cleanup
make emergency-clean

# Check what's using space
docker system df
du -sh ~/.docker/
```

### Problem: Containers Won't Stop
```bash
# Force stop all containers
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)

# Nuclear option
docker system prune -a -f --volumes
```

### Problem: Port Conflicts
```bash
# Check what's using ports
docker ps --format "table {{.Names}}\t{{.Ports}}"

# Clean up networks
docker network prune -f
```

### Problem: Build Failures Due to Cache
```bash
# Clear build cache
docker builder prune -f

# Rebuild without cache
docker-compose build --no-cache
```

## 📈 Performance Tips

### 1. Optimize Docker Desktop Settings
- **Memory**: Allocate 4-8GB (adjust based on system)
- **Disk Image Size**: Set reasonable limit (e.g., 64GB)
- **File Sharing**: Only share necessary directories

### 2. Development Workflow
```bash
# Start clean every morning
make start

# Monitor periodically
make monitor

# Clean up after major changes
make dev-clean
```

### 3. CI/CD Integration
```bash
# In CI pipeline, always start clean
docker-compose down --remove-orphans
docker system prune -f
docker-compose up --build --remove-orphans
```

## 🎯 Best Practices Summary

### ✅ Do's
- Use `make start` instead of `docker-compose up`
- Monitor resources regularly with `make monitor`
- Run `make clean` weekly
- Always use `--remove-orphans` flag
- Set up automated cleanup via cron

### ❌ Don'ts
- Don't accumulate containers without cleanup
- Don't ignore dangling images
- Don't forget to clean build cache
- Don't skip regular monitoring
- Don't manually manage Docker resources without scripts

## 📞 Support

If you encounter issues:

1. **Check system status**: `make status`
2. **Monitor resources**: `make monitor-detail`
3. **Try emergency cleanup**: `make emergency-clean`
4. **Restart Docker Desktop** if problems persist
5. **Check logs**: `/tmp/docker-cleanup.log`

## 🔄 Updates

Keep your Docker management tools updated:
```bash
# Re-run setup after pulling changes
git pull
make setup
```

---

**Remember**: Consistent use of these tools prevents 99% of Docker-related memory and performance issues. Make it part of your daily development routine! 🚀