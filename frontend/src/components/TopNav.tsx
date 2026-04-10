"use client";
import { useState } from 'react';

const FLOW_NODES = [
  { no: '01', title: 'User Query / PDF Upload', desc: 'Research topic or document enters the system via the Claude-style workspace.', color: 'var(--success)', icon: '📝' },
  { no: '02', title: 'AgenticOps Router', desc: 'Classifies prompt complexity and selects optimal pipeline (CoT vs Multi-Agent). Uses cost-quality curves to minimize spend.', color: 'var(--accent-primary)', icon: '🧠' },
  { no: '03', title: 'Search Agent', desc: 'Queries arXiv + Semantic Scholar APIs. Returns {papers, count, success}. Supports max_papers config.', color: 'var(--success)', icon: '🔍' },
  { no: '04', title: 'Summarization Agent', desc: 'Chunks papers via tiktoken (2000 tokens/chunk), runs parallel summarization with ThreadPoolExecutor. Returns per-paper summaries.', color: '#06b6d4', icon: '📄' },
  { no: '05', title: 'Synthesis Agent', desc: 'Cross-references all summaries. Outputs: Common Themes, Methods, Key Findings, Contradictions, Evolution of Ideas.', color: '#8b5cf6', icon: '🧬' },
  { no: '06', title: 'Gap Finder Agent', desc: 'Identifies 6 categories: Unanswered Questions, Methodological Limits, Missing Datasets, Unexplored Combos, Practical Apps, Theory.', color: '#f59e0b', icon: '🔬' },
  { no: '07', title: 'Idea Generator Agent', desc: 'Generates 5 novel hypotheses, each with Problem → Approach → Expected Impact → Novelty. Temp=0.7 for creativity.', color: 'var(--accent-primary)', icon: '💡' },
  { no: '08', title: 'Technique Agent', desc: 'Suggests 3-5 alternative algorithms NOT used in existing papers. Focuses strictly on methods, not timelines.', color: 'var(--danger)', icon: '⚙️' },
  { no: '09', title: 'Implementation Guidance', desc: 'Delivers phased execution plan (Environment → Pipeline → Benchmarking → Deployment) with week-by-week steps.', color: 'var(--danger)', icon: '📋' },
];

export default function TopNav() {
  const [showAbout, setShowAbout] = useState(false);

  return (
    <>
      <button 
        onClick={() => setShowAbout(true)}
        title="View Architecture Flow"
        style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', width: '32px', height: '32px', borderRadius: '50%', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'all 0.2s' }}
        onMouseOver={(e) => e.currentTarget.style.background = 'rgba(59,130,246,0.15)'}
        onMouseOut={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
      </button>

      {showAbout && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(3,7,18,0.85)', backdropFilter: 'blur(12px)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem' }}
             onClick={(e) => { if (e.target === e.currentTarget) setShowAbout(false); }}>
          <div className="glass-panel fade-in" style={{ maxWidth: '750px', width: '100%', maxHeight: '90vh', overflowY: 'auto', padding: '2.5rem', position: 'relative' }}>
            <button onClick={() => setShowAbout(false)} style={{ position: 'absolute', top: '1.5rem', right: '1.5rem', background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '1.5rem' }}>✕</button>
            
            <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem', background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Multi-Agent Pipeline Architecture</h2>
            <p style={{ fontSize: '1rem', marginBottom: '2rem', color: 'var(--text-secondary)' }}>
              ReAssist runs a cascading 9-node pipeline. Each agent receives only the context it needs (context isolation), preventing hallucination drift.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
              {FLOW_NODES.map((node, i) => (
                <div key={node.no}>
                  <div className="arch-node" style={{ animationDelay: `${i * 0.12}s` }}>
                    <div className="arch-node-number" style={{ background: `${node.color}15`, color: node.color, border: `2px solid ${node.color}`, boxShadow: `0 0 12px ${node.color}30` }}>
                      {node.no}
                    </div>
                    <span style={{ fontSize: '1.3rem' }}>{node.icon}</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 700, color: 'white', marginBottom: '0.2rem' }}>{node.title}</div>
                      <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{node.desc}</div>
                    </div>
                  </div>
                  {i < FLOW_NODES.length - 1 && (
                    <div className="arch-connector" style={{ animationDelay: `${i * 0.12 + 0.06}s` }}>
                      <svg width="16" height="20" viewBox="0 0 16 20"><line x1="8" y1="0" x2="8" y2="14" strokeWidth="2"/><polyline points="4 10 8 16 12 10" fill="none" strokeWidth="2"/></svg>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Data flow summary */}
            <div style={{ marginTop: '2rem', padding: '1.5rem', background: 'rgba(59,130,246,0.05)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
              <h4 style={{ color: 'white', marginBottom: '0.75rem', fontSize: '1rem' }}>Data Flow Summary</h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', fontSize: '0.85rem' }}>
                {['Query', '→', 'Papers[]', '→', 'Summaries[]', '→', 'Synthesis', '→', 'Gaps', '→', 'Ideas', '→', 'Techniques', '→', 'Guidance'].map((item, i) => (
                  <span key={i} style={{ color: item === '→' ? 'var(--accent-primary)' : 'white', fontWeight: item === '→' ? 400 : 600, padding: item === '→' ? '0' : '0.25rem 0.5rem', background: item === '→' ? 'transparent' : 'rgba(255,255,255,0.05)', borderRadius: '6px' }}>
                    {item}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
