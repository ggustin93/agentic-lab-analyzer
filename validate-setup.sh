#!/bin/bash

echo "🔍 Validating project setup..."

# Check if package.json exists and has correct PDF viewer
if [ -f "package.json" ]; then
    echo "✅ package.json found"
    
    if grep -q "ng2-pdf-viewer" package.json; then
        echo "✅ ng2-pdf-viewer dependency found"
    elif grep -q "ngx-extended-pdf-viewer" package.json; then
        echo "❌ ngx-extended-pdf-viewer found (incompatible with Angular 19)"
        echo "   Run: sed -i '' 's/ngx-extended-pdf-viewer/ng2-pdf-viewer/g' package.json"
    else
        echo "⚠️  No PDF viewer dependency found"
    fi
    
    if grep -q '"@angular/core": "\^19' package.json; then
        echo "✅ Angular 19 detected"
    else
        echo "⚠️  Angular version might not be 19"
    fi
else
    echo "❌ package.json not found"
fi

# Check if Docker files exist
if [ -f "docker-compose.yml" ]; then
    echo "✅ docker-compose.yml found"
else
    echo "❌ docker-compose.yml not found"
fi

if [ -f "Dockerfile.frontend" ]; then
    echo "✅ Dockerfile.frontend found"
else
    echo "❌ Dockerfile.frontend not found"
fi

if [ -f "backend/Dockerfile.backend" ]; then
    echo "✅ Dockerfile.backend found"
else
    echo "❌ Dockerfile.backend not found"
fi

# Check if backend .env.example exists
if [ -f "backend/.env.example" ]; then
    echo "✅ backend/.env.example found"
    if [ -f "backend/.env" ]; then
        echo "✅ backend/.env found"
    else
        echo "⚠️  backend/.env not found - copy from .env.example"
    fi
else
    echo "❌ backend/.env.example not found"
fi

# Check angular.json for PDF viewer assets
if [ -f "angular.json" ]; then
    if grep -q "ngx-extended-pdf-viewer" angular.json; then
        echo "❌ angular.json still references ngx-extended-pdf-viewer assets"
        echo "   This has been fixed in the current version"
    else
        echo "✅ angular.json looks clean"
    fi
fi

echo ""
echo "🚀 Ready to test Docker build:"
echo "   docker compose up --build"
echo ""
echo "📚 For troubleshooting, see DOCKER_SETUP.md"