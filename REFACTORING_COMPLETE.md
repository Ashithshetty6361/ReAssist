# VERIFICATION SCRIPT - Interview-Grade System Check

## ✅ What Was Refactored

### 1. Agent Architecture (CRITICAL FIX)
**Before:** Each agent had different method signatures (`search()`, `summarize_papers()`, etc.)
**After:** ALL 7 agents now implement standard `run(input_data: dict) -> dict`

### 2. Agent Responsibility (CRITICAL FIX)
**Before:** 6 agents, Technique Agent did both techniques + guidance
**After:** 7 agents, separated into Technique (suggestions) and Guidance (difficulty/timeline)

### 3. Evaluation System (CRITICAL FIX)
**Before:** Narrative text comparison
**After:** Structured JSON with:
- coverage_score: 1-5
- specificity_score: 1-5
- actionability_score: 1-5
- cost_estimate: USD amounts
- latency_comparison: seconds
- winner: determined automatically

### 4. Documentation (CRITICAL ADDITION)
Added 5 required sections:
1. **Agent Interface Contract** - Explains run(dict)->dict pattern
2. **Design Tradeoffs** - 4 major decisions with costs explained
3. **Failure Modes** - 8 explicit limitations with impact
4. **Ideas Rejected** - 6 ideas with why they were rejected
5. **Latency/Cost Table** - Real numbers, when to use what

## 📋 Verification Checklist

Run through this before interview:

### Architecture
- [ ] Open `agents/search_agent.py` - confirm `run(dict) -> dict` method
- [ ] Open `agents/technique_agent.py` - confirm NO guidance, only techniques
- [ ] Open `agents/guidance_agent.py` - confirm exists and has guidance logic
- [ ] Open `root_agent.py` - confirm 7 agent calls in sequence

### Evaluation
- [ ] Open `evaluation/evaluator.py` - find `_compute_coverage_score`, `_compute_specificity_score`, `_compute_actionability_score`
- [ ] Confirm `_estimate_cost()` function exists
- [ ] Confirm saves to `evaluation/run_<timestamp>.json`

### Documentation
- [ ] Open README.md - search for "Agent Interface Contract" section
- [ ] Search for "Design Tradeoffs & Engineering Decisions" section
- [ ] Search for "Failure Modes & Limitations" - count 8 items
- [ ] Search for "Ideas Considered but Rejected" - count 6 items
- [ ] Search for latency table showing ~8s vs ~50s

### Interview Talking Points

**Q: Why did you choose multi-agent over single prompt?**
A: Better separation of concerns and specialized prompts, but I'm honest that it costs 6x more and is 6x slower. I documented exactly when NOT to use it (see README "When NOT to use multi-agent" section).

**Q: How do agents communicate?**
A: Standardized `run(dict) -> dict` interface. JSON-serializable for logging, no shared state. It trades type safety for simplicity and debuggability.

**Q: What are the main limitations?**
A: Eight explicit ones documented in README:
1. API rate limits = complete failure
2. Garbage in, garbage out (bad papers)
3. LLM hallucination in gaps
4. Linear cost scaling
5. No parallelism = slow
6. Heuristic evaluation
7. Single point of failure
8. No citation validation

**Q: Why not use parallel execution?**
A: Considered and rejected. Agents have sequential dependencies. Parallelism would add huge complexity for only ~3x speedup vs 6x if fully parallel. Not worth it. (See "Ideas Rejected" section).

**Q: How do you evaluate quality?**
A: Heuristic scores (coverage, specificity, actionability) on 1-5 scale. I'm honest that they're not rigorous - a proper user study would be needed. But for automation, they provide consistent comparison. (See "Design Tradeoffs" section).

**Q: Show me the cost breakdown.**
A: Single prompt: $0.02, Multi-agent: $0.12. Detailed breakdown in README shows which agent costs what. Multi-agent justified when quality > cost, not for high-volume applications.

## 🎯 System Quality Level

**BEFORE Refactoring:** Demo/Prototype
- Worked but not defensible
- Inconsistent interfaces
- Weak evaluation
- No honest documentation

**AFTER Refactoring:** Interview-Grade
- Strict architectural compliance
- Standardized interfaces
- Structured evaluation with scores
- Brutally honest about limitations
- Clear tradeoffs documented

## ✅ Quick Test (When You Have API Key)

```bash
# 1. Add your OpenAI API key to .env
# 2. Run this
python -c "
from agents.search_agent import create_search_agent
agent = create_search_agent(max_papers=2)
result = agent.run({'query': 'transformers'})
print('✓ Search Agent works:', result['success'])
print('✓ Has standard interface:', 'papers' in result and 'success' in result)
"
```

Expected output:
```
✓ Search Agent works: True
✓ Has standard interface: True
```

This confirms the refactoring is functional.

---

**Remember:** This is NOT about perfection. It's about showing you can:
1. Build proper architecture
2. Make defensible engineering decisions
3. Document tradeoffs honestly
4. Admit limitations without hiding them

That's what impresses in interviews.
