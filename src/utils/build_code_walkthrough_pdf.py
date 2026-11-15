"""
ReAssist — Codebase Architecture & Technical Walkthrough PDF Generator
======================================================================
File: src/utils/build_code_walkthrough_pdf.py

Generates an executive-grade PDF report classifying the codebase into:
  - Tier 1: Mission-Critical Core Code (Where stored + line-by-line explanation)
  - Tier 2: Supporting Services & Orchestration Layer
  - Tier 3: Ancillary Utilities & Boilerplate (Explanation of why they exist)
  - 3-Minute Examiner / Viva Walkthrough Presentation Script
"""

import os
import subprocess
import shutil

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>ReAssist: Codebase Architecture & Technical Walkthrough Guide</title>
<style>
  @page {
    size: A4;
    margin: 16mm 14mm 16mm 14mm;
  }
  @page:first {
    margin: 0;
  }
  * {
    box-sizing: border-box;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1f2328;
    line-height: 1.5;
    font-size: 9.5pt;
    margin: 0;
    padding: 0;
    background: #ffffff;
  }

  /* ─── COVER PAGE ─────────────────────────────────────────── */
  .cover-page {
    width: 100vw;
    height: 100vh;
    min-height: 297mm;
    padding: 35mm 22mm 22mm 22mm;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: linear-gradient(135deg, #0d1117 0%, #161b22 60%, #061c36 100%);
    color: #ffffff;
    page-break-after: always;
  }
  .cover-badge {
    display: inline-block;
    background: rgba(88, 166, 255, 0.15);
    border: 1px solid #58a6ff;
    color: #58a6ff;
    font-size: 8.5pt;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 20px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 18px;
  }
  .cover-title {
    font-size: 28pt;
    font-weight: 800;
    line-height: 1.15;
    margin: 0 0 14px 0;
    letter-spacing: -0.5px;
    color: #ffffff;
  }
  .cover-title span {
    color: #58a6ff;
  }
  .cover-subtitle {
    font-size: 13pt;
    font-weight: 400;
    color: #8b949e;
    line-height: 1.4;
    max-width: 650px;
    margin: 0 0 25px 0;
  }
  .cover-metrics {
    display: flex;
    gap: 15px;
    margin-top: 15px;
  }
  .metric-box {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    padding: 12px 16px;
    flex: 1;
  }
  .metric-val {
    font-size: 16pt;
    font-weight: 800;
    color: #3fb950;
    margin-bottom: 2px;
    font-family: 'Cascadia Code', Consolas, monospace;
  }
  .metric-lbl {
    font-size: 7.5pt;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #8b949e;
  }
  .cover-footer {
    border-top: 1px solid rgba(255, 255, 255, 0.15);
    padding-top: 18px;
    display: flex;
    justify-content: space-between;
    font-size: 8.5pt;
    color: #8b949e;
  }
  .cover-footer strong {
    color: #f0f6fc;
  }

  /* ─── TYPOGRAPHY & LAYOUT ────────────────────────────────── */
  .page {
    padding: 0;
  }
  .page-break {
    page-break-before: always;
  }
  h1 {
    font-size: 14pt;
    font-weight: 800;
    color: #0969da;
    border-bottom: 2px solid #eaeef2;
    padding-bottom: 5px;
    margin-top: 20px;
    margin-bottom: 10px;
    letter-spacing: -0.3px;
    page-break-after: avoid;
  }
  h2 {
    font-size: 11pt;
    font-weight: 700;
    color: #1f2328;
    margin-top: 14px;
    margin-bottom: 6px;
    page-break-after: avoid;
  }
  h3 {
    font-size: 9.5pt;
    font-weight: 700;
    color: #24292f;
    margin-top: 10px;
    margin-bottom: 3px;
    page-break-after: avoid;
  }
  p {
    margin: 0 0 8px 0;
    text-align: justify;
  }
  ul, ol {
    margin: 0 0 8px 0;
    padding-left: 18px;
  }
  li {
    margin-bottom: 3px;
  }
  code {
    font-family: 'Cascadia Code', Consolas, monospace;
    font-size: 8pt;
    background: #f6f8fa;
    border: 1px solid #d0d7de;
    padding: 1px 4px;
    border-radius: 4px;
    color: #0969da;
  }
  pre {
    background: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 8px 10px;
    font-family: 'Cascadia Code', Consolas, monospace;
    font-size: 7.2pt;
    line-height: 1.35;
    overflow-x: auto;
    margin: 6px 0 10px 0;
    page-break-inside: avoid;
    white-space: pre-wrap;
    color: #24292f;
  }

  /* ─── TIERS & BADGES ─────────────────────────────────────── */
  .badge-tier1 {
    display: inline-block;
    background: #dafbe1;
    color: #1a7f37;
    border: 1px solid #2da44e;
    font-size: 7pt;
    font-weight: 800;
    padding: 1px 6px;
    border-radius: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .badge-tier2 {
    display: inline-block;
    background: #ddf4ff;
    color: #0969da;
    border: 1px solid #54aeff;
    font-size: 7pt;
    font-weight: 800;
    padding: 1px 6px;
    border-radius: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .badge-tier3 {
    display: inline-block;
    background: #fff8c5;
    color: #9a6700;
    border: 1px solid #d4a72c;
    font-size: 7pt;
    font-weight: 800;
    padding: 1px 6px;
    border-radius: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  /* ─── TABLES ─────────────────────────────────────────────── */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0 14px 0;
    font-size: 8.5pt;
    page-break-inside: avoid;
  }
  th {
    background: #0969da;
    color: #ffffff;
    font-weight: 600;
    text-align: left;
    padding: 6px 8px;
    border: 1px solid #0969da;
    font-size: 8pt;
    letter-spacing: 0.3px;
  }
  td {
    padding: 6px 8px;
    border: 1px solid #d0d7de;
    vertical-align: top;
  }
  tr:nth-child(even) td {
    background: #f6f8fa;
  }

  /* ─── FILE CARDS ─────────────────────────────────────────── */
  .file-card {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-left: 4px solid #0969da;
    border-radius: 0 6px 6px 0;
    padding: 8px 12px;
    margin-bottom: 10px;
    page-break-inside: avoid;
  }
  .file-card.tier1 { border-left-color: #1a7f37; }
  .file-card.tier2 { border-left-color: #0969da; }
  .file-card.tier3 { border-left-color: #d4a72c; }
  .file-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
  }
  .file-title {
    font-weight: 700;
    font-size: 9pt;
    color: #1f2328;
    font-family: 'Cascadia Code', Consolas, monospace;
  }
  .file-purpose {
    font-size: 8.5pt;
    color: #57606a;
    margin-bottom: 4px;
  }
  .file-viva {
    background: #f6f8fa;
    border-radius: 4px;
    padding: 6px 8px;
    font-size: 8pt;
    color: #24292f;
    border-left: 2px solid #58a6ff;
    margin-top: 4px;
  }

  /* ─── RUNNING FOOTER ─────────────────────────────────────── */
  .doc-footer {
    border-top: 1px solid #d0d7de;
    margin-top: 16px;
    padding-top: 6px;
    display: flex;
    justify-content: space-between;
    font-size: 7.5pt;
    color: #57606a;
  }
</style>
</head>
<body>

<!-- ═════════════════════════════════════════════════════════════════ -->
<!-- COVER PAGE                                                       -->
<!-- ═════════════════════════════════════════════════════════════════ -->
<div class="cover-page">
  <div class="cover-header">
    <div class="cover-badge">ENGINEERING WALKTHROUGH & CODEBASE MAP</div>
    <div class="cover-title">ReAssist: <span>Codebase Architecture</span><br>& Technical Walkthrough Guide</div>
    <div class="cover-subtitle">
      A structured triage and presentation guide: identifying mission-critical core engines,
      supporting service architectures, and ancillary utilities for technical interviews and viva voce defense.
    </div>
    <div class="cover-metrics">
      <div class="metric-box">
        <div class="metric-val">Tier 1</div>
        <div class="metric-lbl">7 Mission-Critical Files</div>
      </div>
      <div class="metric-box">
        <div class="metric-val">Tier 2</div>
        <div class="metric-lbl">4 Supporting Services</div>
      </div>
      <div class="metric-box">
        <div class="metric-val">Tier 3</div>
        <div class="metric-lbl">6 Ancillary Utilities</div>
      </div>
      <div class="metric-box">
        <div class="metric-val">100%</div>
        <div class="metric-lbl">22 Unit Tests Passing</div>
      </div>
    </div>
  </div>

  <div class="cover-footer">
    <div><strong>Project:</strong> ReAssist Autonomous Research Engine</div>
    <div><strong>Target Audience:</strong> Technical Interviewers, Project Examiners, Code Reviewers</div>
    <div><strong>Author:</strong> Ashith Shetty</div>
  </div>
</div>

<!-- ═════════════════════════════════════════════════════════════════ -->
<!-- CHAPTER 1: QUICK REFERENCE CODEBASE MATRIX                       -->
<!-- ═════════════════════════════════════════════════════════════════ -->
<div class="page">
  <h1>1. Codebase Classification Matrix (At a Glance)</h1>
  <p>
    When an examiner asks: <em>"Walk me through your code,"</em> do <strong>not</strong> open files randomly. 
    Focus 80% of your time on <strong>Tier 1</strong> files. Use the matrix below to guide your presentation:
  </p>

  <table>
    <thead>
      <tr>
        <th style="width: 12%;">Priority</th>
        <th style="width: 32%;">File Path</th>
        <th style="width: 26%;">Architectural Responsibility</th>
        <th style="width: 30%;">What to Highlight to Examiner</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><span class="badge-tier1">Tier 1 (Core)</span></td>
        <td><code>src/pipeline/graph_builder.py</code></td>
        <td>LangGraph StateGraph & CRAG cyclic loops</td>
        <td>Cyclic edges, <code>_run_with_retry</code> exponential backoff, context slicing</td>
      </tr>
      <tr>
        <td><span class="badge-tier1">Tier 1 (Core)</span></td>
        <td><code>src/router/agent_router.py</code></td>
        <td>AgenticOps zero-LLM complexity router</td>
        <td>6 lexical signals, &lt;2ms latency, ~75% cost reduction</td>
      </tr>
      <tr>
        <td><span class="badge-tier1">Tier 1 (Core)</span></td>
        <td><code>src/api/routes/pipeline.py</code></td>
        <td>FastAPI async execution & polling routes</td>
        <td><code>BackgroundTasks</code> &lt;15ms dispatch, multi-tenant workspace isolation</td>
      </tr>
      <tr>
        <td><span class="badge-tier1">Tier 1 (Core)</span></td>
        <td><code>src/agents/search_agent.py</code></td>
        <td>Paper discovery & API failover cascade</td>
        <td>arXiv &rarr; Semantic Scholar &rarr; Tavily fallback chain</td>
      </tr>
      <tr>
        <td><span class="badge-tier1">Tier 1 (Core)</span></td>
        <td><code>src/agents/answer_verifier.py</code></td>
        <td>Hallucination guardrail & citation check</td>
        <td>Temperature=0.0 auditing of synthesis against source abstracts</td>
      </tr>
      <tr>
        <td><span class="badge-tier1">Tier 1 (Core)</span></td>
        <td><code>src/rag/retriever.py</code></td>
        <td>ChromaDB vector store & HNSW indexing</td>
        <td>Workspace-isolated collections (<code>ws_{id}</code>), Cosine similarity</td>
      </tr>
      <tr>
        <td><span class="badge-tier1">Tier 1 (Core)</span></td>
        <td><code>src/core/llm_provider.py</code></td>
        <td>Unified multi-provider client adapter & factory</td>
        <td>Dynamic provider switch (<code>LLM_PROVIDER</code>), Ollama /v1 endpoint, Bedrock Adapter, @lru_cache</td>
      </tr>

      <tr>
        <td><span class="badge-tier2">Tier 2 (Service)</span></td>
        <td><code>src/services/research_service.py</code></td>
        <td>Service orchestration & DB telemetry</td>
        <td>Decouples business logic from REST API; saves traces and chat memory</td>
      </tr>
      <tr>
        <td><span class="badge-tier2">Tier 2 (Service)</span></td>
        <td><code>src/rag/document_processor.py</code></td>
        <td>PDF text parsing & chunking</td>
        <td><code>RecursiveCharacterTextSplitter</code> (1,000 chars, 150 overlap)</td>
      </tr>
      <tr>
        <td><span class="badge-tier2">Tier 2 (Service)</span></td>
        <td><code>src/core/database.py</code></td>
        <td>SQLAlchemy 2.0 ORM engine</td>
        <td>SQLite in WAL mode for concurrency, connection pooling</td>
      </tr>
      <tr>
        <td><span class="badge-tier2">Tier 2 (Service)</span></td>
        <td><code>src/core/auth.py</code></td>
        <td>JWT Bearer security & demo fallback</td>
        <td>Auto-resolves default demo user to eliminate demo friction</td>
      </tr>

      <tr>
        <td><span class="badge-tier3">Tier 3 (Utility)</span></td>
        <td><code>src/utils/logger.py</code></td>
        <td>Rotating logger & JSON traces</td>
        <td>Captures per-node latency and telemetry in <code>logs/runs/</code></td>
      </tr>
      <tr>
        <td><span class="badge-tier3">Tier 3 (Utility)</span></td>
        <td><code>src/utils/pdf_parser.py</code></td>
        <td>PyPDF2 / pdfplumber fallback helper</td>
        <td>Handles raw binary PDF extraction for manual uploads</td>
      </tr>
      <tr>
        <td><span class="badge-tier3">Tier 3 (Utility)</span></td>
        <td><code>src/services/export_service.py</code></td>
        <td>Markdown & BibTeX dossier generator</td>
        <td>Formats completed research dossiers for Overleaf and LaTeX export</td>
      </tr>
      <tr>
        <td><span class="badge-tier3">Tier 3 (Utility)</span></td>
        <td><code>src/api/serializers.py</code></td>
        <td>ORM to Pydantic JSON serializers</td>
        <td>Standard boilerplate mapping SQLAlchemy models to REST JSON payloads</td>
      </tr>
      <tr>
        <td><span class="badge-tier3">Tier 3 (Utility)</span></td>
        <td><code>src/api/routes/legacy.py</code></td>
        <td>Deprecated prototype REST endpoints</td>
        <td>Preserved for backward-compatibility with earlier Streamlit UI</td>
      </tr>
      <tr>
        <td><span class="badge-tier3">Tier 3 (Utility)</span></td>
        <td><code>evaluation/stability_tester.py</code></td>
        <td>Automated testing & robustness harness</td>
        <td>Runs repeat queries to verify zero rate-limit crashes and latency bounds</td>
      </tr>
    </tbody>
  </table>

  <div class="doc-footer">
    <div>ReAssist Codebase Walkthrough Guide &bull; Chapter 1: Quick Reference Matrix</div>
    <div>Production v3.2.0</div>
  </div>
</div>

<!-- ═════════════════════════════════════════════════════════════════ -->
<!-- CHAPTER 2: TIER 1 MISSION-CRITICAL CODE DEEP DIVE                -->
<!-- ═════════════════════════════════════════════════════════════════ -->
<div class="page-break"></div>
<div class="page">
  <h1>2. Tier 1: Mission-Critical Core Engines (Show These First)</h1>
  <p>
    These 7 files represent the primary architectural contributions of ReAssist. If you are asked to walk through the codebase,
    open these files and explain the exact mechanisms shown below.
  </p>

  <!-- FILE 1 -->
  <div class="file-card tier1">
    <div class="file-header">
      <span class="file-title">1. src/pipeline/graph_builder.py</span>
      <span class="badge-tier1">Tier 1: Core</span>
    </div>
    <div class="file-purpose"><strong>Purpose:</strong> Assembles the 11-agent declarative LangGraph state machine with cyclic feedback loops and exponential backoff retry.</div>
    <div class="file-viva">
      <strong>Viva / Walkthrough Explanation:</strong> "This is the core state machine. Notice lines 71–90 where <code>_run_with_retry</code> wraps every node with exponential backoff on <code>RateLimitError</code> (sleeping 2^attempt * 5 seconds). Notice lines 365–385 where <code>grade_router</code> and <code>rewrite_router</code> implement the Corrective RAG (CRAG) loop: if verified papers &lt; 3, it loops back to <code>search_node</code> up to 2 times, then falls back to Tavily web search."
    </div>
  </div>
  <pre>
# src/pipeline/graph_builder.py - Fault-Tolerance & Corrective RAG Routers
def _run_with_retry(agent, agent_name, input_data, max_retries=2):
    for attempt in range(max_retries + 1):
        try:
            return agent.run(input_data)
        except Exception as e:
            if attempt < max_retries and isinstance(e, openai.RateLimitError):
                time.sleep((2 ** attempt) * 5)  # 5s, 10s exponential backoff
    raise RuntimeError(f"Agent '{agent_name}' failed after {max_retries + 1} attempts")

def grade_router(state: PipelineState) -> str:
    # If relevant papers >= 3 -> summarize; else -> rewrite query
    return "summarize_node" if len(state.get("papers", [])) >= RELEVANCE_THRESHOLD else "rewrite_node"

def rewrite_router(state: PipelineState) -> str:
    # If attempts left -> loop back to search; if exhausted -> fallback to web
    return "search_node" if state.get("rewrite_count", 0) < MAX_QUERY_REWRITES else "web_search_node"
  </pre>

  <!-- FILE 2 -->
  <div class="file-card tier1">
    <div class="file-header">
      <span class="file-title">2. src/router/agent_router.py</span>
      <span class="badge-tier1">Tier 1: Core</span>
    </div>
    <div class="file-purpose"><strong>Purpose:</strong> Zero-LLM-overhead lexical heuristic router that classifies query complexity to save ~75% in inference costs.</div>
    <div class="file-viva">
      <strong>Viva / Walkthrough Explanation:</strong> "Calling an LLM to decide whether to call an LLM defeats cost savings. This router computes 6 algorithmic signals in under 2ms with zero token cost. If complexity &le; 4, it dispatches to the single-shot CoT baseline (9s, $0.0015); if &ge; 5, it invokes the 11-agent LangGraph pipeline (35s, $0.0060)."
    </div>
  </div>
  <pre>
# src/router/agent_router.py - Pure Lexical Complexity Scoring
def route(self, query: str) -> dict:
    q = query.lower()
    complexity = sum([any(w in q for w in self.DOMAIN_JARGON), len(query.split()) > 8, any(w in q for w in self.COMPARISON_WORDS)])
    precision = sum([any(w in q for w in self.RECENCY_WORDS), any(w in q for w in self.SURVEY_WORDS), len(set(q.split())) < 6])
    total = complexity + precision
    decision = "cot" if total <= 4 else "multi_agent"
    tier = ModelTier.TIER_1_FAST if total <= 2 else (ModelTier.TIER_2_BALANCED if total <= 4 else ModelTier.TIER_3_FRONTIER)
    return {"decision": decision, "tier": tier.value, "score": total, "cost_saved": round(0.0060 - 0.0015, 4)}
  </pre>

  <div class="doc-footer">
    <div>ReAssist Codebase Walkthrough Guide &bull; Chapter 2: Tier 1 Core Engines (Part 1)</div>
    <div>Production v3.2.0</div>
  </div>
</div>

<!-- ═════════════════════════════════════════════════════════════════ -->
<!-- CHAPTER 2 (CONTINUED): TIER 1 CORE FILES                         -->
<!-- ═════════════════════════════════════════════════════════════════ -->
<div class="page-break"></div>
<div class="page">
  <!-- FILE 3 -->
  <div class="file-card tier1">
    <div class="file-header">
      <span class="file-title">3. src/api/routes/pipeline.py</span>
      <span class="badge-tier1">Tier 1: Core</span>
    </div>
    <div class="file-purpose"><strong>Purpose:</strong> Asynchronous non-blocking API endpoint decoupling client HTTP sockets from long-running LangGraph pipelines.</div>
    <div class="file-viva">
      <strong>Viva / Walkthrough Explanation:</strong> "Running 11 agents takes ~30 seconds, which would cause browser HTTP timeouts. In <code>execute_pipeline</code>, we create a <code>running</code> record in the DB and schedule the job onto FastAPI's <code>BackgroundTasks</code>. The endpoint returns in &lt;15ms with an <code>execution_id</code>, and the frontend polls <code>/api/executions/{id}</code>."
    </div>
  </div>
  <pre>
# src/api/routes/pipeline.py - Non-Blocking Asynchronous Job Dispatch
@router.post("/workspaces/{workspace_id}/execute")
def execute_pipeline(workspace_id: str, req: QueryRequest, background_tasks: BackgroundTasks, ...):
    ws = _get_workspace_or_404(workspace_id, user.id, db)
    execution = PipelineExecution(workspace_id=ws.id, query=req.query, status="running")
    db.add(execution); db.commit()

    def run_pipeline():
        pdb = SessionLocal()  # Isolated DB session per background worker thread
        try:
            get_research_service().run_pipeline_sync(workspace_id=ws.id, execution_id=execution.id, ...)
        finally:
            pdb.close()

    background_tasks.add_task(run_pipeline)
    return {"execution_id": execution.id, "status": "running"}  # Returns in < 15ms
  </pre>

  <!-- FILE 4 & 5 -->
  <div class="file-card tier1">
    <div class="file-header">
      <span class="file-title">4. src/agents/search_agent.py & 5. src/agents/answer_verifier.py</span>
      <span class="badge-tier1">Tier 1: Core</span>
    </div>
    <div class="file-purpose"><strong>Purpose:</strong> Dual verification: Multi-API discovery failover and zero-temperature hallucination guardrail.</div>
    <div class="file-viva">
      <strong>Viva / Walkthrough Explanation:</strong> "In <code>SearchAgent</code>, if the arXiv API times out or rate-limits, it catches the error and cascades to Semantic Scholar. In <code>AnswerVerifier</code>, the agent audits synthesized claims against source paper abstracts at <code>temperature=0.0</code>, flagging unbacked assertions and producing a 0.0–1.0 confidence score."
    </div>
  </div>
  <pre>
# src/agents/search_agent.py - Failover Discovery Cascade
try:
    papers.extend(self._search_arxiv(query))
except Exception:
    pass  # Failover immediately to Semantic Scholar
if len(papers) < self.max_papers:
    papers.extend(self._search_semantic_scholar(query, self.max_papers - len(papers)))

# src/agents/answer_verifier.py - Zero-Temperature Hallucination Guardrail
resp = client.chat.completions.create(
    model=self.model,
    messages=[{"role": "system", "content": "Audit this synthesis against source abstracts. Flag unsupported claims."}, ...],
    temperature=0.0  # Deterministic auditing
)
  </pre>

  <!-- FILE 6 -->
  <div class="file-card tier1">
    <div class="file-header">
      <span class="file-title">6. src/rag/retriever.py</span>
      <span class="badge-tier1">Tier 1: Core</span>
    </div>
    <div class="file-purpose"><strong>Purpose:</strong> Workspace-scoped vector store isolation and persistent ChromaDB index management.</div>
    <div class="file-viva">
      <strong>Viva / Walkthrough Explanation:</strong> "To prevent cross-tenant data leakage between researchers, ChromaDB collections are strictly partitioned per workspace (<code>ws_{workspace_id}</code>) using HNSW indexing with cosine similarity distance (<code>hnsw:space: cosine</code>)."
    </div>
  </div>
  <pre>
# src/rag/retriever.py - Workspace Isolation via Dynamic Collection Naming
def _get_collection(self, workspace_id: str):
    collection_name = f"ws_{workspace_id}"
    return self.client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
  </pre>

  <div class="doc-footer">
    <div>ReAssist Codebase Walkthrough Guide &bull; Chapter 2: Tier 1 Core Engines (Part 2)</div>
    <div>Production v3.2.0</div>
  </div>
</div>

<!-- ═════════════════════════════════════════════════════════════════ -->
<!-- CHAPTER 2 (CONTINUED): FILE 7 - MODEL PROVIDER ABSTRACTION       -->
<!-- ═════════════════════════════════════════════════════════════════ -->
<div class="page-break"></div>
<div class="page">
  <!-- FILE 7 -->
  <div class="file-card tier1">
    <div class="file-header">
      <span class="file-title">7. src/core/llm_provider.py (Central Model Factory & Provider Switch)</span>
      <span class="badge-tier1">Tier 1: Core</span>
    </div>
    <div class="file-purpose"><strong>Purpose:</strong> Unified model factory and dynamic runtime switch between local Ollama and cloud OpenAI/Bedrock.</div>
    <div class="file-viva">
      <strong>Viva / Walkthrough Explanation:</strong> "When the examiner asks: <em>'Where is model calling done and where does the switch between local Ollama and other models take place?'</em> — I open lines 178–209 of <code>llm_provider.py</code>! Every agent in <code>src/agents/</code> calls <code>self.client.chat.completions.create(...)</code> adhering to the universal OpenAI specification. Here in <code>get_llm_client()</code>, if <code>LLM_PROVIDER=ollama</code>, we pass <code>base_url='http://localhost:11434/v1'</code> into the official OpenAI SDK. Since Ollama natively serves an OpenAI-compatible <code>/v1</code> endpoint, the exact same client communicates with local Llama 3.1 or Phi-3 without any wrapper bloat. If set to <code>openai</code>, it uses cloud OpenAI; if set to <code>bedrock</code>, our <code>BedrockClientWrapper</code> adapts AWS <code>boto3</code> Converse API. Client instances are cached using <code>@lru_cache(maxsize=4)</code> for zero re-instantiation overhead."
    </div>
  </div>
  <pre>
# src/core/llm_provider.py (Lines 178-209) - Dynamic Provider Switch Factory
@lru_cache(maxsize=4)
def get_llm_client(provider: str | None = None):
    provider = provider or get_provider()  # Driven by LLM_PROVIDER in .env
    config = PROVIDER_DEFAULTS.get(provider, PROVIDER_DEFAULTS["openai"])

    if provider == "openai":
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    elif provider == "ollama":
        # SWITCH TO LOCAL OLLAMA: Official OpenAI SDK points to Ollama /v1 endpoint
        base_url = os.getenv("OLLAMA_BASE_URL", config["base_url"])  # http://localhost:11434/v1
        return OpenAI(base_url=base_url, api_key="ollama")

    elif provider == "bedrock":
        # SWITCH TO AWS BEDROCK: Adapter pattern wrapping boto3 converse() API
        region = os.getenv("AWS_REGION", config.get("region", "us-east-1"))
        return BedrockClientWrapper(region_name=region)

# How ANY Agent Calls the Model (e.g., src/agents/summarize_agent.py Line 100):
# response = self.client.chat.completions.create(model=self.model, messages=[...], temperature=0.3)
  </pre>

  <div class="doc-footer">
    <div>ReAssist Codebase Walkthrough Guide &bull; Chapter 2: Tier 1 Core Engines (Part 3)</div>
    <div>Production v3.2.0</div>
  </div>
</div>

<!-- ═════════════════════════════════════════════════════════════════ -->
<!-- CHAPTER 3: TIER 2 SUPPORTING SERVICES                            -->
<!-- ═════════════════════════════════════════════════════════════════ -->
<div class="page-break"></div>
<div class="page">
  <h1>3. Tier 2: Supporting Services & Orchestration Layer</h1>
  <p>
    These 4 modules provide enterprise-grade glue: managing database state, processing documents, and handling authentication.
    Explain these if the examiner asks about database architecture, storage, or security.
  </p>

  <div class="file-card tier2">
    <div class="file-header">
      <span class="file-title">src/services/research_service.py</span>
      <span class="badge-tier2">Tier 2: Service</span>
    </div>
    <div class="file-purpose"><strong>Purpose:</strong> Business logic coordinator connecting FastAPI routes with LangGraph execution, conversational memory, and ORM persistence.</div>
    <div class="file-viva">
      <strong>Viva Walkthrough:</strong> "This service implements the Service-Layer Pattern. It retrieves recent conversation memory from <code>workspace_memory.py</code>, calls <code>RootAgent.execute_pipeline</code>, saves the full JSON dossier into local/S3 storage via <code>StorageService</code>, and commits per-agent latency and token counts to the <code>AgentTrace</code> database table."
    </div>
  </div>

  <div class="file-card tier2">
    <div class="file-header">
      <span class="file-title">src/rag/document_processor.py & src/rag/embeddings.py</span>
      <span class="badge-tier2">Tier 2: Service</span>
    </div>
    <div class="file-purpose"><strong>Purpose:</strong> Ingestion pipeline parsing uploaded PDFs and generating 768-dimensional dense vectors.</div>
    <div class="file-viva">
      <strong>Viva Walkthrough:</strong> "We use LangChain's <code>RecursiveCharacterTextSplitter</code> with <code>chunk_size=1000</code> and <code>chunk_overlap=150</code>. In <code>embeddings.py</code>, we resolve embeddings via Ollama's <code>nomic-embed-text</code> locally (768 dimensions) or AWS Bedrock Titan v2, with automated URL normalization stripping <code>/v1</code> for native Ollama compatibility."
    </div>
  </div>

  <div class="file-card tier2">
    <div class="file-header">
      <span class="file-title">src/core/database.py & src/models/orm.py</span>
      <span class="badge-tier2">Tier 2: Service</span>
    </div>
    <div class="file-purpose"><strong>Purpose:</strong> Relational persistence layer using SQLAlchemy 2.0 ORM with SQLite Write-Ahead Logging (WAL).</div>
    <div class="file-viva">
      <strong>Viva Walkthrough:</strong> "We use SQLAlchemy 2.0. In development, SQLite runs in WAL mode (<code>PRAGMA journal_mode=WAL</code>) to enable concurrent reads while background workers write. In production, changing <code>DATABASE_URL</code> in <code>.env</code> seamlessly migrates the schema to PostgreSQL. Tables include <code>users</code>, <code>workspaces</code>, <code>pipeline_executions</code>, <code>agent_traces</code>, and <code>chat_messages</code>."
    </div>
  </div>

  <div class="file-card tier2">
    <div class="file-header">
      <span class="file-title">src/core/auth.py</span>
      <span class="badge-tier2">Tier 2: Service</span>
    </div>
    <div class="file-purpose"><strong>Purpose:</strong> JWT Bearer token authentication with automated demo-mode fallback.</div>
    <div class="file-viva">
      <strong>Viva Walkthrough:</strong> "We use standard OAuth2 password bearer tokens with HMAC-SHA256 signing. However, for seamless viva demos, if an examiner opens the UI without logging in, <code>get_current_user</code> automatically creates or resolves a default <code>demo@reassist.ai</code> user, preserving foreign-key database constraints without presentation friction."
    </div>
  </div>

  <div class="doc-footer">
    <div>ReAssist Codebase Walkthrough Guide &bull; Chapter 3: Tier 2 Supporting Services</div>
    <div>Production v3.2.0</div>
  </div>
</div>

<!-- ═════════════════════════════════════════════════════════════════ -->
<!-- CHAPTER 4: TIER 3 ANCILLARY & BOILERPLATE FILES                  -->
<!-- ═════════════════════════════════════════════════════════════════ -->
<div class="page-break"></div>
<div class="page">
  <h1>4. Tier 3: Ancillary Utilities & Boilerplate (Low Priority)</h1>
  <p>
    These files are necessary for production support, data formatting, and backwards compatibility. 
    You do <strong>not</strong> need to proactively show these in an interview. Use the quick explanations below if an examiner clicks on them:
  </p>

  <div class="file-card tier3">
    <div class="file-header">
      <span class="file-title">src/utils/logger.py & logs/runs/</span>
      <span class="badge-tier3">Tier 3: Utility</span>
    </div>
    <div class="file-purpose"><strong>Why it exists:</strong> Structured file and console logging. Appends JSON execution traces to <code>logs/runs/run_*.json</code> for observability telemetry.</div>
  </div>

  <div class="file-card tier3">
    <div class="file-header">
      <span class="file-title">src/utils/pdf_parser.py</span>
      <span class="badge-tier3">Tier 3: Utility</span>
    </div>
    <div class="file-purpose"><strong>Why it exists:</strong> Fallback extraction script that reads text from local PDF files using <code>pdfplumber</code> or <code>PyPDF2</code> if LangChain loaders fail.</div>
  </div>

  <div class="file-card tier3">
    <div class="file-header">
      <span class="file-title">src/services/export_service.py</span>
      <span class="badge-tier3">Tier 3: Utility</span>
    </div>
    <div class="file-purpose"><strong>Why it exists:</strong> Dossier export formatter. Converts final pipeline JSON state into formatted Markdown dossiers or BibTeX citations for LaTeX/Overleaf.</div>
  </div>

  <div class="file-card tier3">
    <div class="file-header">
      <span class="file-title">src/api/serializers.py & src/api/schemas.py</span>
      <span class="badge-tier3">Tier 3: Utility</span>
    </div>
    <div class="file-purpose"><strong>Why it exists:</strong> Standard Pydantic input models (e.g. <code>QueryRequest</code>) and dictionary serializers converting SQLAlchemy ORM rows to clean JSON responses.</div>
  </div>

  <div class="file-card tier3">
    <div class="file-header">
      <span class="file-title">src/api/routes/legacy.py</span>
      <span class="badge-tier3">Tier 3: Utility</span>
    </div>
    <div class="file-purpose"><strong>Why it exists:</strong> Deprecated prototype endpoints from v1.0 (such as <code>/analyze</code>) kept alive so legacy test scripts and prototype frontends don't break.</div>
  </div>

  <div class="file-card tier3">
    <div class="file-header">
      <span class="file-title">src/agents/fair_baseline_agent.py & cot_baseline_agent.py</span>
      <span class="badge-tier3">Tier 3: Utility</span>
    </div>
    <div class="file-purpose"><strong>Why it exists:</strong> Scientific control baselines. <code>CoTBaselineAgent</code> runs single-shot prompting; <code>FairBaselineAgent</code> feeds identical papers to a single prompt for fair benchmark evaluation.</div>
  </div>

  <div class="file-card tier3">
    <div class="file-header">
      <span class="file-title">evaluation/stability_tester.py & evaluator.py</span>
      <span class="badge-tier3">Tier 3: Utility</span>
    </div>
    <div class="file-purpose"><strong>Why it exists:</strong> Evaluation harness that automates rubric scoring (Coverage, Specificity, Actionability) and runs repeat query stability benchmarks.</div>
  </div>

  <!-- 3-MINUTE PRESENTATION SCRIPT -->
  <h2 style="margin-top: 16px;">5. The Exact 3-Minute "Show Me The Code" Presentation Script</h2>
  <div style="background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px; padding: 10px; font-size: 8.5pt;">
    <p><strong>Step 1 (Open <code>src/pipeline/graph_builder.py</code>):</strong><br>
    <em>"Here is our central nervous system. Rather than using brittle Python loops or linear chains, we built an 11-agent LangGraph state machine. Notice lines 71–90 where every node has exponential backoff retry. On line 365, notice the Corrective RAG router: if verified papers &lt; 3, it loops back to rewrite and search again, with Tavily web search as fallback."</em></p>
    
    <p><strong>Step 2 (Open <code>src/router/agent_router.py</code>):</strong><br>
    <em>"Next is our economic gatekeeper. Calling an LLM to decide whether to call an LLM wastes money. On line 85, our router scores 6 heuristic signals in under 2ms with zero token cost. Simple queries route to fast CoT, saving ~75% in inference costs."</em></p>

    <p><strong>Step 3 (Open <code>src/api/routes/pipeline.py</code>):</strong><br>
    <em>"Here is our API decoupling. Because multi-agent discovery takes ~30 seconds, line 75 dispatches execution to FastAPI BackgroundTasks. The endpoint returns in &lt;15ms with an execution ID, and the frontend polls asynchronously, preventing socket timeouts."</em></p>

    <p style="margin-bottom: 0;"><strong>Step 4 (Open <code>src/core/llm_provider.py</code>):</strong><br>
    <em>"And if you look at lines 178–209 of <code>llm_provider.py</code>, here is where all model calling and provider switching happens. Every agent calls standard <code>chat.completions.create</code>. By leveraging Ollama's native <code>/v1</code> endpoint, our factory connects the official OpenAI SDK directly to local Llama 3.1 and Phi-3 Mini for air-gapped zero-cost runs, and switches to cloud OpenAI or AWS Bedrock simply by changing <code>LLM_PROVIDER</code> in <code>.env</code> without altering any agent code."</em></p>
  </div>

  <!-- EXAMINER TRAP QUESTIONS & RAPID REBUTTALS -->
  <h2 style="margin-top: 14px;">6. Examiner Trap Questions & Rapid In-Code Rebuttals</h2>
  <div style="background: #ffffff; border: 1px solid #d0d7de; border-radius: 6px; padding: 8px 10px; font-size: 8pt;">
    <p style="margin-bottom: 5px;"><strong>Trap 1: "Where in the code is the LLM actually called?"</strong><br>
    &bull; <em>Answer:</em> "Inside each agent's execution method (e.g. <code>src/agents/summarize_agent.py:L100</code>, <code>answer_verifier.py:L65</code>) via <code>self.client.chat.completions.create(model=self.model, messages=[...])</code>."</p>
    
    <p style="margin-bottom: 5px;"><strong>Trap 2: "Where does the switch between local Ollama and cloud OpenAI happen?"</strong><br>
    &bull; <em>Answer:</em> "In <code>src/core/llm_provider.py:L178</code> inside <code>get_llm_client()</code>. If <code>LLM_PROVIDER=ollama</code>, it instantiates <code>OpenAI(base_url='http://localhost:11434/v1')</code>; if <code>openai</code>, it passes the cloud API key."</p>

    <p style="margin-bottom: 0;"><strong>Trap 3: "Why benchmark on OpenAI costs if you ran locally on Ollama?"</strong><br>
    &bull; <em>Answer:</em> "The architectural experiment measures multi-agent decomposition against a single prompt on the <em>identical model</em>. Ollama ensures 100% frozen reproducibility and zero API fees, while the OpenAI pricing matrix simulates enterprise deployment savings."</p>
  </div>

  <div class="doc-footer">
    <div>ReAssist Codebase Walkthrough Guide &bull; Chapter 4 & 5: Script & Trap Questions</div>
    <div>Production v3.2.0</div>
  </div>
</div>

</body>
</html>
"""

def generate_code_walkthrough_pdf():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    
    html_path = os.path.join(project_root, "docs", "ReAssist_Codebase_Walkthrough_Guide.html")
    pdf_path = os.path.join(project_root, "ReAssist_Codebase_Walkthrough_Guide.pdf")
    pdf_docs_path = os.path.join(project_root, "docs", "ReAssist_Codebase_Walkthrough_Guide.pdf")
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads", "ReAssist_Codebase_Walkthrough_Guide.pdf")
    
    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    
    print("Writing formatted HTML walkthrough report...")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE)
    print(f"HTML written to: {html_path}")
    
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    edge_exe = next((p for p in edge_paths if os.path.exists(p)), None)
    
    if not edge_exe:
        print("ERROR: Microsoft Edge executable not found.")
        return False
        
    print(f"Compiling Codebase Walkthrough PDF via Edge headless: {edge_exe}...")
    cmd = [
        edge_exe,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
        size = os.path.getsize(pdf_path)
        print(f"Successfully generated root PDF: {pdf_path} ({size} bytes)")
        
        # Copy to docs directory
        shutil.copy2(pdf_path, pdf_docs_path)
        print(f"Copied to docs folder: {pdf_docs_path}")
        
        # Copy to user's Downloads directory
        shutil.copy2(pdf_path, downloads_path)
        print(f"Copied to Downloads folder: {downloads_path}")
        return True
    else:
        print(f"PDF compilation failed: {res.stderr}")
        return False

if __name__ == "__main__":
    generate_code_walkthrough_pdf()
