/**
 * ============================================================================
 * FRONTEND SHOWCASE: AGENTICOPS SANDBOX & LIVE BENCHMARK COMPONENT
 * ============================================================================
 * What to show in an interview:
 * 1. Demonstrates the live demo / benchmark tab in the frontend.
 * 2. Uses asynchronous non-blocking job polling:
 *    - POSTs to /simulate_comparison to dispatch background task
 *    - Polls /executions/{id} every 2000ms until status is 'completed'
 * 3. Renders parallel telemetry comparison (CoT vs Multi-Agent latency & scores)
 * 4. Built with React 19 hooks (useState, useEffect) and Cyber/Glassmorphic CSS tokens.
 *
 * ORIGINAL SOURCE FILE:
 *   - frontend/src/components/SandboxTab.tsx
 * ============================================================================
 */

"use client";
import { useState, useEffect } from 'react';
import { apiUrl } from '@/lib/api';

export default function SandboxTabShowcase() {
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState<'idle' | 'running' | 'completed' | 'failed'>('idle');
  const [jobId, setJobId] = useState('');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  // 1. INITIATE BENCHMARK RUN VIA FASTAPI BACKGROUND TASK
  const handleSimulate = async () => {
    if (!query) return;
    setStatus('running');
    setResult(null);
    setError('');

    try {
      const res = await fetch(apiUrl('/simulate_comparison'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      const data = await res.json();
      if (data.execution_id) {
        setJobId(data.execution_id); // Receive execution token in <15ms
      } else {
        setStatus('failed');
        setError('Failed to start benchmarking.');
      }
    } catch (e: any) {
      setStatus('failed');
      setError(e.message);
    }
  };

  // 2. ASYNCHRONOUS POLLING LOOP (Decouples client from long LLM execution)
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (status === 'running' && jobId) {
      interval = setInterval(async () => {
        try {
          const res = await fetch(apiUrl(`/executions/${jobId}`));
          const data = await res.json();
          if (data.status === 'completed') {
            setStatus('completed');
            setResult(data.result);
            clearInterval(interval);
          } else if (data.status === 'failed') {
            setStatus('failed');
            setError(data.error);
            clearInterval(interval);
          }
        } catch (e) {
          console.error("Polling error:", e);
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [status, jobId]);

  return (
    <div className="sandbox-container">
      <h2>AgenticOps <span>Sandbox</span></h2>
      <p>Live telemetry benchmarking: Standard CoT Baseline vs. ReAssist Multi-Agent Pipeline.</p>
      
      {/* Search Input & Dispatch */}
      <input 
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="Enter research query to benchmark..."
      />
      <button onClick={handleSimulate} disabled={status === 'running'}>
        {status === 'running' ? 'EXECUTING PARALLEL PIPELINES...' : 'INITIATE BENCHMARK'}
      </button>

      {/* Results View: Shows Coverage, Specificity, Actionability & Latency */}
      {status === 'completed' && result && (
        <div className="benchmark-results">
          <div className="score-card">
            <h4>Multi-Agent Score: {result.multi_agent_scores?.avg_score}</h4>
            <p>Coverage: {result.multi_agent_scores?.coverage_score} / 10</p>
            <p>Specificity: {result.multi_agent_scores?.specificity_score} / 10</p>
          </div>
          <div className="score-card">
            <h4>CoT Baseline Score: {result.cot_baseline_scores?.avg_score}</h4>
            <p>Latency: {result.cot_latency_seconds}s</p>
          </div>
        </div>
      )}
    </div>
  );
}

