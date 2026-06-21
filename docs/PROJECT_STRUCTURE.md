# Project Structure

```
Starlight-Blogging-Website/
├── .github/workflows/       # CI and deploy verification
├── docs/                    # Documentation
├── starlight-backend/       # Flask API (Python)
│   ├── app.py               # Application entry + routes
│   ├── models.py            # SQLAlchemy models
│   ├── sanitize.py          # HTML sanitization
│   ├── utils.py             # Slugs, excerpts, usernames
│   ├── schema_migrate.py    # Bootstrap schema patches
│   ├── tests/               # pytest suite
│   ├── migrations/          # Alembic migrations
│   ├── requirements.txt
│   └── Procfile             # Gunicorn (Render)
├── starlight-ng/            # Angular frontend (TypeScript)
│   ├── src/app/             # Components, pages, services
│   ├── angular.json
│   ├── package.json
│   ├── proxy.conf.json      # Dev API proxy → localhost:8080
│   └── vercel.json          # Deploy config when rootDir = starlight-ng
├── render.yaml              # Render blueprint (API + Postgres)
├── vercel.json              # Deploy config when rootDir = repo root
└── README.md
```

## Conventions

- **Backend code** lives only under `starlight-backend/`.
- **Frontend code** lives only under `starlight-ng/`.
- **Secrets** go in `.env` files (never committed). See `starlight-backend/.env.example`.
- **Build output** (`dist/`, `node_modules/`, `__pycache__/`) is gitignored.
- **Local databases** (`*.db`) and **session files** are gitignored.

## Development commands

| Task | Command | Directory |
|------|---------|-------------|
| Run API | `python app.py` | `starlight-backend/` |
| Run UI | `npm start` | `starlight-ng/` |
| Production build | `npm run build:prod` | `starlight-ng/` |
| Backend tests | `pytest tests/ -q` | `starlight-backend/` |

## Deployment

- **Frontend:** Vercel (`vercel.json` at repo root or `starlight-ng/vercel.json`)
- **Backend:** Render (`render.yaml`)
- **CI:** GitHub Actions on push to `main` / `develop`
