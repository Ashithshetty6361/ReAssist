"use client";
import React, { useState } from 'react';

export default function Dashboard() {
  const [query, setQuery] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query) return;

    setIsAnalyzing(true);
    setResults(null);
    setError(null);

    try {
      // Step 1: Request analysis job
      const res = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, use_router: true })
      });
      
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to start analysis');
      
      const jobId = data.job_id;
      
      // Step 2: Poll for results
      let completed = false;
      while (!completed) {
        await new Promise(resolve => setTimeout(resolve, 2000)); // poll every 2s
        const pollRes = await fetch(`http://localhost:8000/jobs/${jobId}`);
        const pollData = await pollRes.json();
        
        if (pollData.status === 'completed') {
          setResults(pollData);
          completed = true;
        } else if (pollData.status === 'failed') {
          throw new Error(pollData.error || 'Analysis failed during execution');
        }
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div style={{ padding: '2rem' }}>
      <header style={{ marginBottom: '3rem' }}>
        <h2 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span style={{ display: 'inline-block', width: '12px', height: '12px', background: 'var(--accent-primary)', borderRadius: '50%', boxShadow: '0 0 10px var(--accent-primary)' }}></span>
          Command Center
        </h2>
        <p style={{ fontFamily: 'JetBrains Mono, monospace', color: 'var(--accent-primary)', opacity: 0.8, fontSize: '0.9rem' }}>
          &gt; initialize_research_protocol(mode="multi_agent")
        </p>
      </header>

      <form onSubmit={handleAnalyze} className="glass-panel" style={{ padding: '2.5rem', marginBottom: '3rem', display: 'flex', gap: '1.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ flex: '1 1 300px', position: 'relative' }}>
          <div style={{ position: 'absolute', top: '50%', transform: 'translateY(-50%)', left: '1rem', color: 'var(--accent-primary)', opacity: 0.8 }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          </div>
          <input 
            type="text" 
            placeholder="Enter research target or upload schematic..." 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{ paddingLeft: '3rem', fontSize: '1.1rem', background: 'rgba(0,0,0,0.6)', border: '1px solid rgba(0, 240, 255, 0.2)' }}
          />
        </div>
        <button type="submit" className="btn-primary" disabled={isAnalyzing} style={{ minWidth: '200px', height: '52px' }}>
          {isAnalyzing ? (
            <><span className="spinner" style={{ animation: 'spin 1s linear infinite', marginRight: '0.5rem' }}>⟳</span> PROCESSING...</>
          ) : (
            <>EXECUTE_QUERY()</>
          )}
        </button>
      </form>

      {error && (
        <div className="glass-panel fade-in" style={{ padding: '1.5rem', borderLeft: '4px solid var(--danger)', backgroundColor: 'rgba(255, 42, 42, 0.05)' }}>
          <h3 style={{ color: 'var(--danger)', margin: '0 0 0.5rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '1.2rem' }}>⚠️</span> CRITICAL ERROR
          </h3>
          <p style={{ margin: 0, fontFamily: 'JetBrains Mono, monospace' }}>{error}</p>
        </div>
      )}

      {isAnalyzing && (
        <div className="glass-panel processing-pulse" style={{ padding: '2.5rem' }}>
          <h3 style={{ marginBottom: '2rem', color: 'var(--accent-primary)', fontFamily: 'JetBrains Mono, monospace', fontSize: '1rem' }}>
            &gt; SYSTEM_ANALYSIS_IN_PROGRESS...
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div className="skeleton" style={{ height: '60px', width: '100%' }}></div>
            <div className="skeleton" style={{ height: '120px', width: '100%' }}></div>
            <div className="skeleton" style={{ height: '60px', width: '80%' }}></div>
          </div>
        </div>
      )}

      {results && results.result && (
        <div className="glass-panel fade-in" style={{ padding: '2.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2.5rem', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '1.5rem' }}>
            <div>
              <h3 style={{ fontSize: '1.75rem', margin: '0 0 0.5rem 0', color: 'white' }}>Data Extracted</h3>
              <div style={{ fontFamily: 'JetBrains Mono, monospace', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Target: {query}</div>
            </div>
            {results.routing_decision && (
              <div style={{ background: 'rgba(0, 240, 255, 0.05)', padding: '0.75rem 1.25rem', borderRadius: '8px', border: '1px solid var(--accent-primary)', boxShadow: '0 0 15px rgba(0, 240, 255, 0.1)' }}>
                <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.25rem' }}>AIOps Route</span>
                <strong style={{ color: 'var(--accent-primary)', fontSize: '1.1rem', letterSpacing: '0.05em' }}>{results.routing_decision.decision}</strong>
              </div>
            )}
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '2rem' }}>
            <div style={{ background: 'rgba(0,0,0,0.4)', padding: '2rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
              <h4 style={{ color: 'var(--text-primary)', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '1.1rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                <span style={{ color: 'var(--accent-purple)' }}>◈</span> Analyzed Datasets
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {results.result.papers?.map((p: any, i: number) => (
                  <div key={i} className="paper-card" style={{ padding: '1.25rem' }}>
                    <div style={{ width: '40px', height: '40px', background: 'rgba(157, 78, 221, 0.1)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-purple)', fontWeight: 'bold' }}>
                      {i + 1}
                    </div>
                    <div>
                      <div style={{ fontWeight: 600, color: 'white', marginBottom: '0.25rem' }}>{p.title}</div>
                      <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontFamily: 'JetBrains Mono, monospace' }}>{p.year} | {p.authors?.slice(0,2).join(', ')}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
              <div style={{ background: 'rgba(0,0,0,0.4)', padding: '2rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <h4 style={{ color: 'var(--text-primary)', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '1.1rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  <span style={{ color: 'var(--accent-primary)' }}>◈</span> Core Synthesis
                </h4>
                <div style={{ whiteSpace: 'pre-wrap', fontSize: '0.95rem', color: 'var(--text-secondary)', maxHeight: '250px', overflowY: 'auto', paddingRight: '1rem' }} className="custom-scroll">
                  {results.result.synthesis?.synthesis_text || 'No synthesis generated.'}
                </div>
              </div>
              
              <div style={{ background: 'rgba(0,0,0,0.4)', padding: '2rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <h4 style={{ color: 'var(--text-primary)', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '1.1rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  <span style={{ color: 'var(--success)' }}>◈</span> Generated Hypotheses
                </h4>
                <div style={{ whiteSpace: 'pre-wrap', fontSize: '0.95rem', color: 'var(--text-secondary)', maxHeight: '250px', overflowY: 'auto', paddingRight: '1rem' }} className="custom-scroll">
                  {results.result.ideas?.ideas_text || 'No ideas generated.'}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
