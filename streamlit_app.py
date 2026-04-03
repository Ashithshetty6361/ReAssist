"""
Streamlit Web UI for Research Intelligence Engine
Optional web interface as an alternative to CLI
"""

import streamlit as st
import os
import json
from dotenv import load_dotenv
from root_agent import create_root_agent
from evaluation.evaluator import create_evaluator
from utils.helpers import format_paper_metadata

# Load environment variables
load_dotenv()

from config import validate_environment
try:
    validate_environment()
except EnvironmentError as e:
    import streamlit as st
    st.error(str(e))
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Research Intelligence Engine",
    page_icon="🔬",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stage-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .paper-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)


def check_api_key():
    """Check if OpenAI API key is configured"""
    api_key = os.getenv("OPENAI_API_KEY")
    return api_key and api_key != "your_openai_api_key_here"

def get_routing_stats():
    records = []
    try:
        with open("logs/routing_log.jsonl", "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    except FileNotFoundError:
        pass
    return records


def main():
    # Header
    st.markdown('<h1 class="main-header">🔬 Research Intelligence Engine</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Multi-Agent Literature Analyzer</p>', unsafe_allow_html=True)
    
    # Check API key
    if not check_api_key():
        st.error("⚠️ OpenAI API key not configured!")
        st.info("Please add your API key to the `.env` file:\n```\nOPENAI_API_KEY=your_key_here\n```")
        st.stop()
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    model = st.sidebar.selectbox(
        "Model",
        ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"],
        index=0,
        help="GPT-3.5-turbo is faster and cheaper, GPT-4 is higher quality"
    )
    
    max_papers = st.sidebar.slider(
        "Number of Papers",
        min_value=1,
        max_value=10,
        value=5,
        help="More papers = better analysis but slower"
    )
    
    run_evaluation = st.sidebar.checkbox(
        "Run Evaluation",
        value=True,
        help="Compare multi-agent output with single LLM baseline"
    )
    

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 About")
    st.sidebar.info(
        "This multi-agent system analyzes research papers and generates "
        "actionable insights through specialized AI agents."
    )
    
    # Main content
    query = st.text_input(
        "🔍 Enter research topic or question:",
        placeholder="e.g., attention mechanisms in transformers",
        help="Enter a research topic to find and analyze relevant papers"
    )
    
    st.markdown("**OR**")
    uploaded_pdf = st.file_uploader("📄 Upload Research PDF (RAG Mode)", type="pdf")
    
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        run_button = st.button("🚀 Analyze", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_button:
        # Clear session state cache too
        if 'analysis_results' in st.session_state:
            del st.session_state['analysis_results']
        if 'chat_messages' in st.session_state:
            del st.session_state['chat_messages']
        st.rerun()
    
    if run_button and (query or uploaded_pdf):
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Create root agent
            status_text.text("Initializing agents...")
            progress_bar.progress(5)
            
            root_agent = create_root_agent(model=model, max_papers=max_papers)
            
            # Run pipeline
            status_text.text("🔍 Stage 1/6: Acquiring context...")
            progress_bar.progress(15)
            
            with st.spinner("Running multi-agent pipeline..."):
                if uploaded_pdf:
                    os.makedirs("data/uploads", exist_ok=True)
                    pdf_path = os.path.join("data/uploads", uploaded_pdf.name)
                    with open(pdf_path, "wb") as f:
                        f.write(uploaded_pdf.getbuffer())
                    results = root_agent.execute_pipeline(pdf_path=pdf_path)
                else:
                    results = root_agent.execute_pipeline(query)
                    from router import create_router
                    router = create_router()
                    routing = router.route(query)
                    router.log_decision(query, routing)
            
            st.session_state['analysis_results'] = results
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            
            # Display results
            # Display results from state
            results = st.session_state.get('analysis_results', {})
            if results.get('error'):
                st.error(f"❌ Pipeline failed: {results['error']}")
            else:
                # Papers section
                st.markdown('<div class="stage-header"><h2>📚 Papers Analyzed</h2></div>', unsafe_allow_html=True)
                
                for idx, paper in enumerate(results.get('papers', [])):
                    with st.expander(f"📄 {idx+1}. {paper['title']}", expanded=False):
                        st.markdown(f"**Authors:** {', '.join(paper['authors'][:5])}")
                        st.markdown(f"**Year:** {paper['year']}")
                        st.markdown(f"**Source:** {paper['source']}")
                        st.markdown(f"**Summary:** {paper.get('summary', 'N/A')}")
                
                # Synthesis
                synthesis = results.get('synthesis', {})
                if synthesis.get('synthesis_text'):
                    st.markdown('<div class="stage-header"><h2>📊 Knowledge Synthesis</h2></div>', unsafe_allow_html=True)
                    st.markdown(synthesis['synthesis_text'])
                
                # Research Gaps
                gaps = results.get('gaps', {})
                if gaps.get('gaps_text'):
                    st.markdown('<div class="stage-header"><h2>🔍 Research Gaps</h2></div>', unsafe_allow_html=True)
                    st.markdown(gaps['gaps_text'])
                
                # Research Ideas
                ideas = results.get('ideas', {})
                if ideas.get('ideas_text'):
                    st.markdown('<div class="stage-header"><h2>💡 Novel Research Ideas</h2></div>', unsafe_allow_html=True)
                    st.markdown(ideas['ideas_text'])
                
                # Techniques
                techniques = results.get('techniques', {})
                if techniques.get('techniques_text'):
                    st.markdown('<div class="stage-header"><h2>🛠️ Alternative Techniques</h2></div>', unsafe_allow_html=True)
                    st.markdown(techniques['techniques_text'])
                
                # Performance summary
                summary = root_agent.get_performance_summary()
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                col1.metric("⏱️ Total Time", f"{summary['total_time']:.1f}s")
                col2.metric("📚 Papers Analyzed", summary['papers_found'])
                col3.metric("🤖 Agents Used", summary['agent_count'])
                
                # Evaluation
                if run_evaluation:
                    st.markdown('<div class="stage-header"><h2>🔬 Evaluation</h2></div>', unsafe_allow_html=True)
                    
                    with st.spinner("Running baseline comparison..."):
                        evaluator = create_evaluator(model=model)
                        comparison = evaluator.run_baseline_comparison(
                            query,
                            results.get('papers', []),
                            results
                        )
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### Single LLM Baseline")
                        st.metric("Duration", f"{comparison['baseline']['duration_seconds']:.1f}s")
                        st.metric("LLM Calls", comparison['baseline']['llm_calls'])
                    
                    with col2:
                        st.markdown("### Multi-Agent Pipeline")
                        st.metric("Duration", f"{comparison['multi_agent']['duration_seconds']:.1f}s")
                        st.metric("LLM Calls", comparison['multi_agent']['llm_calls'])
                    
                    st.markdown("### Baseline Output")
                    st.text_area("Single LLM Response", comparison['baseline']['output'], height=200)

                st.markdown("---")
                st.subheader("AgenticOps Cost Intelligence")

                records = get_routing_stats()

                if records:
                    total = len(records)
                    cot_count = sum(1 for r in records if r.get("decision") == "cot")
                    ma_count = total - cot_count
                    total_saved = sum(r.get("cost_saved_vs_always_multi_agent", 0)
                                      for r in records)
                    actual_cost = sum(r.get("estimated_cost_usd", 0) for r in records)
                    always_multi_cost = actual_cost + total_saved

                    latest = records[-1]
                    this_decision = latest.get("decision", "unknown")
                    this_saved = latest.get("cost_saved_vs_always_multi_agent", 0)
                    this_cost = latest.get("estimated_cost_usd", 0)

                    if this_decision == "cot":
                        st.success(
                            f"Router saved ${this_saved:.4f} on this query by routing "
                            f"to CoT instead of multi-agent pipeline."
                        )
                    else:
                        st.info(
                            "Router selected multi-agent pipeline — "
                            "query complexity justified the cost."
                        )

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("This run cost", f"${this_cost:.4f}")
                    with col2:
                        st.metric("Multi-agent would cost", "$0.0060")
                    with col3:
                        st.metric("Saved this run", f"${this_saved:.4f}")

                    st.markdown("**Cumulative routing stats:**")
                    col4, col5, col6, col7 = st.columns(4)
                    with col4:
                        st.metric("Total queries", total)
                    with col5:
                        st.metric("Routed to CoT", f"{cot_count} ({cot_count/total*100:.0f}%)")
                    with col6:
                        st.metric("Total saved", f"${total_saved:.4f}")
                    with col7:
                        st.metric("vs always multi-agent", f"${always_multi_cost:.4f}")
                else:
                    st.info("Run a query to see cost analytics.")
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())
    
    elif run_button:
        st.warning("⚠️ Please provide a query or upload a PDF!")
        
    # Conversational Memory Render Block
    if st.session_state.get('analysis_results') and not st.session_state['analysis_results'].get('error'):
        st.markdown("---")
        st.subheader("💬 Discuss Results (Conversational Memory)")
        
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []
            
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        if user_prompt := st.chat_input("Ask a follow-up question based on the analysis..."):
            st.session_state.chat_messages.append({"role": "user", "content": user_prompt})
            
            # Instruct the user that this requires backend chat agent integration for live RAG
            st.session_state.chat_messages.append({"role": "assistant", "content": "Chat implementation requires the RAG layer (Phase 5). Connect an OpenAI key to engage with this context."})
            st.rerun()

    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #666;'>"
        "Built with proper AI engineering principles 🚀 | "
        "<a href='https://github.com/yourusername/ReAssist'>GitHub</a>"
        "</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
