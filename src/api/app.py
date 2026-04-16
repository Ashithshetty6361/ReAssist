"""
ReAssist FastAPI Server — Production Grade
App factory with modular route registration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone

from src.core.database import init_db
from src.core.config import validate_environment
from src.api.routes import auth, workspaces, pipeline, documents, legacy

# Validate environment on import
try:
    validate_environment()
except EnvironmentError as e:
    print(e)
    exit(1)

app = FastAPI(
    title="ReAssist API",
    description="Research Intelligence Engine — Multi-Agent Pipeline (Production)",
    version="3.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ─── Register route modules ─────────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(workspaces.router)
app.include_router(pipeline.router)
app.include_router(documents.router)
app.include_router(legacy.router)


# ─── Startup / Health ────────────────────────────────────────────────────────

@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "3.1.0",
        "database": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.app:app", host="0.0.0.0", port=8000, reload=True)
