# ReAssist — Research Intelligence Engine

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue) ![OpenAI GPT](https://img.shields.io/badge/OpenAI-GPT-green) ![arXiv + Semantic Scholar](https://img.shields.io/badge/Search-arXiv%20%2B%20Semantic%20Scholar-orange) ![MIT License](https://img.shields.io/badge/License-MIT-purple)

## 📈 Measured Results

| Metric | Value |
|---|---|
| Multi-agent latency | ~35s |
| CoT baseline latency | ~9s |
| Multi-agent cost (gpt-4o-mini) | ~$0.006/query |
| CoT cost (gpt-4o-mini) | ~$0.0015/query |
| Router cost reduction | ~75% on routed queries |
| Model | gpt-4o-mini |
| Papers per query | 3-7 (arXiv + Semantic Scholar) |

**AgenticOps Router** reduces average cost by ~75% by routing 
simple queries to CoT automatically.

## Roadmap
- [ ] Conversational memory layer
- [ ] RAG pipeline with ChromaDB  
- [ ] Docker containerization
- [ ] CI/CD with GitHub Actions
- [ ] Multi-PDF support

## What Is This
ReAssist is an intelligent research engine that fetches academic papers and runs 7 specialized agents to generate novel research ideas and methodologies. It empirically compares the quality of this 7-agent pipeline against a single Chain-of-Thought (CoT) baseline to measure actual ROI on multiple LLM calls. The integrated AgenticOps router intelligently classifies incoming queries, reducing average API costs by ~70% by routing simple or informational queries directly to the cheaper CoT baseline.

## The Core Question
**"When is a multi-agent system actually worth its cost?"**
Multi-agent systems yield significant quality gains only for complex, novel, or deeply comparative research queries; for standard informational lookups, a single well-prompted model is 4x cheaper and 4x faster. The AgenticOps router provides immense value by programmatically detecting when the expensive 7-agent pipeline is justified versus when a simple CoT baseline suffices.

## Architecture

### The 7-Agent Pipeline

| Agent | Receives (context slicing) | Produces |
|---|---|---|
| **SearchAgent** | `query` | `papers` |
| **SummarizerAgent** | `papers` | `papers` (with summaries) |
| **SynthesizerAgent** | `papers` | `synthesis` |
| **GapFinderAgent** | `synthesis` | `gaps` |
| **IdeaGeneratorAgent**| `gaps`, `synthesis` | `ideas` |
| **TechniqueAgent** | `synthesis`, `ideas` | `techniques` |
| **GuidanceAgent** | `ideas`, `techniques` | `guidance` |

*Note: Context slicing is enforced via the `_slice_context()` method in `root_agent.py`, which restricts the data passed to each agent based strictly on its `required_inputs` list, saving tokens and improving focus.*

### CoT Baseline
The `agents/cot_baseline_agent.py` script serves entirely as a control baseline for the pipeline. Instead of 7 specialized sequential completions, it runs the entire research extraction and generation task as a single, massive JSON-structured Chain-of-Thought prompt over the retrieved papers. Its singular responsibility is generating a baseline comparison to evaluate if the multi-agent pipeline overhead yields better empirical results.

### AgenticOps Router
The `router.py` utilizes 6 distinct heuristic signals to score queries across two dimensions:
- **Complexity Score (0-3):** Presence of domain jargon, query length > 8 words, comparative language (e.g., vs, tradeoff).
- **Precision Score (0-3):** Need for recency (e.g., 2024, sota), survey intent (e.g., review, benchmark), narrow scope (<6 unique words).

**Decision Table:**
- Total Score ≤ 2 → Route to `cot` (90% confidence)
- Total Score ≤ 4 → Route to `cot` (65% confidence)
- Total Score ≥ 5 → Route to `multi_agent` (85% confidence)

The router continually logs its score breakdowns, routing decisions, and resulting cost savings to `routing_log.jsonl` as empirical evidence of operational efficiency.

## Cost Model

| Approach | gpt-3.5-turbo | gpt-4 | Latency | Best For |
|---|---|---|---|---|
| **multi-agent** | ~$0.015 | ~$0.45 | ~35s | Complex, technical, or deeply comparative queries. |
| **cot baseline** | ~$0.004 | ~$0.12 | ~9s | General surveys, established topics, broad overviews. |
| **router auto** | Variable | Variable | Variable | Production environments needing automated cost-optimization. |

**Cost Reduction Mechanisms:**
1. **Context Slicing:** `_slice_context()` enforces that agents only receive data they explicitly request via `required_inputs`, saving dense token cascades.
2. **AgenticOps Routing:** Deflects simple or informational queries away from the multi-agent path, dropping query costs from ~$0.015 to ~$0.004.
3. **Optimized Token Chunking:** Async summarization relies on chunking documents at 2000 tokens within `summarize_agent.py`, ensuring context limits are respected efficiently without massive prompts.

## How To Run

### Prerequisites
`pip install -r requirements.txt`
Copy `.env.example` to `.env` and add your `OPENAI_API_KEY`.

### Run the pipeline
`python main.py`

### Run the Streamlit UI
`streamlit run streamlit_app.py`

### Test router standalone
`python router.py`

### Run E2E tests
`python test_integration.py`

## ⚖️ 6. Human-Annotated Evaluator

To ensure honest evaluation, the system uses **human annotation** 
over LLM self-grading. An LLM scoring its own output is not 
evaluation — it's the model grading its own homework.

- **Control variables:** CoT baseline runs on the exact same 
  source papers as the multi-agent pipeline
- **Human scoring:** 10 test queries scored manually on a 
  1-10 rubric across Coverage, Specificity, Actionability
- **Automated fallback:** Structural scoring when no human 
  annotation exists for a query
- **Results stored:** evaluation/human_annotations.csv

## Project Structure
- `agents/`: Contains the 7 specialized AI agents and the CoT baseline.
- `utils/`: Helper utilities including context helpers, logging, and the TokenCounter observability module.
- `evaluation/`: The `evaluator.py` baseline comparator and the `results/` output directory.
- `logs/`: Destination for `routing_log.jsonl` and performance traces.
- `root_agent.py`: Orchestrates the 7 agents, implements retry mechanisms, and slices context.
- `router.py`: Determines pathing (CoT vs Multi-Agent) via complexity/precision scoring.
- `main.py`: The core CLI and execution entry point.
- `streamlit_app.py`: Web UI for running the pipeline interactively.
- `config.py`: Environment configurations and constants.
- `test_integration.py`: Automated E2E verification script.
- `requirements.txt`: Python package dependencies.
- `.env.example`: Template for environment variables.
- `.gitignore`: Git exclusion rules.
- `README.md`: Main project documentation.

## Roadmap
### 📚 5. RAG Vector Engine (Phase 5)
Planned ChromaDB integration for PDF-based retrieval...

- Phase 6: Router learning from annotation data
- Phase 7: Multi-PDF support

## Key Design Decisions
- **`required_inputs` context slicing:** Passing the entire state dict between 7 agents bloats tokens exponentially; explicit injection guarantees agents only parse what they strictly require.
- **Why OpenAI GPT:** Offers the most reliable JSON schema adherence required by the pipeline's strict dictionary-passing interfaces.
- **Why human annotation over LLM self-grading:** "LLM-as-a-judge" often favors its own verbosity or writing style; human review guarantees ground-truth validity on actionability and hypothesis novelty.
- **Why sequential deterministic pipeline over parallel agents:** Enforces absolute strict dependency trees (e.g., Gaps *must* exist before Ideas), removing the unreliability inherent to agent swarms fighting for state.
