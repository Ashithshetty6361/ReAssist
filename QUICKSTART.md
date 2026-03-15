# Quick Start Guide

## Setup (5 minutes)

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API key**
   ```bash
   # Copy template
   copy .env.example .env
   
   # Edit .env and add your key
   OPENAI_API_KEY=sk-your-key-here
   ```

3. **Run the application**
   ```bash
   # CLI version
   python main.py
   
   # Web UI version (optional)
   streamlit run streamlit_app.py
   ```

## Example Usage

### CLI
```
Query: deep learning for medical imaging
Model: gpt-3.5-turbo
Max Papers: 5
Run Evaluation: Yes
```

### Expected Output
- 5 papers from arXiv/Semantic Scholar
- Synthesis of key findings
- 5-10 research gaps identified
- 5 novel research ideas
- Alternative techniques with guidance
- Evaluation comparison

## Cost Estimate
- GPT-3.5-turbo: ~$0.10 per query
- GPT-4: ~$1.00 per query

## Troubleshooting

**"No papers found"**
- Try broader search terms
- Check internet connection

**"API key not configured"**
- Verify .env file exists
- Check OPENAI_API_KEY is set correctly

**"Rate limit error"**
- Wait a minute and retry
- Consider upgrading OpenAI plan

## Next Steps
- Review logs/ for execution details
- Check evaluation/ for quality comparisons
- Customize agents in agents/ directory
