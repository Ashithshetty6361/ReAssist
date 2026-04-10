"use client";
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// ─── Architecture Flow Diagram (Claude-style animated reveal) ───────────────

const ARCH_NODES = [
  { label: 'User Query / PDF Upload', desc: 'Research topic or document enters the system', icon: '📝', color: '#22c55e' },
  { label: 'AgenticOps Router', desc: 'Classifies complexity → selects optimal pipeline (CoT vs Multi-Agent)', icon: '🧠', color: '#3b82f6' },
  { label: 'Search Agent', desc: 'Queries arXiv + Semantic Scholar for relevant papers', icon: '🔍', color: '#22c55e' },
  { label: 'Summarization Agent', desc: 'Chunks papers via tiktoken, extracts atomic facts per paper', icon: '📄', color: '#06b6d4' },
  { label: 'Synthesis Agent', desc: 'Cross-references all summaries, finds consensus & contradictions', icon: '🧬', color: '#8b5cf6' },
  { label: 'Gap Finder Agent', desc: 'Identifies 6 categories of missing research (unanswered Q, datasets, etc.)', icon: '🔬', color: '#f59e0b' },
  { label: 'Idea Generator Agent', desc: 'Generates 5 novel hypotheses with problem-approach-impact-novelty', icon: '💡', color: '#3b82f6' },
  { label: 'Technique Agent', desc: 'Suggests alternative algorithms NOT used in existing papers', icon: '⚙️', color: '#ef4444' },
  { label: 'Implementation Guidance Agent', desc: 'Builds phased execution plan with week-by-week breakdown', icon: '📋', color: '#10b981' },
];

function ArchitectureDiagram() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
      {ARCH_NODES.map((node, i) => (
        <div key={i}>
          <div className="arch-node" style={{ animationDelay: `${i * 0.15}s` }}>
            <div className="arch-node-number" style={{ background: `${node.color}20`, color: node.color, border: `2px solid ${node.color}` }}>
              {String(i + 1).padStart(2, '0')}
            </div>
            <span style={{ fontSize: '1.3rem' }}>{node.icon}</span>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700, color: 'white', marginBottom: '0.2rem' }}>{node.label}</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{node.desc}</div>
            </div>
          </div>
          {i < ARCH_NODES.length - 1 && (
            <div className="arch-connector" style={{ animationDelay: `${i * 0.15 + 0.1}s` }}>
              <svg width="16" height="24" viewBox="0 0 16 24"><line x1="8" y1="0" x2="8" y2="18" strokeWidth="2"/><polyline points="4 14 8 20 12 14" fill="none" strokeWidth="2"/></svg>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// ─── Tech Stack ─────────────────────────────────────────────────────────────

const TECH_STACK = [
  { layer: 'Frontend', tech: 'Next.js 16 (React)', rationale: 'Server Components for fast artifact rendering', icon: '🌐' },
  { layer: 'Backend API', tech: 'FastAPI (Python)', rationale: 'Native async, auto-docs, Pydantic validation', icon: '⚡' },
  { layer: 'Agent Framework', tech: 'LangChain + Custom Router', rationale: 'Modular agent composition with cost-aware routing', icon: '🔗' },
  { layer: 'Vector Database', tech: 'ChromaDB → pgvector', rationale: 'Start local, migrate to Postgres at scale', icon: '🗃️' },
  { layer: 'Relational DB', tech: 'PostgreSQL 16', rationale: 'ACID compliance for session/trace persistence', icon: '🐘' },
  { layer: 'Auth', tech: 'JWT + bcrypt', rationale: 'Stateless, scalable authentication', icon: '🔐' },
  { layer: 'Deployment', tech: 'Docker Compose', rationale: 'Single-command local + production deployment', icon: '🐳' },
  { layer: 'Monitoring', tech: 'tiktoken + custom logger', rationale: 'Per-agent token tracking and cost attribution', icon: '📊' },
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
1. Initialize backend with \`pip install fastapi langchain chromadb openai\`
2. Scaffold the Router with a lightweight classifier
3. Create \`agents/\` directory with modular agent classes

#### Phase 2: Pipeline Construction (Week 2-3)
4. Wire 7-Agent Chain: Search → Summarize → Synthesis → Gap → Idea → Technique → Guidance
5. Add Token Tracking with \`tiktoken\` per agent
6. Connect ChromaDB for RAG document ingestion

#### Phase 3: Benchmarking (Week 4)
7. Build Evaluation Harness in \`evaluation/evaluator.py\`
8. Run 500-query benchmark, logging cost and quality per run
9. Auto-generate comparison charts

#### Phase 4: Deployment (Week 5)
10. Containerize with Docker
11. Add JWT auth for multi-user access
12. Deploy with Docker Compose + PostgreSQL`;

// ─── Component ──────────────────────────────────────────────────────────────

export default function ImplementationTab({ resultData, onInlineChat }: { resultData: any, onInlineChat?: (msg: string) => void }) {
  const [inlineMsg, setInlineMsg] = useState('');
  const [showArch, setShowArch] = useState(false);

  if (!resultData) {
    return (
      <div className="fade-in" style={{ textAlign: 'center', padding: '6rem 2rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
         <div style={{ padding: '2rem', background: 'rgba(255,255,255,0.03)', borderRadius: '50%', marginBottom: '2rem' }}>
           <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
         </div>
         <h3 style={{ fontSize: '1.5rem', color: 'white', marginBottom: '0.5rem' }}>Awaiting Synthesis Results</h3>
         <p style={{ maxWidth: '400px', lineHeight: 1.6 }}>Complete the Synthesis pipeline and send results here.</p>
      </div>
    );
  }

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '1000px', margin: '0 auto', width: '100%', padding: '2rem 0' }}>
       <div style={{ textAlign: 'center', marginBottom: '0.5rem' }}>
         <h2 style={{ fontSize: '3rem', fontWeight: 800, color: 'white', letterSpacing: '-0.02em', marginBottom: '1rem' }}>
           Architecture <span style={{ color: 'var(--danger)' }}>Implementation</span>
         </h2>
         <p style={{ fontSize: '1.1rem', color: 'var(--text-secondary)' }}>Your complete execution blueprint, generated by the Techniques and Guidance agents.</p>
       </div>

       {/* Architecture Diagram Toggle */}
       <div className="glass-panel" style={{ padding: '1.5rem', overflow: 'hidden' }}>
         <div onClick={() => setShowArch(!showArch)} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}>
           <span style={{ fontSize: '1.3rem' }}>🏗️</span>
           <h4 style={{ color: 'white', fontSize: '1.1rem', fontWeight: 700, flex: 1 }}>Project Architecture Flow</h4>
           <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" strokeWidth="2" style={{ transition: 'transform 0.3s', transform: showArch ? 'rotate(180deg)' : 'rotate(0)' }}>
             <polyline points="6 9 12 15 18 9"/>
           </svg>
         </div>
         {showArch && (
           <div className="fade-in" style={{ marginTop: '1.5rem' }}>
             <ArchitectureDiagram />
           </div>
         )}
       </div>

       {/* Techniques Agent */}
       <div className="glass-panel" style={{ padding: '2rem', borderLeft: '4px solid #f59e0b' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '1.4rem' }}>🔬</span>
            <h3 style={{ fontSize: '1.15rem', color: '#f59e0b', fontWeight: 700, flex: 1 }}>Techniques Agent</h3>
            <div style={{ background: 'rgba(245,158,11,0.15)', color: '#f59e0b', padding: '0.2rem 0.65rem', borderRadius: '999px', fontSize: '0.75rem', fontWeight: 700 }}>Agent 6</div>
          </div>
          <code style={{ display: 'inline-block', fontSize: '0.75rem', color: 'var(--text-secondary)', background: 'rgba(255,255,255,0.06)', padding: '0.15rem 0.5rem', borderRadius: '4px', marginBottom: '1.25rem' }}>agents/technique_agent.py → {'{ techniques, success }'}</code>
          
          {/* Evaluation Metrics as JSX table */}
          <div className="markdown-body">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{TECHNIQUE_MD}</ReactMarkdown>
          </div>
          <div style={{ marginTop: '1.5rem' }}>
            <h4 style={{ color: 'white', fontSize: '0.95rem', marginBottom: '0.75rem', fontWeight: 600 }}>Evaluation Metrics</h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
              {[
                { metric: 'Cost Efficiency', method: 'Tokens × model pricing', target: '≥60% reduction', color: '#22c55e' },
                { metric: 'Quality Score', method: 'ROUGE-L + Human eval', target: '≥8.5/10', color: '#3b82f6' },
                { metric: 'Latency', method: 'End-to-end wall clock', target: '<15s/query', color: '#f59e0b' },
                { metric: 'Hallucination', method: 'Fact-check vs source', target: '<2%', color: '#ef4444' },
              ].map(m => (
                <div key={m.metric} style={{ background: 'rgba(0,0,0,0.25)', borderRadius: '10px', padding: '1rem', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>{m.metric}</div>
                  <div style={{ fontWeight: 700, color: m.color, fontSize: '1.1rem', marginBottom: '0.25rem' }}>{m.target}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{m.method}</div>
                </div>
              ))}
            </div>
          </div>
       </div>

       {/* Tech Stack as JSX cards */}
       <div className="glass-panel" style={{ padding: '2rem', borderLeft: '4px solid var(--danger)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
            <span style={{ fontSize: '1.4rem' }}>🏗️</span>
            <h3 style={{ color: 'var(--danger)', fontSize: '1.15rem', fontWeight: 700, flex: 1 }}>Technology Stack</h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Ask Copilot to swap →</span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '0.75rem', marginBottom: '1.5rem' }}>
            {TECH_STACK.map(t => (
              <div key={t.layer} style={{ background: 'rgba(0,0,0,0.25)', borderRadius: '10px', padding: '1rem', border: '1px solid rgba(255,255,255,0.06)', transition: 'all 0.2s' }}
                   onMouseOver={e => (e.currentTarget.style.borderColor = 'var(--border-hover)')}
                   onMouseOut={e => (e.currentTarget.style.borderColor = 'rgba(255,255,255,0.06)')}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <span>{t.icon}</span>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{t.layer}</span>
                </div>
                <div style={{ fontWeight: 700, color: 'white', marginBottom: '0.3rem' }}>{t.tech}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>{t.rationale}</div>
              </div>
            ))}
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', background: 'rgba(0,0,0,0.3)', padding: '0.5rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
              <input value={inlineMsg} onChange={e => setInlineMsg(e.target.value)}
                 onKeyDown={e => { if (e.key === 'Enter' && inlineMsg.trim()) { onInlineChat?.(inlineMsg); setInlineMsg(''); } }}
                 placeholder="E.g. Can we use Vue instead of React? What about Supabase?"
                 style={{ flex: 1, background: 'transparent', border: 'none', color: 'white', padding: '0.5rem', outline: 'none' }} />
              <button onClick={() => { if (inlineMsg.trim()) { onInlineChat?.(inlineMsg); setInlineMsg(''); } }}
                 style={{ padding: '0 1.5rem', background: 'var(--accent-gradient)', border: 'none', borderRadius: '8px', color: 'white', fontWeight: 600, cursor: 'pointer' }}>
                 Ask Copilot →
              </button>
          </div>
       </div>

       {/* Guidance Agent */}
       <div className="glass-panel" style={{ padding: '2rem', borderLeft: '4px solid var(--success)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '1.4rem' }}>📋</span>
            <h3 style={{ fontSize: '1.15rem', color: 'var(--success)', fontWeight: 700, flex: 1 }}>Implementation Guidance Agent</h3>
            <div style={{ background: 'rgba(34,197,94,0.15)', color: 'var(--success)', padding: '0.2rem 0.65rem', borderRadius: '999px', fontSize: '0.75rem', fontWeight: 700 }}>Agent 7</div>
          </div>
          <code style={{ display: 'inline-block', fontSize: '0.75rem', color: 'var(--text-secondary)', background: 'rgba(255,255,255,0.06)', padding: '0.15rem 0.5rem', borderRadius: '4px', marginBottom: '1.25rem' }}>agents/guidance_agent.py → {'{ guidance, success }'}</code>
          <div className="markdown-body">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{GUIDANCE_MD}</ReactMarkdown>
          </div>
       </div>
    </div>
  );
}
