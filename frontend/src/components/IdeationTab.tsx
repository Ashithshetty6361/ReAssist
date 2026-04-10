"use client";
import { useState } from 'react';

export default function IdeationTab({ onSelectTopic }: { onSelectTopic: (topic: string) => void }) {
  const [field, setField] = useState('');
  const [loading, setLoading] = useState(false);
  const [topics, setTopics] = useState<string[]>([]);
  
  const handleIdeate = async () => {
    if (!field) return;
    setLoading(true);
    
    // DEMO MODE: Instantly generate dummy topics
    setTimeout(() => {
      setTopics([
        "Agentic RAG Cost Optimization - Evaluating dynamic token-routing latency against traditional standalone Vector DBs.",
        "Generative Pipeline Security - Sandboxing multi-agent architectures to prevent localized hallucination loops.",
        "Quantum-Inspired NLP Synthesis - Using multidimensional tensor frameworks for cross-referencing literature gaps."
      ]);
      setLoading(false);
    }, 1500);
  };

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '800px', margin: '0 auto', width: '100%', padding: '2rem 0' }}>
      <div style={{ textAlign: 'center' }}>
         <h2 style={{ fontSize: '3rem', marginBottom: '1rem', fontWeight: 800, letterSpacing: '-0.02em', background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Research Ideation
         </h2>
         <p style={{ fontSize: '1.1rem', maxWidth: '600px', margin: '0 auto', color: 'var(--text-secondary)' }}>
            Stuck on what to research? Enter a broad scientific field or industry and our generative AI will suggest highly niche, novel topics for you.
         </p>
      </div>

      <div className="glass-panel" style={{ padding: '2rem', background: 'var(--bg-glass-heavy)' }}>
         <div style={{ display: 'flex', gap: '1rem' }}>
           <input 
             value={field}
             onChange={e => setField(e.target.value)}
             placeholder="e.g. Artificial Intelligence in Medicine, Quantum Computing..." 
             style={{ padding: '1rem', fontSize: '1.1rem', background: 'rgba(15,23,42,0.8)' }}
             onKeyDown={e => e.key === 'Enter' && handleIdeate()}
           />
           <button onClick={handleIdeate} disabled={loading} className="btn-primary" style={{ padding: '0 2rem' }}>
             {loading ? 'Ideating...' : 'Generate'}
           </button>
         </div>
      </div>

      {loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
           {[1,2,3].map(i => <div key={i} className="skeleton" style={{ height: '120px' }}></div>)}
        </div>
      )}

      {topics.length > 0 && (
         <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
           <h3 style={{ color: 'var(--text-secondary)', fontSize: '1rem', fontWeight: 500, letterSpacing: '0.05em', textTransform: 'uppercase', marginTop: '1rem' }}>Generated Concepts</h3>
           {topics.map((topic, i) => {
              const parts = topic.split(' - ');
              const title = parts[0] || topic;
              const desc = parts[1] || '';
              return (
                <div 
                  key={i} 
                  onClick={() => onSelectTopic(title)}
                  className="glass-panel" 
                  style={{ padding: '1.5rem', cursor: 'pointer', transition: 'all 0.3s ease', borderLeft: '4px solid var(--accent-primary)', position: 'relative', overflow: 'hidden' }}
                  onMouseOver={e => {
                    e.currentTarget.style.transform = 'translateY(-5px)';
                    e.currentTarget.style.borderColor = 'var(--success)';
                  }}
                  onMouseOut={e => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.borderColor = 'var(--accent-primary)';
                  }}
                >
                   <div style={{ fontSize: '1.25rem', fontWeight: 600, color: 'white', marginBottom: '0.5rem' }}>{title}</div>
                   <div style={{ color: 'var(--text-secondary)', lineHeight: 1.5 }}>{desc}</div>
                   <div style={{ marginTop: '1.5rem', color: 'var(--accent-primary)', fontSize: '0.9rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      Send to Discovery Pipeline <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
                   </div>
                </div>
              );
           })}
         </div>
      )}
    </div>
  );
}
