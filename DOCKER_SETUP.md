# Docker Setup Guide

## Quick Start

```bash
# Build and start all services
docker compose up --build

# Or use the test script
./test-docker.sh
```

## Services

- **Frontend**: http://localhost:4200 (Angular 19)
- **Backend**: http://localhost:8000 (FastAPI)
- **Cypress E2E**: Run with `docker compose run --rm cypress`

## Development Mode

```bash
# Start in detached mode
docker compose up --build -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

## Troubleshooting

### Frontend Build Issues

If you see npm package version errors:

1. Check `package.json` for correct versions
2. Delete `node_modules` and `package-lock.json`
3. Rebuild: `docker compose build --no-cache frontend`

### Backend Issues

If backend health checks fail:

1. Check backend logs: `docker compose logs backend`
2. Verify environment variables in `backend/.env`
3. Ensure all required environment variables are set

### PDF Viewer Issues

We've switched from `ngx-extended-pdf-viewer` to `ng2-pdf-viewer` for better compatibility with Angular 19.

## Environment Variables

Copy the example files and configure:

```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys
```

Required variables:
- `CHUTES_AI_API_KEY`
- `MISTRAL_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`

## Performance Tips

- Use `docker compose up --build` only when code changes
- Use `docker compose up` for quick restarts
- Use `docker compose build --no-cache` to force rebuild