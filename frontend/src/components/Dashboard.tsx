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
    <div style={{ padding: '1rem' }}>
      <header style={{ marginBottom: '2.5rem' }}>
        <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem', background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', display: 'inline-block' }}>
          Research Intelligence
        </h2>
        <p>Enter a research topic or upload a PDF to extract actionable insights via multi-agent pipeline.</p>
      </header>

      <form onSubmit={handleAnalyze} className="glass-panel" style={{ padding: '2rem', marginBottom: '2rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        <div style={{ flex: '1 1 300px' }}>
          <input 
            type="text" 
            placeholder="e.g. Attention mechanisms in transformers..." 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <button type="submit" className="btn-primary" disabled={isAnalyzing}>
          {isAnalyzing ? (
            <><span className="spinner" style={{ animation: 'spin 1s linear infinite' }}>⏳</span> Analyzing...</>
          ) : (
            <>🚀 Search & Analyze</>
          )}
        </button>
      </form>

      {error && (
        <div className="glass-panel" style={{ padding: '1.5rem', borderLeft: '4px solid var(--danger)', backgroundColor: 'rgba(239, 68, 68, 0.05)' }}>
          <h3 style={{ color: 'var(--danger)', margin: '0 0 0.5rem 0' }}>Error</h3>
          <p style={{ margin: 0 }}>{error}</p>
        </div>
      )}

      {isAnalyzing && (
        <div className="glass-panel" style={{ padding: '2rem' }}>
          <h3 style={{ marginBottom: '1.5rem' }}>Processing Pipeline...</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="skeleton" style={{ height: '60px', width: '100%' }}></div>
            <div className="skeleton" style={{ height: '100px', width: '100%' }}></div>
            <div className="skeleton" style={{ height: '60px', width: '80%' }}></div>
          </div>
        </div>
      )}

      {results && results.result && (
        <div className="glass-panel" style={{ padding: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
            <h3 style={{ fontSize: '1.5rem', margin: 0 }}>Analysis Results</h3>
            {results.routing_decision && (
              <span style={{ background: 'var(--bg-secondary)', padding: '0.5rem 1rem', borderRadius: '20px', fontSize: '0.85rem', border: '1px solid var(--border-color)' }}>
                Router Path: <strong style={{ color: 'var(--success)' }}>{results.routing_decision.decision}</strong>
              </span>
            )}
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
            <div style={{ background: 'var(--bg-secondary)', padding: '1.5rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
              <h4 style={{ color: 'var(--accent-primary)', marginBottom: '1rem' }}>📚 Papers Analyzed</h4>
              {results.result.papers?.map((p: any, i: number) => (
                <div key={i} style={{ marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border-color)' }}>
                  <div style={{ fontWeight: 600 }}>{p.title}</div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{p.year} • {p.authors?.slice(0,3).join(', ')}</div>
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div style={{ background: 'var(--bg-secondary)', padding: '1.5rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                <h4 style={{ color: 'var(--accent-primary)', marginBottom: '1rem' }}>📊 Synthesis</h4>
                <div style={{ whiteSpace: 'pre-wrap', fontSize: '0.9rem', color: 'var(--text-secondary)', maxHeight: '200px', overflowY: 'auto' }} className="custom-scroll">
                  {results.result.synthesis?.synthesis_text || 'No synthesis generated.'}
                </div>
              </div>
              
              <div style={{ background: 'var(--bg-secondary)', padding: '1.5rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                <h4 style={{ color: 'var(--accent-primary)', marginBottom: '1rem' }}>💡 Novel Ideas</h4>
                <div style={{ whiteSpace: 'pre-wrap', fontSize: '0.9rem', color: 'var(--text-secondary)', maxHeight: '200px', overflowY: 'auto' }} className="custom-scroll">
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
