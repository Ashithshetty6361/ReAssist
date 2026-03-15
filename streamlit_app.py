"""
Streamlit Web UI for Research Intelligence Engine
Optional web interface as an alternative to CLI
"""

import streamlit as st
import os
from dotenv import load_dotenv
from root_agent import create_root_agent
from evaluation.evaluator import create_evaluator
from utils.helpers import format_paper_metadata

# Load environment variables
load_dotenv()

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
    
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        run_button = st.button("🚀 Analyze", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_button:
        st.rerun()
    
    if run_button and query:
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Create root agent
            status_text.text("Initializing agents...")
            progress_bar.progress(5)
            
            root_agent = create_root_agent(model=model, max_papers=max_papers)
            
            # Run pipeline
            status_text.text("🔍 Stage 1/6: Searching for papers...")
            progress_bar.progress(15)
            
            with st.spinner("Running multi-agent pipeline..."):
                results = root_agent.execute_pipeline(query)
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            
            # Display results
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
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())
    
    elif run_button:
        st.warning("⚠️ Please enter a research topic!")
    
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
