# API Reference

## Authentication (`/auth`)
- `POST /auth/register` — Registers a new User
- `POST /auth/login` — Returns `access_token`

## Workspaces (`/workspaces`)
- `POST /workspaces` — Create new workspace project
- `GET /workspaces` — List workspaces owned by user
- `POST /workspaces/{id}/messages` — Append conversation message

## Pipeline (`/workspaces/{id}/execute`)
- `POST /workspaces/{id}/execute` — Run adaptive LangGraph research pipeline (Async)
- `GET /executions/{id}` — Fetch pipeline status and payload

## Documents & RAG (`/workspaces/{id}/documents`)
- `POST /workspaces/{id}/documents` — Upload and ingest PDF into Vector DB
- `POST /workspaces/{id}/rag-query` — Retrieve specific chunked info from ingested docs
