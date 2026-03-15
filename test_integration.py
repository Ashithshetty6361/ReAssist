"""
Integration Test - Verifies end-to-end pipeline with fair baseline evaluation
Tests: Query mode, context slicing, 3-way evaluation
"""

import os
from dotenv import load_dotenv
from root_agent import create_root_agent
from evaluation.evaluator import create_evaluator

load_dotenv()

def test_query_mode():
    """Test query mode with fair baseline evaluation"""
    
    print("=" * 80)
    print("INTEGRATION TEST: Query Mode + Fair Baseline Evaluation")
    print("=" * 80)
    
    # Create root agent
    print("\n1. Initializing root agent...")
    agent = create_root_agent(model="gpt-3.5-turbo", max_papers=3)  # Use 3 papers for speed
    print("✓ Root agent initialized")
    
    # Execute pipeline
    print("\n2. Running 7-agent pipeline...")
    query = "transformer attention mechanisms in NLP"
    results = agent.execute_pipeline(query=query)
    
    if results.get('error'):
        print(f"✗ Pipeline failed: {results['error']}")
        return False
    
    print("✓ Pipeline completed")
    print(f"  - Papers: {len(results.get('papers', []))}")
    print(f"  - Synthesis: {len(results.get('synthesis', ''))} chars")
    print(f"  - Gaps: {len(results.get('gaps', ''))} chars")
    print(f"  - Ideas: {len(results.get('ideas', ''))} chars")
    print(f"  - Techniques: {len(results.get('techniques', ''))} chars")
    print(f"  - Guidance: {len(results.get('guidance', ''))} chars")
    
    # Verify context slicing worked (check timings)
    print("\n3. Verifying agent execution...")
    timings = results.get('agent_timings', {})
    expected_agents = ['search', 'summarizer', 'synthesizer', 'gap_finder', 
                       'idea_generator', 'technique', 'guidance']
    
    for agent_name in expected_agents:
        if agent_name in timings:
            print(f"  ✓ {agent_name}: {timings[agent_name]:.2f}s")
        else:
            print(f"  ✗ {agent_name}: MISSING")
            return False
    
    # Run 3-way evaluation
    print("\n4. Running 3-way evaluation...")
    evaluator = create_evaluator(model="gpt-3.5-turbo")
    
    evaluation = evaluator.run_three_way_comparison(
        query=query,
        papers=results['papers'],
        multi_agent_results=results,
        rag_enabled=False
    )
    
    if evaluation.get('error'):
        print(f"✗ Evaluation failed: {evaluation['error']}")
        return False
    
    print("✓ Evaluation completed")
    print(f"  Winner: {evaluation.get('winner')}")
    
    # Verify 3-way scores exist
    scores = evaluation.get('scores', {})
    if 'fair_baseline' in scores and 'multi_agent' in scores:
        print(f"  ✓ Fair baseline score: {sum(scores['fair_baseline'].values())}/15")
        print(f"  ✓ Multi-agent score: {sum(scores['multi_agent'].values())}/15")
    else:
        print("  ✗ Scores missing")
        return False
    
    # Verify evaluation saved
    if os.path.exists('evaluation'):
        eval_files = [f for f in os.listdir('evaluation') if f.startswith('run_')]
        print(f"\n  ✓ Evaluation saved: {len(eval_files)} file(s) in evaluation/")
    
    print("\n" + "=" * 80)
    print("INTEGRATION TEST: PASSED ✓")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("✗ OPENAI_API_KEY not found in .env")
        print("Please add your API key to .env file")
        exit(1)
    
    # Run test
    success = test_query_mode()
    
    exit(0 if success else 1)
