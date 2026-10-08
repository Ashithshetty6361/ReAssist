"use client";
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// ─── Architecture Flow Diagram ──────────────────────────────────────────────

const ARCH_NODES = [
  { label: 'Query / Document Input', desc: 'Research topic or PDF enters the workspace', icon: '◈', color: 'var(--success)' },
  { label: 'AgenticOps Router', desc: 'Classifies complexity → selects optimal execution path', icon: '⚙️', color: 'var(--accent-primary)' },
  { label: 'Search Module', desc: 'Queries scholarly APIs for relevant literature', icon: '🔍', color: 'var(--success)' },
  { label: 'Summarization Module', desc: 'Parallel chunking & extraction via tiktoken', icon: '📄', color: 'var(--accent-primary)' },
  { label: 'Synthesis Module', desc: 'Cross-references summaries, identifies consensus & conflict', icon: '🧬', color: 'var(--accent-purple)' },
  { label: 'Gap Analysis Module', desc: 'Identifies missing datasets, untested methods, etc.', icon: '🔬', color: 'var(--warning)' },
  { label: 'Hypothesis Generator', desc: 'Generates novel vectors with problem-approach-impact', icon: '💡', color: 'var(--accent-primary)' },
  { label: 'Techniques Module', desc: 'Suggests alternative algorithms NOT in existing papers', icon: '⚡', color: 'var(--danger)' },
  { label: 'Guidance Module', desc: 'Builds phased execution plan with metrics', icon: '📋', color: 'var(--success)' },
];

function ArchitectureDiagram() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
      {ARCH_NODES.map((node, i) => (
        <div key={i}>
          <div className="arch-node" style={{ animationDelay: `${i * 0.1}s`, background: 'rgba(0,0,0,0.5)' }}>
            <div className="arch-node-number" style={{ background: `${node.color}15`, color: node.color, border: `1px solid ${node.color}50` }}>
              {String(i + 1).padStart(2, '0')}
            </div>
            <span style={{ fontSize: '1.2rem', filter: `drop-shadow(0 0 5px ${node.color})` }}>{node.icon}</span>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700, color: 'white', marginBottom: '0.2rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontSize: '0.9rem' }}>{node.label}</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontFamily: 'JetBrains Mono, monospace' }}>{node.desc}</div>
            </div>
          </div>
          {i < ARCH_NODES.length - 1 && (
            <div className="arch-connector" style={{ animationDelay: `${i * 0.1 + 0.05}s` }}>
              <svg width="16" height="24" viewBox="0 0 16 24"><line x1="8" y1="0" x2="8" y2="18" strokeWidth="2" strokeDasharray="2 2" stroke="var(--border-color)" /><polyline points="4 14 8 20 12 14" fill="none" strokeWidth="2" stroke="var(--border-color)" /></svg>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// ─── Tech Stack ─────────────────────────────────────────────────────────────

const TECH_STACK = [
  { layer: 'Frontend', tech: 'Next.js 14', rationale: 'Server Components for fast artifact rendering', icon: '🌐' },
  { layer: 'Backend', tech: 'FastAPI', rationale: 'Native async, auto-docs, Pydantic validation', icon: '⚡' },
  { layer: 'Agent Framework', tech: 'LangGraph', rationale: 'Stateful, cyclic agent composition', icon: '🔗' },
  { layer: 'Vector DB', tech: 'ChromaDB', rationale: 'Local fast retrieval, easy postgres migration', icon: '🗃️' },
  { layer: 'Persistence', tech: 'PostgreSQL', rationale: 'ACID compliance for trace persistence', icon: '🐘' },
  { layer: 'Auth', tech: 'JWT', rationale: 'Stateless, scalable authentication', icon: '🔐' },
  { layer: 'Telemetry', tech: 'tiktoken', rationale: 'Per-agent token tracking and cost attribution', icon: '📊' },
];

const TECHNIQUE_MD = `#### 1. Experimental Design
- **Hypothesis:** DTRP reduces multi-agent pipeline cost by ≥60% with <5% quality degradation
- **Independent Variable:** Router classification threshold (t ∈ [0.5, 0.9])
- **Dependent Variables:** Total cost (USD), latency (ms), BLEU/ROUGE scores
- **Control:** Standard Chain-of-Thought baseline (GPT-4, single prompt)

#### 2. Dataset Requirements
- **Benchmark Suite:** 500 diverse research queries across 5 domains
- **Ground Truth:** Human-annotated quality scores per synthesis
- **Scale:** Minimum 3 runs per configuration for statistical significance`;

const GUIDANCE_MD = `#### Phase 1: Environment Setup (Week 1)
1. Initialize backend with \\\`pip install fastapi langgraph chromadb openai\\\`
2. Scaffold the Router with a lightweight classifier
3. Create \\\`agents/\\\` directory with modular agent classes

#### Phase 2: Pipeline Construction (Week 2-3)
4. Wire 7-Agent Chain: Search → Summarize → Synthesis → Gap → Idea → Technique → Guidance
5. Add Token Tracking with \\\`tiktoken\\\` per node
6. Connect ChromaDB for RAG document ingestion

#### Phase 3: Benchmarking (Week 4)
7. Build Evaluation Harness in \\\`evaluation/evaluator.py\\\`
8. Run 500-query benchmark, logging cost and quality per run
9. Auto-generate comparison charts`;

// ─── Component ──────────────────────────────────────────────────────────────

export default function ImplementationTab({ resultData, onInlineChat }: { resultData: any, onInlineChat?: (msg: string) => void }) {
  const [inlineMsg, setInlineMsg] = useState('');
  const [showArch, setShowArch] = useState(false);

  if (!resultData) {
    return (
      <div className="fade-in" style={{ textAlign: 'center', padding: '6rem 2rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
         <div style={{ padding: '2rem', background: 'rgba(0, 240, 255, 0.05)', borderRadius: '50%', marginBottom: '2rem', border: '1px solid rgba(0, 240, 255, 0.1)' }}>
           <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" strokeWidth="1.5"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
         </div>
         <h3 style={{ fontSize: '1.5rem', color: 'white', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Awaiting Telemetry</h3>
         <p style={{ maxWidth: '400px', lineHeight: 1.6, fontFamily: 'JetBrains Mono, monospace', fontSize: '0.9rem' }}>&gt; Complete the Discovery pipeline to generate implementation schematics.</p>
      </div>
    );
  }

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem', maxWidth: '1000px', margin: '0 auto', width: '100%', padding: '2rem 0' }}>
       <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
         <h2 style={{ fontSize: '3.5rem', fontWeight: 800, color: 'white', letterSpacing: '-0.03em', marginBottom: '1rem', textTransform: 'uppercase' }}>
           System <span style={{ color: 'var(--danger)', textShadow: '0 0 20px rgba(239, 68, 68, 0.4)' }}>Implementation</span>
         </h2>
         <p style={{ fontSize: '1.1rem', color: 'var(--text-secondary)', fontFamily: 'JetBrains Mono, monospace' }}>&gt; Your complete execution blueprint, compiled by the Guidance module.</p>
       </div>

       {/* Architecture Diagram Toggle */}
       <div className="glass-panel" style={{ padding: '2rem', overflow: 'hidden' }}>
         <div onClick={() => setShowArch(!showArch)} style={{ display: 'flex', alignItems: 'center', gap: '1rem', cursor: 'pointer' }}>
           <span style={{ fontSize: '1.5rem', filter: 'drop-shadow(0 0 5px var(--accent-primary))' }}>🏗️</span>
           <h4 style={{ color: 'white', fontSize: '1.2rem', fontWeight: 700, flex: 1, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Pipeline Architecture Flow</h4>
           <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" strokeWidth="2" style={{ transition: 'transform 0.3s cubic-bezier(0.16, 1, 0.3, 1)', transform: showArch ? 'rotate(180deg)' : 'rotate(0)' }}>
             <polyline points="6 9 12 15 18 9"/>
           </svg>
         </div>
         {showArch && (
           <div className="fade-in" style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border-color)' }}>
             <ArchitectureDiagram />
           </div>
         )}
       </div>

       {/* Techniques Agent */}
       <div className="glass-panel" style={{ padding: '2.5rem', borderLeft: '4px solid var(--warning)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
            <span style={{ fontSize: '1.5rem', filter: 'drop-shadow(0 0 5px var(--warning))' }}>⚡</span>
            <h3 style={{ fontSize: '1.2rem', color: 'var(--warning)', fontWeight: 700, flex: 1, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Techniques Module</h3>
            <div style={{ background: 'rgba(245,158,11,0.1)', color: 'var(--warning)', padding: '0.3rem 0.8rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700, fontFamily: 'JetBrains Mono, monospace', border: '1px solid rgba(245,158,11,0.3)' }}>NODE_08</div>
          </div>
          <code style={{ display: 'inline-block', fontSize: '0.8rem', color: 'var(--text-secondary)', background: 'rgba(0,0,0,0.5)', padding: '0.25rem 0.75rem', borderRadius: '4px', marginBottom: '1.5rem', fontFamily: 'JetBrains Mono, monospace', border: '1px solid rgba(255,255,255,0.05)' }}>SRC: agents/technique_agent.py → {'{ techniques, success }'}</code>
          
          <div className="markdown-body">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{resultData?.techniques || TECHNIQUE_MD}</ReactMarkdown>
          </div>
          <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border-color)' }}>
            <h4 style={{ color: 'white', fontSize: '0.95rem', marginBottom: '1rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Evaluation Metrics</h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
              {[
                { metric: 'COST_EFFICIENCY', method: 'Tokens × pricing', target: '≥60% REDUCTION', color: 'var(--success)' },
                { metric: 'QUALITY_SCORE', method: 'ROUGE-L + Eval', target: '≥8.5/10', color: 'var(--accent-primary)' },
                { metric: 'LATENCY', method: 'E2E Wall Clock', target: '<15s/QUERY', color: 'var(--warning)' },
                { metric: 'HALLUCINATION', method: 'Fact-check vs source', target: '<2%', color: 'var(--danger)' },
              ].map(m => (
                <div key={m.metric} style={{ background: 'rgba(0,0,0,0.4)', borderRadius: '8px', padding: '1.25rem', border: `1px solid ${m.color}30` }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontFamily: 'JetBrains Mono, monospace' }}>&gt; {m.metric}</div>
                  <div style={{ fontWeight: 800, color: m.color, fontSize: '1.2rem', marginBottom: '0.5rem' }}>{m.target}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontFamily: 'JetBrains Mono, monospace' }}>{m.method}</div>
                </div>
              ))}
            </div>
          </div>
       </div>

       {/* Tech Stack */}
       <div className="glass-panel" style={{ padding: '2.5rem', borderLeft: '4px solid var(--danger)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
            <span style={{ fontSize: '1.5rem', filter: 'drop-shadow(0 0 5px var(--danger))' }}>🏗️</span>
            <h3 style={{ color: 'var(--danger)', fontSize: '1.2rem', fontWeight: 700, flex: 1, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Technology Stack</h3>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
            {TECH_STACK.map(t => (
              <div key={t.layer} style={{ background: 'rgba(0,0,0,0.4)', borderRadius: '8px', padding: '1.25rem', border: '1px solid rgba(255,255,255,0.05)', transition: 'all 0.3s' }}
                   onMouseOver={e => { e.currentTarget.style.borderColor = 'var(--accent-primary)'; e.currentTarget.style.transform = 'translateY(-2px)'; }}
                   onMouseOut={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.05)'; e.currentTarget.style.transform = 'translateY(0)'; }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                  <span>{t.icon}</span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.1em', fontFamily: 'JetBrains Mono, monospace' }}>{t.layer}</span>
                </div>
                <div style={{ fontWeight: 700, color: 'white', marginBottom: '0.5rem', fontSize: '1.1rem' }}>{t.tech}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{t.rationale}</div>
              </div>
            ))}
          </div>
          
          {/* Copilot input */}
          <div style={{ display: 'flex', gap: '1rem', background: 'rgba(0,0,0,0.5)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
              <input value={inlineMsg} onChange={e => setInlineMsg(e.target.value)}
                 onKeyDown={e => { if (e.key === 'Enter' && inlineMsg.trim()) { onInlineChat?.(inlineMsg); setInlineMsg(''); } }}
                 placeholder="&gt; Consult Copilot (e.g. Can we use Vue instead of React?)"
                 style={{ flex: 1, background: 'transparent', border: 'none', color: 'white', padding: '0.5rem 1rem', outline: 'none', fontFamily: 'JetBrains Mono, monospace' }} />
              <button onClick={() => { if (inlineMsg.trim()) { onInlineChat?.(inlineMsg); setInlineMsg(''); } }}
                 className="btn-primary" style={{ padding: '0 2rem' }}>
                 ASK
              </button>
          </div>
       </div>

       {/* Guidance Agent */}
       <div className="glass-panel" style={{ padding: '2.5rem', borderLeft: '4px solid var(--success)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
            <span style={{ fontSize: '1.5rem', filter: 'drop-shadow(0 0 5px var(--success))' }}>📋</span>
            <h3 style={{ fontSize: '1.2rem', color: 'var(--success)', fontWeight: 700, flex: 1, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Guidance Module</h3>
            <div style={{ background: 'rgba(34,197,94,0.1)', color: 'var(--success)', padding: '0.3rem 0.8rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700, fontFamily: 'JetBrains Mono, monospace', border: '1px solid rgba(34,197,94,0.3)' }}>NODE_09</div>
          </div>
          <code style={{ display: 'inline-block', fontSize: '0.8rem', color: 'var(--text-secondary)', background: 'rgba(0,0,0,0.5)', padding: '0.25rem 0.75rem', borderRadius: '4px', marginBottom: '1.5rem', fontFamily: 'JetBrains Mono, monospace', border: '1px solid rgba(255,255,255,0.05)' }}>SRC: agents/guidance_agent.py → {'{ guidance, success }'}</code>
          <div className="markdown-body">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{resultData?.guidance || GUIDANCE_MD}</ReactMarkdown>
          </div>
       </div>
    </div>
  );
}
