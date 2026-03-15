# 🚀 Quick Setup Guide - Run in 3 Steps!

## Step 1: Install Dependencies ✅ (Running now...)
```bash
pip install -r requirements.txt
```
**This installs:** OpenAI, arXiv, Streamlit, and other libraries
**Time:** ~2-3 minutes

---

## Step 2: Add Your OpenAI API Key 🔑

### Option A: Edit .env file (Recommended)
1. Open `.env` file in notepad
2. Replace `your_openai_api_key_here` with your actual key
3. Save the file

```
OPENAI_API_KEY=sk-proj-your-actual-key-here
MODEL_NAME=gpt-3.5-turbo
MAX_PAPERS=5
```

### Option B: Set environment variable
```bash
set OPENAI_API_KEY=sk-proj-your-key-here
```

### Don't have an API key yet?
1. Go to: https://platform.openai.com/api-keys
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key (starts with sk-)
5. Add $5-10 credit at: https://platform.openai.com/account/billing

---

## Step 3: Run the Project! 🎉

### Option A: CLI Interface (Simple)
```bash
python main.py
```

**What you'll see:**
- Configuration prompts
- Enter your research topic
- Watch agents work in real-time
- Get complete analysis

### Option B: Web UI (Pretty!)
```bash
streamlit run streamlit_app.py
```

**What you'll see:**
- Modern web interface
- Progress bars
- Interactive results
- Beautiful formatting

### Option C: Test First (Recommended!)
```bash
python test_setup.py
```

**This checks:**
- All imports work ✓
- API key is set ✓
- Utilities function ✓
- System ready ✓

---

## 🎯 Example Usage

Once running, try these queries:

**Research Topics:**
- "attention mechanisms in transformers"
- "deep learning for medical imaging"
- "reinforcement learning for robotics"
- "graph neural networks"
- "few-shot learning"

**What you'll get:**
1. 5 relevant research papers
2. Synthesis of key findings
3. Research gaps identified
4. 5 novel research ideas
5. Alternative techniques suggested
6. Difficulty/timeline guidance

---

## 💰 Cost Per Query

**Using GPT-3.5-turbo (default):**
- ~$0.10 per query
- ~50 seconds per query
- Good quality

**Using GPT-4:**
- ~$1.00 per query
- ~60 seconds per query
- Excellent quality

---

## 🆘 Troubleshooting

**"No module named 'X'"**
→ Run: `pip install -r requirements.txt` again

**"API key not configured"**
→ Check your .env file has the key

**"Rate limit error"**
→ Wait 1 minute, try again

**"No papers found"**
→ Try broader search terms

---

## 📁 Files Created

After running, check these folders:

**logs/** - Execution logs
- `research_log_YYYYMMDD_HHMMSS.log` (readable)
- `research_log_YYYYMMDD_HHMMSS.json` (structured data)

**evaluation/** - Quality comparisons
- `comparison_YYYYMMDD_HHMMSS.json`

---

## 🎉 You're Ready!

1. Wait for pip install to finish
2. Add your OpenAI API key
3. Run `python main.py`
4. Enter a research topic
5. Watch the magic happen! ✨
