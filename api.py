"""
ReAssist FastAPI Server
Exposes the pipeline and router as HTTP endpoints
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import uuid
import asyncio
from datetime import datetime

from root_agent import create_root_agent
from router import create_router
from config import validate_environment, DEFAULT_MODEL, MAX_PAPERS

# Validate environment on startup
try:
    validate_environment()
except EnvironmentError as e:
    print(e)
    exit(1)

app = FastAPI(
    title="ReAssist API",
    description="Research Intelligence Engine — Multi-Agent Pipeline",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# In-memory job store (use Redis in production)
jobs = {}


class QueryRequest(BaseModel):
    query: str
    model: Optional[str] = DEFAULT_MODEL
    max_papers: Optional[int] = MAX_PAPERS
    use_router: Optional[bool] = True


class RouterRequest(BaseModel):
    query: str
    model: Optional[str] = DEFAULT_MODEL


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }


@app.post("/route")
def route_query(request: RouterRequest):
    """Get routing decision without running the pipeline"""
    router = create_router(model=request.model)
    result = router.route(request.query)
    router.log_decision(request.query, result)
    return result


@app.post("/analyze")
async def analyze_query(request: QueryRequest, background_tasks: BackgroundTasks):
    """
    Start a research analysis pipeline.
    Returns a job_id immediately. Poll /jobs/{job_id} for results.
    """
    job_id = uuid.uuid4().hex[:8]
    jobs[job_id] = {
        "status": "running",
        "job_id": job_id,
        "query": request.query,
        "started_at": datetime.now().isoformat(),
        "result": None,
        "error": None
    }

    def run_pipeline():
        try:
            # Router decision
            if request.use_router:
                router = create_router(model=request.model)
                routing = router.route(request.query)
                router.log_decision(request.query, routing)
                jobs[job_id]['routing_decision'] = routing

            agent = create_root_agent(
                model=request.model,
                max_papers=request.max_papers
            )
            result = agent.execute_pipeline(query=request.query)
            jobs[job_id]['status'] = 'completed'
            jobs[job_id]['result'] = result
            jobs[job_id]['completed_at'] = datetime.now().isoformat()
        except Exception as e:
            jobs[job_id]['status'] = 'failed'
            jobs[job_id]['error'] = str(e)

    background_tasks.add_task(run_pipeline)
    return {"job_id": job_id, "status": "running"}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    """Poll for pipeline results"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


@app.get("/stats/router")
def router_stats():
    """Get AgenticOps routing statistics"""
    router = create_router()
    return router.get_stats()


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
