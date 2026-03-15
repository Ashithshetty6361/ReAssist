# Paper Upload Mode - Usage Guide

## 🎯 What It Is

A second entry point into the research pipeline that analyzes **a single uploaded PDF** instead of searching multiple papers.

## 🔄 Two Modes Available

### Mode A: Query Mode (Original)
```python
from root_agent import create_root_agent

agent = create_root_agent()
results = agent.execute_pipeline(query="attention mechanisms in transformers")
```

**Flow:** Search → Summarize → Synthesize → Gaps → Ideas → Techniques → Guidance

### Mode B: PDF Upload Mode (NEW)
```python
from root_agent import create_root_agent

agent = create_root_agent()
results = agent.execute_pipeline(pdf_path="paper.pdf")
```

**Flow:** Extract PDF → Summarize → Synthesize → Gaps → Ideas → Techniques → Guidance

## 📦 Installation

```bash
# Install PDF parsing library
pip install pdfplumber

# Or install all requirements
pip install -r requirements.txt
```

## 🚀 Usage Examples

### Example 1: Analyze Your Own Research Paper

```python
from root_agent import create_root_agent

# Initialize agent
agent = create_root_agent(model="gpt-3.5-turbo")

# Upload your paper
results = agent.execute_pipeline(pdf_path="my_research_paper.pdf")

# Get outputs
print("📄 Summary:", results['papers'][0]['summary'])
print("🔍 Limitations:", results['gaps'])
print("💡 Novelty Opportunities:", results['ideas'])
print("🛠️ Alternative Techniques:", results['techniques'])
print("📋 Implementation Guidance:", results['guidance'])
```

### Example 2: Compare Against Your Paper

```python
# Analyze your paper
my_paper = agent.execute_pipeline(pdf_path="my_paper.pdf")

# Analyze existing research in the same domain
related_work = agent.execute_pipeline(query="same topic as my paper")

# Compare gaps and ideas
print("Gaps in my paper:", my_paper['gaps'])
print("Gaps in existing research:", related_work['gaps'])
```

## 📊 What You Get

**For each uploaded paper:**

1. **Summary** - Key contributions, methods, results, limitations
2. **Drawbacks** - Identified via Gap Finder Agent
   - Methodological limitations
   - Missing benchmarks
   - Unexplored combinations
3. **Novelty Opportunities** - 5 concrete research ideas
4. **Alternative Techniques** - 3-5 different approaches not used
5. **Implementation Guidance** - Difficulty, skills, timeline

## ⚙️ How It Works (Under the Hood)

```python
# PDF Mode skips search agent
if pdf_path:
    return self._execute_pdf_mode(pdf_path)

# _execute_pdf_mode():
# 1. Extract text from PDF (pdfplumber)
# 2. Convert to paper dict format
# 3. Send to summarizer (same agent as query mode)
# 4. Continue through rest of pipeline (no code duplication)
```

**Key:** Reuses ALL 7 agents. Zero duplication.

## 📝 Logging

PDF mode is logged identically to query mode:

```json
{
  "mode": "pdf_upload",
  "pdf_path": "paper.pdf",
  "agent_timings": {
    "pdf_extraction": 1.2,
    "summarizer": 8.3,
    "synthesizer": 5.1,
    "gap_finder": 4.2,
    "idea_generator": 6.5,
    "technique": 3.8,
    "guidance": 4.1
  }
}
```

## ⚠️ Limitations

### 1. PDF Quality Matters
- Scanned PDFs (images) → Poor extraction
- Two-column layouts → May have ordering issues
- Equations/tables → May not extract cleanly

### 2. Title Extraction is Heuristic
```python
# We guess the title from first lines
# May not always be accurate
```

### 3. Author/Year Not Extracted
- Returned as "Unknown"
- Could be added with more PDF metadata parsing

### 4. Full Text Processing
- Very long papers (> 20 pages) → High token cost
- Summarizer uses chunking but still expensive

## 🎓 Use Cases

**Perfect for:**
- Analyzing your own draft papers
- Getting feedback on research ideas
- Finding gaps in your methodology
- Discovering alternative approaches
- Comparing with existing work

**Not for:**
- Scanned PDFs (no OCR support)
- Non-academic documents
- Bulk analysis (expensive per paper)

## 💰 Cost Estimate

**Single Paper Analysis (10 pages, GPT-3.5-turbo):**
- PDF extraction: Free
- Summarizer: ~$0.04 (long content)
- Synthesizer: ~$0.02
- Gap Finder: ~$0.02
- Idea Generator: ~$0.025
- Technique: ~$0.015
- Guidance: ~$0.02
- **Total: ~$0.13-0.15 per paper**

## 🔧 Advanced: CLI Integration

```python
# In main.py (example)
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--query', type=str, help='Research topic')
parser.add_argument('--pdf', type=str, help='Path to PDF file')
args = parser.parse_args()

agent = create_root_agent()

if args.pdf:
    results = agent.execute_pipeline(pdf_path=args.pdf)
else:
    results = agent.execute_pipeline(query=args.query)
```

**Usage:**
```bash
# Query mode
python main.py --query "transformers"

# PDF mode
python main.py --pdf "my_paper.pdf"
```

## 🎯 Interview Talking Point

**Q: Why not create separate PDF analysis agents?**

**A:** "I reused the existing 7-agent pipeline. PDF upload is just an alternate entry point - it skips search and starts from summarizer. This follows DRY principles and reduces code duplication. The Gap Finder identifies drawbacks, Idea Generator finds novelty opportunities, exactly as designed. Zero new agents needed."

**That's good engineering.**
