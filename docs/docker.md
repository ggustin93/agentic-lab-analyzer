# Docker guide

## Quick start

```bash
cp backend/.env.example backend/.env   # then fill in the two AI keys (local mode needs nothing else)
docker compose up --build
```

Local-mode data persists on the host via the `./backend` bind mount
(`backend/data/`, `backend/uploads/`).

| Service | URL |
|---|---|
| Frontend (Angular) | http://localhost:4200 |
| Backend (FastAPI, Swagger UI) | http://localhost:8000/docs |
| Cypress E2E | `docker compose run --rm cypress` |

## Common commands

```bash
docker compose up --build -d    # detached
docker compose logs -f          # follow logs
docker compose down             # stop
npm run test:all:docker         # full containerized test run
```

`make start` / `make clean` / `make monitor` wrap the cleanup and monitoring
scripts in [`scripts/`](../scripts/); see [`scripts/README.md`](../scripts/README.md).

## Troubleshooting

- **Frontend build fails on npm versions**: remove `node_modules` and
  `package-lock.json`, then `docker compose build --no-cache frontend`.
- **Backend health check fails**: `docker compose logs backend`, then verify
  every variable in `backend/.env` is set (see README section 7.2).
- **Stale cache issues**: `docker builder prune -f` and rebuild with
  `--no-cache`.
