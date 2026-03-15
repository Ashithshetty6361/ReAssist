"""
Research Intelligence Engine - Main CLI Interface
Multi-Agent Literature Analyzer
"""

import os
import sys
from dotenv import load_dotenv
from root_agent import create_root_agent
from evaluation.evaluator import create_evaluator
from utils.helpers import format_paper_metadata

# Load environment variables
load_dotenv()


def print_banner():
    """Print application banner"""
    print("\n" + "=" * 80)
    print(" " * 15 + "RESEARCH INTELLIGENCE ENGINE")
    print(" " * 15 + "Multi-Agent Literature Analyzer")
    print("=" * 80 + "\n")


def print_results(results):
    """
    Pretty-print pipeline results
    
    Args:
        results: Results dictionary from pipeline
    """
    print("\n" + "=" * 80)
    print("RESEARCH ANALYSIS RESULTS")
    print("=" * 80)
    
    # Papers found
    print(f"\n📚 Papers Analyzed: {len(results.get('papers', []))}")
    print("-" * 80)
    for idx, paper in enumerate(results.get('papers', [])):
        print(f"\n{idx+1}. {format_paper_metadata(paper)}")
        print(f"   Source: {paper.get('source', 'Unknown')}")
    
    # Synthesis
    synthesis = results.get('synthesis', {})
    if synthesis.get('synthesis_text'):
        print("\n" + "=" * 80)
        print("📊 KNOWLEDGE SYNTHESIS")
        print("=" * 80)
        print(synthesis['synthesis_text'])
    
    # Research Gaps
    gaps = results.get('gaps', {})
    if gaps.get('gaps_text'):
        print("\n" + "=" * 80)
        print("🔍 RESEARCH GAPS IDENTIFIED")
        print("=" * 80)
        print(gaps['gaps_text'])
    
    # Research Ideas
    ideas = results.get('ideas', {})
    if ideas.get('ideas_text'):
        print("\n" + "=" * 80)
        print("💡 NOVEL RESEARCH IDEAS")
        print("=" * 80)
        print(ideas['ideas_text'])
    
    # Technique Suggestions
    techniques = results.get('techniques', {})
    if techniques.get('techniques_text'):
        print("\n" + "=" * 80)
        print("🛠️  ALTERNATIVE TECHNIQUES & GUIDANCE")
        print("=" * 80)
        print(techniques['techniques_text'])
    
    print("\n" + "=" * 80)


def validate_api_key():
    """Validate that OpenAI API key is set"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ ERROR: OpenAI API key not configured!")
        print("\nPlease set your API key in one of these ways:")
        print("1. Create a .env file with: OPENAI_API_KEY=your_key_here")
        print("2. Set environment variable: set OPENAI_API_KEY=your_key_here")
        print("\nGet your API key from: https://platform.openai.com/api-keys")
        return False
    return True


def get_user_query():
    """Get research query from user"""
    print("\n📝 Enter your research topic or question:")
    print("   (e.g., 'attention mechanisms in transformers')")
    print("   (or type 'exit' to quit)\n")
    query = input("Query: ").strip()
    
    if query.lower() == 'exit':
        return None
    
    if not query:
        print("❌ Query cannot be empty!")
        return get_user_query()
    
    return query


def get_configuration():
    """Get configuration from user"""
    print("\n⚙️  Configuration:")
    
    # Model selection
    print("\nSelect model:")
    print("1. gpt-3.5-turbo (faster, cheaper)")
    print("2. gpt-4 (better quality, slower, more expensive)")
    print("3. gpt-4-turbo-preview (best quality)")
    
    model_choice = input("\nChoice (1-3, default 1): ").strip() or "1"
    
    model_map = {
        "1": "gpt-3.5-turbo",
        "2": "gpt-4",
        "3": "gpt-4-turbo-preview"
    }
    model = model_map.get(model_choice, "gpt-3.5-turbo")
    
    # Max papers
    max_papers_input = input("\nNumber of papers to analyze (default 5): ").strip() or "5"
    try:
        max_papers = int(max_papers_input)
        max_papers = max(1, min(max_papers, 10))  # Clamp between 1-10
    except ValueError:
        max_papers = 5
    
    # Run evaluation
    run_eval = input("\nRun evaluation comparison? (y/n, default y): ").strip().lower() or "y"
    run_evaluation = run_eval == 'y'
    
    return {
        'model': model,
        'max_papers': max_papers,
        'run_evaluation': run_evaluation
    }


def main():
    """Main application entry point"""
    print_banner()
    
    # Validate API key
    if not validate_api_key():
        sys.exit(1)
    
    # Get configuration
    config = get_configuration()
    
    print(f"\n✅ Configuration:")
    print(f"   Model: {config['model']}")
    print(f"   Max Papers: {config['max_papers']}")
    print(f"   Evaluation: {'Yes' if config['run_evaluation'] else 'No'}")
    
    # Main loop
    while True:
        # Get user query
        query = get_user_query()
        
        if query is None:
            print("\n👋 Goodbye!")
            break
        
        print(f"\n🚀 Starting multi-agent research pipeline...")
        print(f"   Topic: {query}")
        
        # Create and run root agent
        try:
            root_agent = create_root_agent(
                model=config['model'],
                max_papers=config['max_papers']
            )
            
            results = root_agent.execute_pipeline(query)
            
            # Print results
            if results.get('error'):
                print(f"\n❌ Pipeline failed: {results['error']}")
            else:
                print_results(results)
                
                # Run evaluation if requested
                if config['run_evaluation']:
                    print("\n🔬 Running evaluation comparison...")
                    evaluator = create_evaluator(model=config['model'])
                    comparison = evaluator.run_baseline_comparison(
                        query,
                        results.get('papers', []),
                        results
                    )
            
            # Show performance summary
            summary = root_agent.get_performance_summary()
            print(f"\n⏱️  Performance Summary:")
            print(f"   Total time: {summary['total_time']:.2f}s")
            print(f"   Agents executed: {summary['agent_count']}")
            print(f"   Papers found: {summary['papers_found']}")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Pipeline interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Continue or exit
        print("\n" + "=" * 80)
        continue_choice = input("\nAnalyze another topic? (y/n): ").strip().lower()
        if continue_choice != 'y':
            print("\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()
