#!/bin/bash
# Fix Docker dependencies issue

echo "🔧 Fixing Docker dependencies..."

# Remove problematic lock file
rm -f package-lock.json

# Clean npm cache
echo "📦 Cleaning npm cache..."
npm cache clean --force 2>/dev/null || true

# Remove node_modules if it exists
if [ -d "node_modules" ]; then
    echo "🗑️ Removing node_modules..."
    rm -rf node_modules
fi

# Regenerate package-lock.json with Node 20 compatibility
echo "📝 Regenerating package-lock.json..."
npm install --package-lock-only

# Install dependencies
echo "⬇️ Installing dependencies..."
npm install

echo "✅ Dependencies fixed! Docker build should now work."
echo "💡 Run: docker-compose up --build"