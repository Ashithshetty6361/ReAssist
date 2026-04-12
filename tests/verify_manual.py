"""
Manual Verification Script
Run this to verify context slicing and baseline fairness
"""

import os
from dotenv import load_dotenv
from root_agent import create_root_agent
from evaluation.evaluator import create_evaluator

load_dotenv()

print("=" * 80)
print("STEP 1: CONTEXT SLICING VERIFICATION")
print("=" * 80)

# Create agent
agent = create_root_agent(model="gpt-3.5-turbo", max_papers=2)

# Run query
print("\nRunning query: 'attention mechanisms'")
print("\nWatch for '→ AgentName receives: [keys]' messages below:")
print("-" * 80)

results = agent.execute_pipeline(query="attention mechanisms")

print("\n" + "=" * 80)
print("STEP 2: VERIFY OUTPUTS")
print("=" * 80)

if results.get('error'):
    print(f"✗ Error: {results['error']}")
else:
    print(f"✓ Papers found: {len(results.get('papers', []))}")
    print(f"✓ Synthesis length: {len(results.get('synthesis', ''))} chars")
    print(f"✓ Gaps length: {len(results.get('gaps', ''))} chars")
    print(f"✓ Ideas length: {len(results.get('ideas', ''))} chars")
    print(f"✓ Techniques length: {len(results.get('techniques', ''))} chars")
    print(f"✓ Guidance length: {len(results.get('guidance', ''))} chars")

print("\n" + "=" * 80)
print("STEP 3: BASELINE FAIRNESS CHECK")
print("=" * 80)

evaluator = create_evaluator(model="gpt-3.5-turbo")

print("\nRunning 3-way evaluation...")
print("Baseline will receive these papers:")
for i, paper in enumerate(results.get('papers', [])[:2], 1):
    title = paper.get('title', 'Untitled')[:60]
    print(f"  {i}. {title}...")

evaluation = evaluator.run_three_way_comparison(
    query="attention mechanisms",
    papers=results['papers'],
    multi_agent_results=results,
    rag_enabled=False
)

if not evaluation.get('error'):
    print("\n✓ Evaluation complete")
    print(f"  Winner: {evaluation.get('winner')}")
    scores = evaluation.get('scores', {})
    print(f"  Fair baseline score: {sum(scores.get('fair_baseline', {}).values())}/15")
    print(f"  Multi-agent score: {sum(scores.get('multi_agent', {}).values())}/15")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
print("\nCheck above output for:")
print("1. Each agent receives ONLY its required_inputs")
print("2. Baseline gets same papers as multi-agent")
print("3. Evaluation produces valid scores")
