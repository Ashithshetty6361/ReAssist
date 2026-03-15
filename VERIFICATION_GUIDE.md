# Manual Verification Guide

## What I Just Did

### 1. Added Debug Printing
- Modified `root_agent._slice_context()` to print what each agent receives
- Format: `→ AgentName receives: ['key1', 'key2']`

### 2. Created `verify_manual.py`
- Runs a real query with 2 papers (fast)
- Shows context slicing in action
- Verifies baseline fairness
- Checks evaluation output

### 3. Fixed Lint Error
- Fixed `search_agent.py` line 137 indentation
- Factory function now properly formatted

### 4. Running Verification Test
- `python verify_manual.py` is executing now
- Will show you EXACTLY what each agent receives

---

## How to Verify Manually (After My Test Completes)

### Step 1: Check Context Slicing

Run the verification script:
```bash
cd c:\mitbtech\Agentic_Ai_projects\ReAssist
python verify_manual.py
```

**Look for these lines:**
```
→ SearchAgent receives: ['query']
→ SummarizerAgent receives: ['papers']
→ SynthesizerAgent receives: ['papers']
→ GapFinderAgent receives: ['synthesis']
→ IdeaGeneratorAgent receives: ['gaps', 'synthesis']
→ TechniqueAgent receives: ['synthesis', 'ideas']
→ GuidanceAgent receives: ['ideas', 'techniques']
```

**✓ PASS if:** Each agent gets ONLY its required_inputs
**✗ FAIL if:** Any agent gets extra keys (like 'query', 'gaps' when not needed)

---

### Step 2: Verify Baseline Fairness

In the same output, check:
```
Baseline will receive these papers:
  1. Paper Title...
  2. Paper Title...
```

**Then run baseline manually to see what it gets:**

```python
# In Python shell
from agents.fair_baseline_agent import create_fair_baseline_agent

baseline = create_fair_baseline_agent()
# Papers from your run
papers = [{"title": "...", "abstract": "..."}]  # Copy from output

result = baseline.run({'papers': papers})
print(result['baseline_output'][:500])  # See what baseline produced
```

**✓ PASS if:** Baseline mentions same paper titles as multi-agent saw
**✗ FAIL if:** Baseline sees different papers

---

### Step 3: Stability Test (Run Twice)

```bash
# Run 1
python verify_manual.py > run1.txt

# Run 2 (same query)
python verify_manual.py > run2.txt

# Compare
diff run1.txt run2.txt
```

**✓ PASS if:** 
- Agent timing differs but agent inputs are identical
- Both produce synthesis, gaps, ideas
- No hidden state leaks

**✗ FAIL if:**
- Different agents receive different inputs
- One run succeeds, other fails

---

### Step 4: Check Evaluation JSON

```bash
# After running verify_manual.py
dir evaluation\run_*.json
```

Open the latest JSON file. Verify:
```json
{
  "scores": {
    "fair_baseline": {"coverage_score": X, ...},
    "multi_agent": {"coverage_score": X, ...}
  },
  "latency_comparison": {...},
  "cost_estimate": {...},
  "winner": "multi_agent" or "fair_baseline"
}
```

**✓ PASS if:** JSON is well-formed, has 3 score categories, winner determined
**✗ FAIL if:** Missing fields, error messages

---

## What to Look For

### Good Signs ✓
- Each agent log shows `→ AgentName receives: [expected keys]`
- Baseline receives same papers as multi-agent
- Evaluation JSON saved successfully
- No excessive state (like passing all papers to Gap Finder)

### Red Flags ✗
- Agent receives keys it doesn't need
- Baseline gets different papers than multi-agent
- Evaluation fails or produces error
- State accumulation (all previous results passed to every agent)

---

## After Verification

If all passes:
1. **System is STABLE** ✓
2. **Ready for expansion** (RAG, multi-PDF)
3. **Production-ready** for query mode

If issues found:
1. Note which agent gets wrong inputs
2. Check that agent's `required_inputs` attribute
3. Verify `_slice_context()` logic

---

**I'm running the test now. Wait for completion, then you can run it manually following this guide.**
