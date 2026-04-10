"use client";
import { useState, useEffect } from 'react';

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
      const res = await fetch('http://localhost:8000/simulate_comparison', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, model: 'gpt-3.5-turbo' })
      });
      const data = await res.json();
      if (data.job_id) {
        setJobId(data.job_id);
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
          const res = await fetch(`http://localhost:8000/jobs/${jobId}`);
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
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '1000px', margin: '0 auto', width: '100%', padding: '2rem 0' }}>
       <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
         <h2 style={{ fontSize: '3rem', fontWeight: 800, color: 'white', letterSpacing: '-0.02em', marginBottom: '1rem' }}>AgenticOps <span style={{ color: 'var(--accent-primary)' }}>Sandbox</span></h2>
         <p style={{ fontSize: '1.1rem', color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto' }}>Test the live impact of the AgenticOps router. Enter a query and we will race the baseline CoT model against our 7-Agent Pipeline.</p>
       </div>

       <div className="glass-panel" style={{ padding: '2rem', background: 'var(--bg-glass-heavy)' }}>
         <div style={{ display: 'flex', gap: '1rem' }}>
           <input 
             value={query}
             onChange={e => setQuery(e.target.value)}
             placeholder="Enter a test query to benchmark..." 
             style={{ padding: '1rem', fontSize: '1.1rem', background: 'rgba(15,23,42,0.8)' }}
             onKeyDown={e => e.key === 'Enter' && handleSimulate()}
           />
           <button onClick={handleSimulate} disabled={status === 'running' || !query} className="btn-primary" style={{ padding: '0 2rem' }}>
             {status === 'running' ? 'Simulating...' : 'Run Benchmark'}
           </button>
         </div>
       </div>

       {status === 'running' && (
         <div style={{ marginTop: '2rem', textAlign: 'center' }}>
           <div className="skeleton" style={{ height: '8px', width: '100%', marginBottom: '1rem', borderRadius: '100px' }}></div>
           <p style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>Executing parallel pipelines and calculating metrics...</p>
         </div>
       )}

       {status === 'failed' && (
         <div className="glass-panel" style={{ padding: '1.5rem', borderLeft: '4px solid var(--danger)', color: 'var(--danger)' }}>
            <strong>Benchmark Error:</strong> {error}
         </div>
       )}

       {status === 'completed' && result && (
         <div className="fade-in glass-panel" style={{ padding: '2.5rem', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
           <h3 style={{ fontSize: '1.5rem', color: 'white', textAlign: 'center' }}>Benchmark Report</h3>
           
           <div style={{ display: 'flex', justifyContent: 'center', gap: '4rem' }}>
             <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '4rem', fontWeight: 800, color: 'var(--success)' }}>
                  {result.cot_latency_seconds ? `${(result.multi_agent_scores?.avg_score || 0).toFixed(1)}` : '0'} 
                </div>
                <div style={{ color: 'var(--text-secondary)' }}>Multi-Agent Quality</div>
             </div>
             
             <div style={{ width: '1px', background: 'var(--border-color)' }}></div>
             
             <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '4rem', fontWeight: 800, color: 'var(--warning)' }}>
                   {result.cot_baseline_scores?.avg_score?.toFixed(1) || '0'}
                </div>
                <div style={{ color: 'var(--text-secondary)' }}>CoT Quality</div>
             </div>
           </div>

           <div style={{ background: 'rgba(0,0,0,0.3)', padding: '2rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                 <div style={{ fontSize: '1.1rem', color: 'white' }}>Final Recommendation</div>
                 <div style={{ padding: '4px 12px', background: 'var(--accent-gradient)', borderRadius: '100px', fontSize: '0.8rem', fontWeight: 'bold', color: 'white' }}>
                    {result.winner?.toUpperCase() || 'UNKNOWN'} WINS
                 </div>
              </div>
              <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                 {result.recommendation}
              </p>
           </div>
         </div>
       )}
    </div>
  );
}
