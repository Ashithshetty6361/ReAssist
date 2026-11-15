# 🎯 ReAssist — Master Resume Code Showcase & Interview Navigator

> **Placement:** `00_RESUME_CODE_SHOWCASE/` (Always sorted at the very top of your IDE file explorer)  
> **Purpose:** Instant screen-share lookup during technical interviews, project defenses, and live code walkthroughs.  
> **How to search in VS Code:** Press `Ctrl + P`, type the filename, and press `Enter`.

---

## 🗂️ Separate Backend & Frontend Master Guides

To present the system clearly, the codebase is partitioned into two dedicated guides:

| Component | Master Walkthrough Guide | Standalone Startup Script | Primary Tech Stack |
|---|---|---|---|
| **Backend (Server & Agents)** | [**`01_BACKEND_CODE_SHOWCASE.md`**](file:///c:/Users/shett/MIT_BTech/ReAssist_Project/00_RESUME_CODE_SHOWCASE/01_BACKEND_CODE_SHOWCASE.md) | Double-click [`start_backend.bat`](file:///c:/Users/shett/MIT_BTech/ReAssist_Project/start_backend.bat) (Port 8000/8001) | FastAPI, LangGraph, Ollama, Bedrock, SQLAlchemy |
| **Frontend (Dashboard & UI)** | [**`02_FRONTEND_CODE_SHOWCASE.md`**](file:///c:/Users/shett/MIT_BTech/ReAssist_Project/00_RESUME_CODE_SHOWCASE/02_FRONTEND_CODE_SHOWCASE.md) | Double-click [`start_frontend.bat`](file:///c:/Users/shett/MIT_BTech/ReAssist_Project/start_frontend.bat) (Port 3000) | Next.js 16, React 19, TypeScript, Turbopack |

---

## ⚡ Quick Search Cheat Sheet (Press `Ctrl + P` in VS Code)

| Resume Bullet Point | File to Open (`Ctrl + P`) | Core Function / Concept to Highlight |
|---|---|---|
| **Bullet 1: 7-Agent Pipeline & Interface** | `01_agent_interface_contract.py` | `required_inputs = ['synthesis']`, `run(dict) -> dict` |
| **Bullet 1: Dynamic Context Slicing** | `02_context_slicing_engine.py` | `slice_context(state, required_inputs)` |
| **Bullet 1: State Machine & Graph** | `03_deterministic_state_graph.py` | `PipelineState(TypedDict)`, LangGraph node slicing |
| **Bullet 2: CoT Baseline & 28% Token Reduction**| `01_cot_baseline_vs_multiagent.py`| Monolithic CoT prompt vs. sliced cascade token math |
| **Bullet 2: Evaluation Scoring Harness** | `02_token_reduction_evaluator.py` | `run_baseline_comparison()`, Coverage/Specificity |
| **Bullet 2: 99.2% Schema Compliance Test** | `03_stability_test_99_2_compliance.py`| Multi-run stability suite, 99.2% compliance rate |
| **Bullet 2: Typed Pydantic Contracts** | `04_pydantic_schema_contracts.py` | `VerificationResult(BaseModel)`, bounds validation |
| **Bullet 2: Self-Healing JSON Parser** | `05_self_healing_json_parser.py` | 4-stage cleanup (`clean_llm_json`) |
| **Bullet 3: Per-Agent Token/Latency Metrics** | `01_per_agent_token_latency_counter.py`| `TokenCounter.track()`, dollar cost calculation |
| **Bullet 3: Structured JSON Logging** | `02_structured_json_logger.py` | `ResearchLogger`, machine-readable telemetry schema |
| **Bullet 3: Real Execution Trace Artifact** | `03_real_execution_trace_sample.json` | Live run: per-agent timings, `slowest_agent`, 0.95 conf |
| **Bullet 3: CRAG Corrective Loop Trace** | `04_crag_corrective_trace_sample.json` | Query rewrites (r0, r1) and Tavily web fallback |
| **Bullet 3: AgenticOps Heuristic Router** | `05_agenticops_router_telemetry.py` | < 2ms lexical scoring (0-6), 70% cost savings |

---

## 📌 Bullet-by-Bullet Deep Dive: What to Show & Say

### 🔹 Bullet 1: 7-Agent Synthesis Pipeline & Dynamic Context Slicing
> *"Designed a deterministic 7-agent research synthesis pipeline with strict typed run(dict) → dict interfaces and dynamic context slicing."*

#### 1. Files to Open:
1. `00_RESUME_CODE_SHOWCASE/BULLET1_7_AGENTS_AND_CONTEXT_SLICING/01_agent_interface_contract.py`
   *(Original: `src/agents/gap_finder_agent.py` and `src/agents/idea_generator_agent.py`)*
2. `00_RESUME_CODE_SHOWCASE/BULLET1_7_AGENTS_AND_CONTEXT_SLICING/02_context_slicing_engine.py`
   *(Original: `src/utils/context_slicer.py`)*
3. `00_RESUME_CODE_SHOWCASE/BULLET1_7_AGENTS_AND_CONTEXT_SLICING/03_deterministic_state_graph.py`
   *(Original: `src/pipeline/graph_builder.py` and `src/models/state.py`)*

#### 2. What to Highlight on Screen:
- Highlight `required_inputs = ['synthesis']` in `GapFinderAgent`.
- Highlight `slice_context(state, required_inputs)` in `02_context_slicing_engine.py`.
- Highlight `PipelineState(TypedDict)` in `03_deterministic_state_graph.py`.

#### 3. What to Say (30-Second Interview Pitch):
> *"In literature review, asking a single prompt to read 5–7 papers and simultaneously synthesize, find gaps, and invent hypotheses causes severe attention degradation—the well-known 'Lost in the Middle' phenomenon.  
> To solve this, I decoupled the workflow into 7 specialized single-responsibility agents. Every agent conforms to a strict contract: `run(dict) -> dict` and explicitly declares its `required_inputs`.  
> At each node boundary, my `slice_context` engine filters the global state, passing ONLY the declared keys. For example, the Gap Finder receives only the synthesis—not the 15,000 tokens of raw papers. This prevents $O(N^2)$ token explosion, cutting cascade tokens by 52%."*

---

### 🔹 Bullet 2: 28% Token Reduction & 99.2% Schema Compliance
> *"Achieved a 28% token reduction against standard Chain-of-Thought (CoT) baselines and 99.2% schema compliance across multi-run stability tests."*

#### 1. Files to Open:
1. `00_RESUME_CODE_SHOWCASE/BULLET2_TOKEN_REDUCTION_AND_99_2_SCHEMA/01_cot_baseline_vs_multiagent.py`
   *(Original: `src/agents/cot_baseline_agent.py`)*
2. `00_RESUME_CODE_SHOWCASE/BULLET2_TOKEN_REDUCTION_AND_99_2_SCHEMA/03_stability_test_99_2_compliance.py`
   *(Original: `evaluation/stability_tester.py`)*
3. `00_RESUME_CODE_SHOWCASE/BULLET2_TOKEN_REDUCTION_AND_99_2_SCHEMA/04_pydantic_schema_contracts.py`
   *(Original: `src/models/agent_outputs.py`)*
4. `00_RESUME_CODE_SHOWCASE/BULLET2_TOKEN_REDUCTION_AND_99_2_SCHEMA/05_self_healing_json_parser.py`
   *(Original: `src/utils/json_parser.py`)*

#### 2. What to Highlight on Screen:
- Highlight `COT_PROMPT_TEMPLATE` in `01_cot_baseline_vs_multiagent.py`: Show how monolithic CoT holds all raw paper tokens in context across all generation stages.
- Highlight the math: $(17,450 - 12,560) / 17,450 = 28.02\%$ token reduction!
- Highlight `MultiRunStabilityTester` in `03_stability_test_99_2_compliance.py`: Shows how 99.2% schema compliance was verified across repeated execution runs.
- Highlight `clean_llm_json()` in `05_self_healing_json_parser.py`: Show the 4-stage cleanup (stripping markdown code blocks, regex brace extraction, quote fixing).

#### 3. What to Say (30-Second Interview Pitch):
> *"To rigorously prove that a multi-agent system is worth the complexity, I built an automated evaluation harness comparing our pipeline against a monolithic Chain-of-Thought (CoT) baseline.  
> Monolithic CoT must hold all 15,000 raw paper tokens in context while generating reasoning across all 6 sections. In ReAssist, our Summarizer condenses papers into structured 1,200-token summaries, and downstream agents run on sliced contexts. This resulted in a **28% net token reduction** compared to CoT on identical research queries.  
> Furthermore, across multi-run stability testing with $>500$ agent steps, our pipeline achieved **99.2% schema compliance** against our Pydantic models, made possible by low-temperature deterministic prompting and a 4-tier self-healing JSON parser."*

---

### 🔹 Bullet 3: Observability Metrics & Structured JSON Logging
> *"Built per-agent latency/token observability metrics and structured JSON logging for real-time trace analysis."*

#### 1. Files to Open:
1. `00_RESUME_CODE_SHOWCASE/BULLET3_OBSERVABILITY_AND_JSON_LOGS/01_per_agent_token_latency_counter.py`
   *(Original: `src/utils/token_counter.py`)*
2. `00_RESUME_CODE_SHOWCASE/BULLET3_OBSERVABILITY_AND_JSON_LOGS/02_structured_json_logger.py`
   *(Original: `src/utils/logger.py`)*
3. `00_RESUME_CODE_SHOWCASE/BULLET3_OBSERVABILITY_AND_JSON_LOGS/03_real_execution_trace_sample.json`
   *(Original: `logs/runs/run_4a9431a1.json`)*
4. `00_RESUME_CODE_SHOWCASE/BULLET3_OBSERVABILITY_AND_JSON_LOGS/05_agenticops_router_telemetry.py`
   *(Original: `src/router/agent_router.py`)*

#### 2. What to Highlight on Screen:
- Highlight `TokenCounter.track()` and `cost_usd` formula in `01_per_agent_token_latency_counter.py`.
- Open `03_real_execution_trace_sample.json`: Show the real per-agent latency waterfall (`search: 20.51s`, `summarizer: 195.99s`, `technique: 603.22s`, `slowest_agent: technique`), and the `verification` block (`confidence: 0.95`, `unsupported_claims: []`).
- Open `05_agenticops_router_telemetry.py`: Show the 6 lexical heuristic signals that execute in **$< 2$ ms** with zero token consumption, routing simple queries to CoT and saving 68%–75% of cloud costs.

#### 3. What to Say (30-Second Interview Pitch):
> *"Debugging distributed LLM agents without observability is impossible. I implemented full three-pillar observability:  
> 1. **Metrics:** `TokenCounter` tracks prompt tokens, completion tokens, latency, and cost per agent, automatically identifying the slowest and most expensive nodes.  
> 2. **Structured Logs:** `ResearchLogger` emits machine-readable JSON logs for every execution trace, ready for ingestion into Datadog or CloudWatch.  
> 3. **Traces:** Here in `run_4a9431a1.json`, you can see an actual recorded run trace: it captures per-node latencies, identifying `TechniqueAgent` as the bottleneck, and records our `AnswerVerifier` auditing synthesis faithfulness with 0.95 confidence."*

---

## 🔗 Quick Reference to Original Codebase Locations

```
ReAssist_Project/
├── 00_RESUME_CODE_SHOWCASE/                   <-- Top of File Explorer!
│   ├── 00_MASTER_SHOWCASE_NAVIGATOR.md        <-- You are here!
│   ├── BULLET1_7_AGENTS_AND_CONTEXT_SLICING/
│   ├── BULLET2_TOKEN_REDUCTION_AND_99_2_SCHEMA/
│   └── BULLET3_OBSERVABILITY_AND_JSON_LOGS/
├── src/
│   ├── agents/                                <-- Individual Agent Implementations
│   ├── pipeline/graph_builder.py              <-- LangGraph 11-Agent State Machine
│   ├── pipeline/orchestrator.py               <-- Root Orchestrator
│   ├── models/state.py                        <-- PipelineState TypedDict
│   ├── models/agent_outputs.py                <-- Pydantic Schema Contracts
│   ├── router/agent_router.py                 <-- <2ms Heuristic Router
│   └── utils/
│       ├── context_slicer.py                  <-- slice_context() Engine
│       ├── token_counter.py                   <-- Token & Cost Observability
│       ├── logger.py                          <-- Structured JSON Logger
│       └── json_parser.py                     <-- 4-Stage Self-Healing Parser
├── evaluation/
│   ├── evaluator.py                           <-- CoT vs Multi-Agent Evaluator
│   └── stability_tester.py                    <-- 99.2% Compliance Stability Suite
└── logs/runs/                                 <-- Real-World Run Trace Artifacts
```

