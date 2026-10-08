"use client";
import { useState, useEffect } from 'react';
import { apiUrl } from '@/lib/api';

export default function SandboxTab() {
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState<'idle'|'running'|'completed'|'failed'>('idle');
  const [jobId, setJobId] = useState('');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

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
        setJobId(data.execution_id);
      } else {
        setStatus('failed');
        setError('Failed to start benchmarking.');
      }
    } catch (e: any) {
      setStatus('failed');
      setError(e.message);
    }
  };

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
          console.error(e);
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [status, jobId]);

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '3rem', maxWidth: '1000px', margin: '0 auto', width: '100%', padding: '2rem 0' }}>
       <div style={{ textAlign: 'center' }}>
         <h2 style={{ fontSize: '3.5rem', fontWeight: 800, color: 'white', letterSpacing: '-0.03em', marginBottom: '1rem', textTransform: 'uppercase' }}>
           AgenticOps <span style={{ color: 'var(--accent-primary)', textShadow: '0 0 20px rgba(0, 240, 255, 0.4)' }}>Sandbox</span>
         </h2>
         <p style={{ fontSize: '1.1rem', color: 'var(--text-secondary)', maxWidth: '650px', margin: '0 auto', fontFamily: 'JetBrains Mono, monospace' }}>
           &gt; Live telemetry benchmarking: Standard CoT Baseline vs. ReAssist Multi-Agent Pipeline. Execute query to simulate load.
         </p>
       </div>

       <div className="glass-panel" style={{ padding: '2.5rem', background: 'var(--bg-glass-heavy)' }}>
         <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
           <input 
             value={query}
             onChange={e => setQuery(e.target.value)}
             placeholder="&gt; Target query for stress test..." 
             style={{ flex: 1, padding: '1.25rem', fontSize: '1.1rem', background: 'rgba(0,0,0,0.6)', border: '1px solid var(--border-color)', borderRadius: '8px', color: 'var(--accent-primary)', fontFamily: 'JetBrains Mono, monospace' }}
             onKeyDown={e => e.key === 'Enter' && handleSimulate()}
           />
           <button onClick={handleSimulate} disabled={status === 'running' || !query} className="btn-primary" style={{ padding: '0 2.5rem', height: '62px' }}>
             {status === 'running' ? 'SIMULATING...' : 'INITIATE BENCHMARK'}
           </button>
         </div>
       </div>

       {status === 'running' && (
         <div style={{ marginTop: '2rem', textAlign: 'center' }}>
           <div className="skeleton" style={{ height: '4px', width: '100%', marginBottom: '2rem', background: 'linear-gradient(90deg, transparent, var(--accent-primary), transparent)' }}></div>
           <p style={{ color: 'var(--accent-primary)', fontWeight: 700, fontFamily: 'JetBrains Mono, monospace', animation: 'pulse 1.5s infinite' }}>&gt; EXECUTING PARALLEL PIPELINES...</p>
         </div>
       )}

       {status === 'failed' && (
         <div className="glass-panel" style={{ padding: '2rem', borderLeft: '4px solid var(--danger)', color: 'var(--danger)', background: 'rgba(239, 68, 68, 0.05)' }}>
            <span style={{ fontFamily: 'JetBrains Mono, monospace', fontWeight: 600 }}>&gt; SYS_ERROR:</span> {error}
         </div>
       )}

       {status === 'completed' && result && (
         <div className="fade-in glass-panel" style={{ padding: '3rem', display: 'flex', flexDirection: 'column', gap: '2.5rem', border: '1px solid rgba(0, 240, 255, 0.15)' }}>
           <h3 style={{ fontSize: '1.5rem', color: 'white', textAlign: 'center', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
             <span style={{ color: 'var(--accent-primary)' }}>◈</span> Benchmark Telemetry <span style={{ color: 'var(--accent-primary)' }}>◈</span>
           </h3>
           
           <div style={{ display: 'flex', justifyContent: 'center', gap: '4rem', flexWrap: 'wrap' }}>
             <div style={{ textAlign: 'center', flex: 1, minWidth: '200px', background: 'rgba(0,0,0,0.4)', padding: '2rem', borderRadius: '12px', border: '1px solid rgba(0, 255, 136, 0.2)' }}>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem', fontFamily: 'JetBrains Mono, monospace', letterSpacing: '0.05em' }}>&gt; MULTI-AGENT SCORE</div>
                <div style={{ fontSize: '4.5rem', fontWeight: 800, color: 'var(--success)', textShadow: '0 0 20px rgba(0, 255, 136, 0.4)' }}>
                  {result.cot_latency_seconds ? `${(result.multi_agent_scores?.avg_score || 0).toFixed(1)}` : '0'} 
                </div>
             </div>
             
             <div style={{ textAlign: 'center', flex: 1, minWidth: '200px', background: 'rgba(0,0,0,0.4)', padding: '2rem', borderRadius: '12px', border: '1px solid rgba(245, 158, 11, 0.2)' }}>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem', fontFamily: 'JetBrains Mono, monospace', letterSpacing: '0.05em' }}>&gt; BASELINE CoT SCORE</div>
                <div style={{ fontSize: '4.5rem', fontWeight: 800, color: 'var(--warning)', textShadow: '0 0 20px rgba(245, 158, 11, 0.4)' }}>
                   {result.cot_baseline_scores?.avg_score?.toFixed(1) || '0'}
                </div>
             </div>
           </div>

           <div style={{ background: 'rgba(0,0,0,0.5)', padding: '2.5rem', borderRadius: '12px', border: '1px solid var(--border-color)', position: 'relative', overflow: 'hidden' }}>
              <div style={{ position: 'absolute', top: 0, left: 0, width: '4px', height: '100%', background: 'var(--accent-gradient)' }}></div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
                 <div style={{ fontSize: '1.2rem', color: 'white', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 700 }}>System Recommendation</div>
                 <div style={{ padding: '0.4rem 1.5rem', background: 'rgba(0, 240, 255, 0.1)', border: '1px solid var(--accent-primary)', borderRadius: '4px', fontSize: '0.9rem', fontWeight: 700, color: 'var(--accent-primary)', fontFamily: 'JetBrains Mono, monospace' }}>
                    {result.winner?.toUpperCase() || 'UNKNOWN'} OPTIMAL
                 </div>
              </div>
              <p style={{ fontSize: '1.1rem', color: 'var(--text-secondary)', lineHeight: 1.6, fontFamily: 'JetBrains Mono, monospace' }}>
                 &gt; {result.recommendation}
              </p>
           </div>
         </div>
       )}
    </div>
  );
}
