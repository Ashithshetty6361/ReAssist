# ⚙️ ReAssist — Backend Architecture & Code Walkthrough Guide

> **Core Technology Stack:** Python 3.11+, FastAPI, LangGraph, SQLAlchemy 2.0 (SQLite/WAL), ChromaDB, Ollama / AWS Bedrock / OpenAI SDK  
> **Backend Root Folder:** [`src/`](file:///c:/Users/shett/MIT_BTech/ReAssist_Project/src/)  
> **Standalone Run Script:** Double-click [`start_backend.bat`](file:///c:/Users/shett/MIT_BTech/ReAssist_Project/start_backend.bat) (Starts FastAPI on port 8000/8001 with interactive docs at `/docs`)

---

## 📂 Backend Directory Structure

```
ReAssist_Project/
├── src/
│   ├── api/                    <── FastAPI Routes, Schemas & Serialization
│   │   ├── routes/
│   │   │   ├── auth.py         <── JWT Registration, Login, Current User
│   │   │   ├── pipeline.py     <── Async Pipeline Execution (BackgroundTasks)
│   │   │   ├── observability.py<── Telemetry & Run History API
│   │   │   ├── documents.py    <── PDF & Vector Upload Endpoints
│   │   │   ├── export.py       <── Export Dossier (Markdown, BibTeX, JSON)
│   │   │   ├── workspaces.py   <── Multi-Tenant Workspace Management
│   │   │   └── legacy.py       <── Sandbox Benchmark (/simulate_comparison)
│   │   ├── app.py              <── FastAPI App Initialization & CORS Middleware
│   │   └── schemas.py          <── Pydantic Request/Response API Schemas
│   │
│   ├── core/                   <── Infrastructure & Foundations
│   │   ├── auth.py             <── Bcrypt, JWT Tokens & Demo User Auto-Fallback
│   │   ├── llm_provider.py     <── Universal LLM Client (OpenAI/Bedrock/Ollama)
│   │   ├── config.py           <── Environment Settings & Model Defaults
│   │   ├── database.py         <── SQLAlchemy Engine & WAL Session Factory
│   │   └── storage.py          <── S3 & Local File Storage Abstraction
│   │
│   ├── pipeline/               <── Multi-Agent State Machine & Orchestrator
│   │   ├── graph_builder.py    <── LangGraph StateGraph, Edges & Cyclic Routers
│   │   └── orchestrator.py     <── RootAgent Facade, Query & PDF Modes
│   │
│   ├── agents/                 <── 11 Specialized AI Agents
│   │   ├── search_agent.py     <── arXiv & Semantic Scholar Ingestion
│   │   ├── summarize_agent.py  <── 2,000-token Chunked Summarizer
│   │   ├── synthesize_agent.py <── Cross-Paper Thematic Knowledge Synthesis
│   │   ├── gap_finder_agent.py <── Research Gaps & Blind Spots
│   │   ├── idea_generator_agent.py <── 5 Testable Novel Hypotheses
│   │   ├── technique_agent.py  <── Mathematical Formulations & Benchmarks
│   │   ├── guidance_agent.py   <── Phased Execution Milestones
│   │   ├── relevance_grader.py <── Binary Quality Gate (T=0.0)
│   │   ├── query_rewriter.py   <── Academic Query Reformulator
│   │   ├── web_search_agent.py <── Tavily Web Search Fallback
│   │   └── answer_verifier.py  <── Hallucination Guard (T=0.0)
│   │
│   ├── router/
│   │   └── agent_router.py     <── <2ms Lexical Heuristic Cost Router
│   │
│   ├── services/               <── Business Logic Layer
│   │   ├── observability_service.py <── Run History & Telemetry Aggregator
│   │   ├── rag_service.py      <── ChromaDB Semantic Search Service
│   │   └── research_service.py <── Literature Orchestration Service
│   │
│   ├── utils/                  <── Utility Engines
│   │   ├── token_counter.py    <── Per-Agent Token & Cost Tracking Engine
│   │   ├── logger.py           <── Structured JSON Logging Engine
│   │   ├── context_slicer.py   <── Dynamic Context Slicing (slice_context)
│   │   └── json_parser.py      <── 4-Stage Self-Healing JSON Parser
│   │
│   └── models/
│       ├── state.py            <── PipelineState (TypedDict) Contract
│       ├── agent_outputs.py    <── Pydantic Output Validation Models
│       └── orm.py              <── SQLAlchemy Relational Database Tables
│
└── evaluation/                 <── Benchmark & Reliability Suites
    ├── evaluator.py            <── 3-Way Baseline Evaluator (Coverage/Specificity)
    └── stability_tester.py     <── Multi-Run 99.2% Schema Compliance Tester
```

---

## 🎯 5 Key Backend Subsystems: What to Show in an Interview

### 1. 🔐 Authentication & Demo Auto-Fallback
* **File:** [`src/core/auth.py`](file:///c:/Users/shett/MIT_BTech/ReAssist_Project/src/core/auth.py#L57-L83)
* **What to Highlight:** Look at `get_current_user()`. If a request arrives without a JWT token, it does **not** fail with HTTP 401; instead, it automatically creates or fetches a default `demo@reassist.ai` user.
* **Why to Mention:** Eliminates authentication friction during live presentations, jury evaluations, and demo runs while maintaining strict foreign key constraints in the database.

---

### 2. 🤖 LLM Client Abstraction & Model Calling
* **File:** [`src/core/llm_provider.py`](file:///c:/Users/shett/MIT_BTech/ReAssist_Project/src/core/llm_provider.py#L178-L228)
* **What to Highlight:**
  * `get_llm_client()`: Cached factory function using `@lru_cache(maxsize=4)`.
  * Dynamically switches between:
    * **Ollama:** `http://localhost:11434/v1` (air-gapped local execution, $0 cost).
    * **AWS Bedrock:** Uses `BedrockClientWrapper` to map standard OpenAI completion payloads into Bedrock's native `converse()` API via `boto3`.
    * **OpenAI:** Uses standard OpenAI client.
  * **Zero Agent Vendor Lock-in:** None of the 11 agents contain `if/else` checks for specific providers; all agents call `self.client.chat.completions.create(...)`.

---

### 3. 🔀 Multi-Agent Orchestration & Context Slicing
* **File 1:** [`src/pipeline/graph_builder.py`](file:///c:/Users/shett/MIT_BTech/ReAssist_Project/src/pipeline/graph_builder.py#L27-L45)
  * Assembles the compiled LangGraph `StateGraph(PipelineState)`.
  * Demonstrates cyclic edge routers: `grade_router` $\rightarrow$ `rewrite_router` $\rightarrow$ `web_search_router`.
  * Shows `_run_with_retry()`: Exponential backoff sleeping $(2^{\text{attempt}} \times 5)$ seconds on `RateLimitError`.
* **File 2:** [`src/utils/context_slicer.py`](file:///c:/Users/shett/MIT_BTech/ReAssist_Project/src/utils/context_slicer.py#L7-L29)
  * Shows `slice_context(state, required_inputs)`.
  * Demonstrates how `GapFinderAgent` only receives `synthesis`, dropping 15,000 tokens of raw papers and reducing cascade tokens by **52%**.

---

### 4. 📊 Metrics & Cost Calculation
* **Token Usage & Costs:** [`src/utils/token_counter.py`](file:///c:/Users/shett/MIT_BTech/ReAssist_Project/src/utils/token_counter.py#L15-L71) computes input/output tokens and dollar costs per node, identifying `slowest_agent` and `most_expensive_agent`.
* **Complexity & Cost Savings:** [`src/router/agent_router.py`](file:///c:/Users/shett/MIT_BTech/ReAssist_Project/src/router/agent_router.py#L100-L190) executes 6 lexical heuristic signals in **$< 2$ ms** with zero tokens, saving 68%–75% of API costs.
* **Schema Compliance (99.2%):** [`evaluation/stability_tester.py`](file:///c:/Users/shett/MIT_BTech/ReAssist_Project/evaluation/stability_tester.py#L48-L103) validates outputs across repeated runs against Pydantic models in [`src/models/agent_outputs.py`](file:///c:/Users/shett/MIT_BTech/ReAssist_Project/src/models/agent_outputs.py).

---

### 5. 🧪 Demo & Sandbox Calculation Backend
* **File:** [`src/api/routes/legacy.py`](file:///c:/Users/shett/MIT_BTech/ReAssist_Project/src/api/routes/legacy.py#L67-L130)
* **What to Highlight:** `@router.post("/simulate_comparison")` dispatches an asynchronous background task comparing the **Monolithic CoT baseline** against the **Multi-Agent pipeline**, calculating quality deltas and latency comparisons on the fly.

