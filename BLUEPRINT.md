# ReAssist — System Blueprint

**Research Intelligence Engine with Fair Multi-Agent Evaluation**

---

## 🎯 System Overview

ReAssist is a research assistance system that analyzes academic papers and generates novel research ideas through either:
1. **Multi-agent pipeline** - 7 specialized agents working sequentially
2. **Fair baseline** - Structured single-prompt Chain-of-Thought

The system provides **honest 3-way evaluation** comparing both approaches.

---

## 🏗️ Architecture

### Design Principles

1. **Single Responsibility** - Each agent has ONE job
2. **Strict Interface** - All agents use `run(dict) -> dict`
3. **Context Slicing** - Agents receive ONLY required inputs
4. **No Agent-to-Agent Calls** - Root orchestrates everything
5. **Deterministic Orchestration** - Predictable execution flow

### High-Level Flow

```
User Query
    ↓
Root Agent (Orchestrator)
    ↓
├─ Search Agent ────────→ Papers
├─ Summarizer Agent ────→ Summaries
├─ Synthesizer Agent ───→ Cross-paper themes
├─ Gap Finder Agent ────→ Research gaps
├─ Idea Generator Agent ─→ Novel ideas
├─ Technique Agent ─────→ Alternative methods
└─ Guidance Agent ──────→ Implementation guidance
    ↓
Multi-Agent Results
    ↓
Evaluator (3-way comparison)
    ↓
├─ Fair Baseline (CoT)
├─ Multi-Agent
└─ Multi-Agent + RAG (future)
    ↓
Structured JSON Evaluation
```

---

## 📦 Component Specifications

### 1. Root Agent (`root_agent.py`)

**Responsibility:** Pipeline orchestration ONLY

**Interface:**
```python
execute_pipeline(query=None, pdf_path=None) -> dict
```

**Key Methods:**
- `_execute_query_mode(query)` - Run 7-agent pipeline on search results
- `_execute_pdf_mode(pdf_path)` - Run 6-agent pipeline on PDF (skip search)
- `_slice_context(state, agent)` - Extract only required inputs for agent

**State Management:**
```python
results = {
    'query': str,
    'papers': List[dict],
    'synthesis': str,
    'gaps': str,
    'ideas': str,
    'techniques': str,
    'guidance': str,
    'agent_timings': dict
}
```

**Context Slicing Example:**
```python
# Before (bad): Full state passed
gaps_result = self.gap_finder_agent.run(results)

# After (good): Only required inputs
gaps_result = self.gap_finder_agent.run(
    self._slice_context(results, self.gap_finder_agent)
)
# Gap Finder receives: {'synthesis': "..."}
```

---

### 2. The 7 Specialized Agents

#### Search Agent (`agents/search_agent.py`)
- **Job:** Find papers from arXiv + Semantic Scholar
- **Input:** `{'query': str}`
- **Output:** `{'papers': List[dict], 'count': int}`
- **Config:** `MAX_PAPERS = 7` (from config.py)

#### Summarizer Agent (`agents/summarize_agent.py`)
- **Job:** Summarize each paper independently
- **Input:** `{'papers': List[dict]}`
- **Output:** `{'papers': List[dict]}` (with 'summary' added)
- **Technique:** Chunking for long abstracts (2000 tokens max)

#### Synthesizer Agent (`agents/synthesize_agent.py`)
- **Job:** Extract cross-paper themes, patterns, trends
- **Input:** `{'papers': List[dict]}`
- **Output:** `{'synthesis': str}`
- **Focus:** What do papers have in COMMON?

#### Gap Finder Agent (`agents/gap_finder_agent.py`)
- **Job:** Identify missing research areas
- **Input:** `{'synthesis': str}`
- **Output:** `{'gaps': str}`
- **Focus:** What's NOT being studied?

#### Idea Generator Agent (`agents/idea_generator_agent.py`)
- **Job:** Generate 3-5 novel research ideas
- **Input:** `{'gaps': str, 'synthesis': str}`
- **Output:** `{'ideas': str, 'idea_count': int}`
- **Constraint:** Must be feasible, address gaps

#### Technique Agent (`agents/technique_agent.py`)
- **Job:** Suggest alternative algorithms NOT in papers
- **Input:** `{'synthesis': str, 'ideas': str}`
- **Output:** `{'techniques': str}`
- **Focus:** What methods WEREN'T tried?

#### Guidance Agent (`agents/guidance_agent.py`)
- **Job:** Provide difficulty, skills, timeline estimates
- **Input:** `{'ideas': str, 'techniques': str}`
- **Output:** `{'guidance': str}`
- **Format:** Structured guidance per idea

---

### 3. Fair Baseline Agent (`agents/fair_baseline_agent.py`)

**Purpose:** Honest comparison - NOT a strawman

**Structured 5-Step CoT Prompt:**
```
1. Summarize each paper
2. Extract common themes
3. Identify research gaps
4. Generate novel ideas
5. Suggest alternative techniques
```

**Critical:** Receives SAME papers as multi-agent
```python
# Fair comparison
baseline_result = baseline_agent.run({'papers': papers})
multi_agent_result = root_agent.execute_pipeline(query=query)
# Both see same papers!
```

**Required Inputs:** `['papers']`

---

### 4. Evaluator (`evaluation/evaluator.py`)

**Job:** 3-way comparison with structured metrics

**Configurations Compared:**
1. **Fair Baseline** - Structured CoT (single prompt)
2. **Multi-Agent** - 7-agent pipeline
3. **Multi-Agent + RAG** - Future (with PDF embeddings)

**Scoring Dimensions (1-5 scale):**
- **Coverage:** Breadth of analysis
- **Specificity:** Technical depth
- **Actionability:** Practical guidance quality

**Output Format:**
```json
{
  "timestamp": "2024-...",
  "query": "...",
  "rag_enabled": false,
  
  "scores": {
    "fair_baseline": {
      "coverage_score": 3,
      "specificity_score": 3,
      "actionability_score": 2
    },
    "multi_agent": {
      "coverage_score": 5,
      "specificity_score": 5,
      "actionability_score": 5
    }
  },
  
  "latency_comparison": {
    "fair_baseline_seconds": 8.2,
    "multi_agent_seconds": 32.5
  },
  
  "cost_estimate": {
    "fair_baseline_usd": 0.0085,
    "multi_agent_usd": 0.0320
  },
  
  "winner": "multi_agent",
  "notes": "..."
}
```

**Saved to:** `evaluation/run_<timestamp>.json`

---

## 🗂️ File Structure

```
ReAssist/
├── agents/
│   ├── search_agent.py          # Paper discovery
│   ├── summarize_agent.py       # Paper summarization
│   ├── synthesize_agent.py      # Cross-paper synthesis
│   ├── gap_finder_agent.py      # Gap identification
│   ├── idea_generator_agent.py  # Idea generation
│   ├── technique_agent.py       # Alternative techniques
│   ├── guidance_agent.py        # Implementation guidance
│   └── fair_baseline_agent.py   # Honest CoT baseline
│
├── evaluation/
│   ├── evaluator.py             # 3-way comparison engine
│   └── run_*.json               # Evaluation results
│
├── utils/
│   ├── helpers.py               # Text chunking, cleaning
│   ├── logger.py                # Pipeline logging
│   ├── pdf_parser.py            # PDF text extraction
│   ├── json_parser.py           # Robust LLM JSON parsing
│   └── context_slicer.py        # Context slicing helpers
│
├── logs/
│   └── pipeline_*.json          # Execution logs
│
├── root_agent.py                # Main orchestrator
├── config.py                    # Centralized constants
├── cli.py                       # Command-line interface
├── app.py                       # Streamlit UI
│
├── test_integration.py          # End-to-end tests
├── verify_manual.py             # Manual verification script
│
├── requirements.txt             # Dependencies
├── .env                         # API keys
│
└── Documentation/
    ├── README.md                # User guide
    ├── PDF_UPLOAD_GUIDE.md      # PDF mode documentation
    ├── BLUEPRINT.md             # This file
    ├── STATUS.md                # Current status
    └── VERIFICATION_GUIDE.md    # Testing instructions
```

---

## 🔄 Data Flow Example

### Query Mode

```python
# User input
query = "transformer attention mechanisms"

# Stage 1: Search
papers = search_agent.run({'query': query})
# → 7 papers from arXiv/Semantic Scholar

# Stage 2: Summarize
papers = summarizer.run({'papers': papers})
# → Each paper now has 'summary' field

# Stage 3: Synthesize
synthesis = synthesizer.run({'papers': papers})
# → "Common themes: self-attention, multi-head..."

# Stage 4: Find Gaps
gaps = gap_finder.run({'synthesis': synthesis})
# → "Missing: sparse attention, dynamic..."

# Stage 5: Generate Ideas
ideas = idea_generator.run({'gaps': gaps, 'synthesis': synthesis})
# → "Idea 1: Hybrid sparse-dense attention..."

# Stage 6: Techniques
techniques = technique.run({'synthesis': synthesis, 'ideas': ideas})
# → "Try graph attention, state space models..."

# Stage 7: Guidance
guidance = guidance.run({'ideas': ideas, 'techniques': techniques})
# → "Idea 1: Difficulty=Intermediate, 3-6 months..."
```

### Context Slicing in Action

```python
# Root agent state
state = {
    'query': '...',
    'papers': [...],
    'synthesis': '...',
    'gaps': '...',
    'ideas': '...'
}

# Gap Finder only needs synthesis
gap_finder.required_inputs = ['synthesis']
gap_input = _slice_context(state, gap_finder)
# → {'synthesis': '...'}  # Only this!

# Idea Generator needs gaps + synthesis
idea_generator.required_inputs = ['gaps', 'synthesis']
idea_input = _slice_context(state, idea_generator)
# → {'gaps': '...', 'synthesis': '...'}  # Only these!
```

---

## ⚙️ Configuration (`config.py`)

```python
# Search Settings
MAX_PAPERS = 7                    # Max papers per query
DEFAULT_PAPERS = 5

# Model Settings
DEFAULT_MODEL = "gpt-3.5-turbo"
AVAILABLE_MODELS = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"]

# Agent Settings
MAX_CHUNK_TOKENS = 2000           # Text chunking limit
SUMMARIZER_MAX_TOKENS = 500
SYNTHESIZER_MAX_TOKENS = 1500

# RAG Settings (future)
RAG_TOP_K = 10
RAG_CHUNK_SIZE = 500
EMBEDDING_MODEL = "text-embedding-ada-002"

# Cost Tracking (USD per 1K tokens)
PRICING = {
    'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
    'gpt-4': {'input': 0.03, 'output': 0.06},
    'text-embedding-ada-002': 0.0001
}
```

---

## 🧪 Testing & Verification

### Integration Test
```bash
python test_integration.py
```
- Runs 7-agent pipeline
- Executes 3-way evaluation
- Verifies JSON output
- Fast (uses 3 papers)

### Manual Verification
```bash
python verify_manual.py
```
- Shows context slicing in action
- Prints what each agent receives
- Verifies baseline fairness
- Checks evaluation output

### Expected Output
```
→ SearchAgent receives: ['query']
→ SummarizerAgent receives: ['papers']
→ SynthesizerAgent receives: ['papers']
→ GapFinderAgent receives: ['synthesis']
→ IdeaGeneratorAgent receives: ['gaps', 'synthesis']
→ TechniqueAgent receives: ['synthesis', 'ideas']
→ GuidanceAgent receives: ['ideas', 'techniques']

✓ Pipeline completed
✓ Evaluation complete
  Winner: multi_agent
```

---

## 💰 Cost Analysis

### Per-Query Estimates (GPT-3.5-turbo, 7 papers)

**Fair Baseline:**
- 1 LLM call
- Input: ~2,500 tokens (papers + prompt)
- Output: ~2,000 tokens
- **Cost: ~$0.008**

**Multi-Agent:**
- 7 LLM calls
- Search: 1,000 tokens total
- Summarizer: 14,000 tokens (7 papers × 2K)
- Other 5 agents: ~5,000 tokens
- **Cost: ~$0.032**

**Multi-Agent + RAG (future):**
- Above + embedding costs
- ~10K tokens to embed
- **Cost: ~$0.033**

**Tradeoff:** Multi-agent is ~4x more expensive but provides specialized analysis

---

## 🔐 Security & API Keys

### Environment Variables (.env)
```bash
OPENAI_API_KEY=sk-...
MODEL_NAME=gpt-3.5-turbo  # Optional override
```

### .gitignore
```
.env
logs/
evaluation/
__pycache__/
*.pyc
```

---

## 🚀 Usage Examples

### CLI
```bash
# Basic query
python cli.py "transformer attention mechanisms"

# Specify model
python cli.py --model gpt-4 "quantum computing"

# PDF mode
python cli.py --pdf paper.pdf

# Evaluation mode
python cli.py --evaluate "deep learning optimization"
```

### Programmatic
```python
from root_agent import create_root_agent
from evaluation.evaluator import create_evaluator

# Run multi-agent
agent = create_root_agent()
results = agent.execute_pipeline(query="attention mechanisms")

# Run evaluation
evaluator = create_evaluator()
eval_results = evaluator.run_three_way_comparison(
    query="attention mechanisms",
    papers=results['papers'],
    multi_agent_results=results,
    rag_enabled=False
)

print(f"Winner: {eval_results['winner']}")
```

---

## 📊 System Capabilities

### ✅ Implemented
- Query mode (7-agent pipeline)
- PDF upload mode (single PDF)
- Fair baseline comparison
- 3-way evaluation
- Structured JSON output
- Cost estimation
- Latency tracking
- Context slicing
- Logging system

### 🔄 Future Expansion
- RAG retriever agent
- ChromaDB integration
- Multi-PDF support (5-7 PDFs)
- History persistence
- Enhanced cost tracker
- Web UI improvements

---

## 🎓 Design Rationale

### Why Multi-Agent?

**Advantages:**
- Specialized prompts per task
- Better error isolation
- Incremental validation
- Clear separation of concerns

**Tradeoffs:**
- Higher latency (7 API calls)
- Higher cost (~4x baseline)
- More complex orchestration

### Why Fair Baseline?

**Problem:** Naive single-prompt comparison is unfair
**Solution:** Structured CoT with same context
**Result:** Honest evaluation showing real tradeoffs

### Why Context Slicing?

**Problem:** Passing full state bloats tokens
**Solution:** Each agent gets ONLY required inputs
**Result:** Lower costs, cleaner interfaces

---

## 📈 Performance Characteristics

### Latency
- **Fair Baseline:** ~8-10 seconds
- **Multi-Agent:** ~30-40 seconds
- **Multi-Agent + RAG:** ~35-45 seconds (future)

### Token Usage (per query, 7 papers)
- **Fair Baseline:** ~4,500 tokens
- **Multi-Agent:** ~20,000 tokens
- **Multi-Agent + RAG:** ~25,000 tokens (future)

### Accuracy (heuristic)
- **Coverage:** Multi-agent > Baseline
- **Specificity:** Multi-agent > Baseline
- **Actionability:** Multi-agent >> Baseline (dedicated guidance)

---

## 🔧 Maintenance & Extension

### Adding a New Agent

1. Create `agents/new_agent.py`:
```python
class NewAgent:
    required_inputs = ['dependency1', 'dependency2']
    
    def run(self, input_data):
        # Validate inputs
        dep1 = input_data.get('dependency1')
        
        # Do work
        result = process(dep1)
        
        # Return standard format
        return {
            'output_key': result,
            'success': True,
            'error': None
        }
```

2. Update `root_agent.py`:
```python
from agents.new_agent import create_new_agent

self.new_agent = create_new_agent()

# In pipeline
new_result = self.new_agent.run(
    self._slice_context(results, self.new_agent)
)
```

3. Update evaluation scores if needed

### Modifying Evaluation

Edit `evaluation/evaluator.py`:
- Change scoring logic in `_compute_scores()`
- Adjust cost estimates in `_estimate_costs()`
- Update winner determination in `_determine_winner()`

---

## 📝 Key Files to Understand

**Start here:**
1. `root_agent.py` - Orchestration logic
2. `agents/fair_baseline_agent.py` - Baseline implementation
3. `evaluation/evaluator.py` - 3-way comparison

**Then explore:**
4. `agents/search_agent.py` - See agent pattern
5. `config.py` - System constants
6. `utils/context_slicer.py` - Slicing logic

---

## 🎯 Interview Talking Points

### Architecture
- "7 specialized agents with strict single responsibility"
- "Context slicing prevents state bloat - agents get ONLY required inputs"
- "Deterministic orchestration - root agent controls flow"

### Evaluation
- "Fair baseline receives same papers as multi-agent"
- "3-way comparison: CoT vs Multi-Agent vs Multi-Agent+RAG"
- "Heuristic scoring acknowledged as estimates, not ground truth"

### Engineering
- "Standard run(dict) -> dict interface across all agents"
- "No agent-to-agent calls - clean dependency graph"
- "Centralized config eliminates magic numbers"

---

## 🐛 Common Issues & Solutions

### Issue: Agent receives wrong inputs
**Diagnosis:** Check `agent.required_inputs` attribute
**Fix:** Update required_inputs list or verify _slice_context() call

### Issue: Baseline sees different papers
**Diagnosis:** Check papers passed to evaluator
**Fix:** Ensure same `results['papers']` passed to both

### Issue: Evaluation fails
**Diagnosis:** Check evaluation/*.json files for errors
**Fix:** Verify baseline_agent.run() succeeds, check API key

### Issue: High costs
**Diagnosis:** Too many papers or large abstracts
**Fix:** Reduce MAX_PAPERS in config.py, use chunking

---

**Blueprint Version:** 1.0 (Tier-1 Stabilization Complete)
**Last Updated:** 2024-02-15
**Status:** Production-Ready (Query Mode)
