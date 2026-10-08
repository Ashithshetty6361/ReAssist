"use client";
import { useState } from 'react';

const FLOW_NODES = [
  { no: '01', title: 'User Query / PDF Upload', desc: 'Research topic or document enters the system via the tech workspace.', color: 'var(--success)', icon: '◈' },
  { no: '02', title: 'AgenticOps Router', desc: 'Classifies prompt complexity and selects optimal pipeline (CoT vs Multi-Agent). Uses cost-quality curves to minimize spend.', color: 'var(--accent-primary)', icon: '⚙️' },
  { no: '03', title: 'Search Agent', desc: 'Queries arXiv + Semantic Scholar APIs. Returns {papers, count, success}. Supports max_papers config.', color: 'var(--success)', icon: '🔍' },
  { no: '04', title: 'Summarization Agent', desc: 'Chunks papers via tiktoken (2000 tokens/chunk), runs parallel summarization. Returns per-paper summaries.', color: 'var(--accent-primary)', icon: '📄' },
  { no: '05', title: 'Synthesis Agent', desc: 'Cross-references all summaries. Outputs: Common Themes, Methods, Key Findings, Contradictions, Evolution of Ideas.', color: 'var(--accent-purple)', icon: '🧬' },
  { no: '06', title: 'Gap Finder Agent', desc: 'Identifies 6 categories: Unanswered Questions, Methodological Limits, Missing Datasets, Unexplored Combos.', color: '#ffb800', icon: '🔬' },
  { no: '07', title: 'Idea Generator Agent', desc: 'Generates 5 novel hypotheses, each with Problem → Approach → Expected Impact → Novelty.', color: 'var(--accent-primary)', icon: '💡' },
  { no: '08', title: 'Technique Agent', desc: 'Suggests 3-5 alternative algorithms NOT used in existing papers. Focuses strictly on methods.', color: 'var(--danger)', icon: '⚡' },
  { no: '09', title: 'Implementation Guidance', desc: 'Delivers phased execution plan (Environment → Pipeline → Benchmarking) with week-by-week steps.', color: 'var(--danger)', icon: '📋' },
];

export default function TopNav() {
  const [showAbout, setShowAbout] = useState(false);

  return (
    <>
      <button 
        onClick={() => setShowAbout(true)}
        title="View Architecture Flow"
        style={{ background: 'rgba(0, 240, 255, 0.05)', border: '1px solid rgba(0, 240, 255, 0.2)', color: 'var(--accent-primary)', width: '36px', height: '36px', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'all 0.3s ease', boxShadow: '0 0 10px rgba(0, 240, 255, 0.1)' }}
        onMouseOver={(e) => {
          e.currentTarget.style.background = 'rgba(0, 240, 255, 0.15)';
          e.currentTarget.style.boxShadow = '0 0 15px rgba(0, 240, 255, 0.4)';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.background = 'rgba(0, 240, 255, 0.05)';
          e.currentTarget.style.boxShadow = '0 0 10px rgba(0, 240, 255, 0.1)';
        }}
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
      </button>

      {showAbout && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(5,5,8,0.9)', backdropFilter: 'blur(16px)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem' }}
             onClick={(e) => { if (e.target === e.currentTarget) setShowAbout(false); }}>
          <div className="glass-panel fade-in" style={{ maxWidth: '800px', width: '100%', maxHeight: '90vh', overflowY: 'auto', padding: '3rem', position: 'relative', border: '1px solid var(--accent-primary)', boxShadow: '0 0 30px rgba(0, 240, 255, 0.1)' }}>
            <button onClick={() => setShowAbout(false)} style={{ position: 'absolute', top: '1.5rem', right: '1.5rem', background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '1.5rem', transition: 'color 0.2s' }} onMouseOver={(e)=>e.currentTarget.style.color='var(--accent-primary)'} onMouseOut={(e)=>e.currentTarget.style.color='var(--text-secondary)'}>✕</button>
            
            <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem', color: 'white', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              System <span style={{ color: 'var(--accent-primary)' }}>Architecture</span>
            </h2>
            <p style={{ fontSize: '0.95rem', marginBottom: '2.5rem', color: 'var(--text-secondary)', fontFamily: 'JetBrains Mono, monospace' }}>
              &gt; ReAssist runs a cascading 9-node pipeline. Context isolation prevents hallucination drift.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
              {FLOW_NODES.map((node, i) => (
                <div key={node.no}>
                  <div className="arch-node" style={{ animationDelay: `${i * 0.12}s`, background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '8px' }}>
                    <div className="arch-node-number" style={{ background: `${node.color}15`, color: node.color, border: `1px solid ${node.color}`, boxShadow: `0 0 15px ${node.color}30`, fontFamily: 'JetBrains Mono, monospace' }}>
                      {node.no}
                    </div>
                    <span style={{ fontSize: '1.3rem', filter: `drop-shadow(0 0 5px ${node.color})` }}>{node.icon}</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600, color: 'white', marginBottom: '0.3rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontSize: '0.9rem' }}>{node.title}</div>
                      <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{node.desc}</div>
                    </div>
                  </div>
                  {i < FLOW_NODES.length - 1 && (
                    <div className="arch-connector" style={{ animationDelay: `${i * 0.12 + 0.06}s` }}>
                      <svg width="16" height="24" viewBox="0 0 16 24"><line x1="8" y1="0" x2="8" y2="18" strokeWidth="2" strokeDasharray="4 4" /><polyline points="4 14 8 20 12 14" fill="none" strokeWidth="2"/></svg>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Data flow summary */}
            <div style={{ marginTop: '3rem', padding: '2rem', background: 'rgba(0, 240, 255, 0.02)', borderRadius: '8px', border: '1px solid rgba(0, 240, 255, 0.1)' }}>
              <h4 style={{ color: 'var(--accent-primary)', marginBottom: '1rem', fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '0.1em', fontFamily: 'JetBrains Mono, monospace' }}>&gt; Data Flow Summary</h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', fontSize: '0.85rem', fontFamily: 'JetBrains Mono, monospace' }}>
                {['Query', '→', 'Papers[]', '→', 'Summaries[]', '→', 'Synthesis', '→', 'Gaps', '→', 'Ideas', '→', 'Techniques', '→', 'Guidance'].map((item, i) => (
                  <span key={i} style={{ color: item === '→' ? 'var(--accent-primary)' : 'white', fontWeight: item === '→' ? 400 : 500, padding: item === '→' ? '0' : '0.4rem 0.6rem', background: item === '→' ? 'transparent' : 'rgba(255,255,255,0.05)', borderRadius: '4px' }}>
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
