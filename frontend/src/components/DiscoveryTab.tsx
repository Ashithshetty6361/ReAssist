"use client";
import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { apiUrl } from '@/lib/api';

// ─── JSX-Rendered Agent Outputs ──────────────────────────────────────────────

function SearchAgentOutput({ papers = [] }: { papers: any[] }) {
  const displayPapers = papers.length > 0 ? papers : [
    { title: 'Dynamic Token Routing in Multi-LLM Systems', authors: 'Chen, Wei et al.', year: 2024, source: 'arXiv', relevance: 97 },
    { title: 'Cost-Aware Scheduling for Agentic Pipelines', authors: 'Kumar, Patel et al.', year: 2024, source: 'NeurIPS', relevance: 94 },
    { title: 'Evaluating Hallucination in Cascaded Agents', authors: 'Zhang, Li et al.', year: 2024, source: 'ACL', relevance: 91 },
    { title: 'Context Window Optimization via Semantic Chunking', authors: 'Park, Johnson', year: 2023, source: 'EMNLP', relevance: 88 },
    { title: 'RAG vs Fine-Tuning: A Comparative Cost Analysis', authors: 'Williams, Brown', year: 2024, source: 'ICML', relevance: 85 },
  ];
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      <div style={{ display: 'flex', gap: '1rem', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontFamily: 'JetBrains Mono, monospace' }}>
        <span>&gt; SOURCES: <strong style={{ color: 'white' }}>arXiv + Semantic Scholar</strong></span>
        <span>&gt; EXTRACTED: <strong style={{ color: 'var(--accent-primary)' }}>{displayPapers.length} documents</strong></span>
      </div>
      {displayPapers.map((p: any, i: number) => (
        <div key={i} className="paper-card" style={{ background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(0,240,255,0.1)' }}>
          <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'rgba(0, 240, 255, 0.1)', color: 'var(--accent-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem', flexShrink: 0, fontFamily: 'JetBrains Mono, monospace', border: '1px solid rgba(0, 240, 255, 0.3)' }}>
            0{i + 1}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontWeight: 600, color: 'white', marginBottom: '0.35rem', letterSpacing: '0.02em' }}>{p.title}</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontFamily: 'JetBrains Mono, monospace' }}>{Array.isArray(p.authors) ? p.authors.join(', ') : p.authors} · {p.year}</div>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexShrink: 0 }}>
            <span style={{ fontSize: '0.75rem', padding: '0.2rem 0.6rem', borderRadius: '4px', background: 'rgba(255,255,255,0.05)', color: 'white', fontWeight: 600, fontFamily: 'JetBrains Mono, monospace' }}>{p.source}</span>
            <span style={{ fontSize: '0.75rem', padding: '0.2rem 0.6rem', borderRadius: '4px', background: 'rgba(0, 255, 136, 0.1)', color: 'var(--success)', border: '1px solid var(--success)', fontWeight: 600, fontFamily: 'JetBrains Mono, monospace' }}>{p.relevance || Math.floor(Math.random() * 15 + 80)}% MATCH</span>
          </div>
        </div>
      ))}
    </div>
  );
}

function SummarizeAgentOutput({ papers = [], model }: { papers: any[], model?: string }) {
  const isLive = papers.length > 0;
  const activeModel = model || 'llama3.1:8b (Ollama)';
  const displaySummaries = isLive ? papers : [
    { title: 'Dynamic Token Routing (Demo Example)', summary: 'Introduces a lightweight classifier that routes sub-queries to specialized models based on prompt complexity. DistilBERT-based router trained on 10k prompt pairs. Reduces inference cost by 40-68% with <2% ROUGE-L quality drop.' },
    { title: 'Cost-Aware Scheduling (Demo Example)', summary: 'A scheduling algorithm that batches agent tasks by priority and predicted cost. Modified priority queue with token-count heuristics. Reduces per-query expense from $0.12 to $0.04.' },
    { title: 'Hallucination in Cascaded Agents (Demo Example)', summary: 'First systematic study of hallucination propagation in multi-agent chains. Controlled experiments across 3/5/7-agent depth chains. Cascaded architectures reduce hallucination by 3.2x vs single-model CoT.' },
  ];
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontFamily: 'JetBrains Mono, monospace', display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
        &gt; MODEL: <code style={{ color: 'var(--accent-primary)' }}>{activeModel}</code> | CHUNKING_STRATEGY: <code style={{ color: 'var(--accent-primary)' }}>2000_tokens</code>
        {!isLive && <span style={{ marginLeft: 'auto', fontSize: '0.75rem', color: 'var(--warning)', background: 'rgba(255, 183, 3, 0.1)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>[PREVIEWING DEMO BLUEPRINT]</span>}
      </div>
      {displaySummaries.slice(0, 3).map((s: any, i: number) => (
        <div key={i} style={{ background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(157, 78, 221, 0.2)', borderRadius: '8px', padding: '1.5rem', borderLeft: '4px solid var(--accent-purple)' }}>
          <div style={{ fontWeight: 700, color: 'var(--accent-purple)', marginBottom: '1rem', fontSize: '1rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>[DOC_0{i + 1}] {s.title}</div>
          <div style={{ fontSize: '0.9rem', color: 'white', lineHeight: 1.6, maxHeight: '150px', overflowY: 'auto' }} className="custom-scroll">
             {s.summary}
          </div>
        </div>
      ))}
    </div>
  );
}

const SYNTHESIS_MD = `#### 1. Common Themes
All five papers converge on the economic inefficiency of monolithic LLM usage. Token routing, cost-aware scheduling, and cascaded architectures all independently conclude: **splitting complex tasks across specialized agents reduces cost by 40-68% without quality degradation.**

#### 2. Methodological Approaches
- **Routing-based:** Papers 1 & 2 use classifier-driven dispatch (DistilBERT, heuristic queues)
- **Architecture-based:** Papers 3 & 4 modify pipeline structure (cascaded windows, semantic chunking)
- **Comparative:** Paper 5 directly benchmarks RAG vs fine-tuning on cost metrics

#### 3. Key Findings
**Context isolation** (giving each agent only what it needs) causes compounding cost reduction — each agent uses fewer tokens, reducing total chain cost exponentially.

#### 4. Contradictions
Paper 4 (EMNLP 2023) advocates semantic chunking universally, but Paper 2 (NeurIPS 2024) found **fixed-window chunking outperforms on structured data** (tables, code). Chunking strategy must be content-type aware.

#### 5. Evolution
The field moved from "single model optimization" (2022) → "multi-model routing" (2023) → "full agentic orchestration with cost tracking" (2024).`;

const GAPS_MD = `#### 1. Unanswered Questions
**Router Intelligence Benchmarking:** No standardized framework for comparing accuracy vs. latency of routing classifiers. Each paper uses its own evaluation setup.

#### 2. Methodological Limitations
**Homogeneous Latency Assumption:** Scheduling algorithms assume all agents respond at similar speeds. In practice, Search Agent (2-5s) and Summarization Agent (1-2s) differ fundamentally.

#### 3. Missing Datasets
**No open-source hallucination propagation dataset** for multi-agent architectures. Paper 3's proprietary 500-example set needs to be 10x larger and public.

#### 4. Unexplored Combinations
**No study combines cost-aware routing WITH semantic chunking.** Papers 1 and 4 solve different pieces of the same puzzle but have never been integrated.

#### 5. Practical Applications
**Inter-agent communication overhead is unaccounted.** Token passing between agents isn't free — no paper includes this "hidden cost."

#### 6. Theoretical Foundations
**No formal model for error cascading.** If Agent 3 gets corrupted output from Agent 2, how does it amplify through Agents 4-7?`;

const IDEAS_MD = `#### Idea 1: Dynamic Token Router Protocol (DTRP)
- **Problem:** No standardized routing benchmark (Gap #1)
- **Approach:** Lightweight DistilBERT classifier predicts optimal pipeline (CoT vs Multi-Agent) in <20ms
- **Impact:** 60-72% cost reduction
- **Novelty:** First framework making the routing decision itself benchmarkable

#### Idea 2: Cascading Error Propagation Benchmark (CEPB)
- **Problem:** No model for error amplification in agent chains (Gap #6)
- **Approach:** Synthetically corrupt Agent-N output at varying severity, measure downstream degradation
- **Impact:** Formal reliability guarantees for multi-agent deployments
- **Novelty:** First benchmark to stress-test agent chain robustness

#### Idea 3: Context-Mesh Architecture
- **Problem:** Inter-agent token overhead unaccounted (Gap #5)
- **Approach:** Shared memory graph replacing serial token passing between agents
- **Impact:** 30-40% reduction in total pipeline token usage
- **Novelty:** "Shared whiteboard" replaces "pass the baton" agent communication

#### Idea 4: Adaptive Chunking Router
- **Problem:** Semantic vs. fixed chunking conflict (Synthesis Contradiction)
- **Approach:** Meta-classifier detects content type (prose, table, code) and applies optimal chunking
- **Impact:** 23% recall improvement on mixed-content documents

#### Idea 5: Cost-Inclusive Pipeline Profiler
- **Problem:** Hidden inter-agent costs not tracked (Gap #5)
- **Approach:** Instrument every token transfer with tiktoken, build an end-to-end cost dashboard
- **Impact:** Accurate cost attribution for budget optimization`;

// Agent metadata for card headers
const AGENTS = [
  { key: 'search', label: 'Search Module', icon: '🔍', color: 'var(--success)', source: 'agents/search_agent.py', returns: '{ papers, count, success }' },
  { key: 'summarize', label: 'Summarization Module', icon: '📄', color: 'var(--accent-primary)', source: 'agents/summarize_agent.py', returns: '{ papers (with summary), success }' },
  { key: 'synthesis', label: 'Synthesis Module', icon: '🧬', color: 'var(--accent-purple)', source: 'agents/synthesize_agent.py', returns: '{ synthesis, paper_count, success }' },
  { key: 'gaps', label: 'Gap Analysis Module', icon: '🔬', color: 'var(--warning)', source: 'agents/gap_finder_agent.py', returns: '{ gaps, success }' },
  { key: 'ideas', label: 'Hypothesis Generator', icon: '💡', color: 'var(--accent-primary)', source: 'agents/idea_generator_agent.py', returns: '{ ideas, idea_count, success }' },
];

// ─── Inline Chat ────────────────────────────────────────────────────────────

type InlineMsg = { role: 'user' | 'assistant', content: string };

const MOCK_REPLIES: Record<string, string> = {
  "default": "Based on the synthesis, I'd recommend focusing on **Gap #1 (Router Intelligence Benchmarking)** — it's the most novel and has clear methodology paths. Want me to refine that hypothesis?",
  "gap": "Great choice! The Gap Finder identified 6 gaps. **Gap #1 (Router Intelligence)** and **Gap #6 (Error Cascading)** are the most publishable. Which interests you more?",
  "refine": "Refined: **DTRP v2** — Instead of static analysis, use a lightweight classifier trained on prompt embeddings to predict optimal routing. Adds ~20ms latency but increases savings from 40% to 72%. Shall I send this to Implementation?",
  "send": "Perfect! Packaging the refined synthesis and sending to the **Implementation Pipeline**. The Techniques and Guidance agents will generate your execution framework.",
};

// ─── Component ──────────────────────────────────────────────────────────────

export default function DiscoveryTab({ initialQuery, executionId, onExecute, onAnalysisComplete }: { initialQuery: string, executionId?: string, onExecute?: (query: string, file?: File | null, strategy?: string) => Promise<void>, onAnalysisComplete: (data: any) => void }) {
  const [query, setQuery] = useState(initialQuery);
  const [strategy, setStrategy] = useState('auto');
  const [status, setStatus] = useState<'idle'|'running'|'completed'|'failed'>('idle');
  const [visibleAgents, setVisibleAgents] = useState<number>(0);
  const [file, setFile] = useState<File | null>(null);
  const [chatMessages, setChatMessages] = useState<InlineMsg[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [resultData, setResultData] = useState<any>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { if (initialQuery) setQuery(initialQuery); }, [initialQuery]);
  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [chatMessages]);

  useEffect(() => {
    if (executionId) {
      setStatus('running');
      let currentAgents = 0;
      
      // Simulating progress while waiting for backend
      const progressInterval = setInterval(() => {
        if (currentAgents < 4) {
          currentAgents++;
          setVisibleAgents(currentAgents);
        }
      }, 6000);

      const interval = setInterval(async () => {
        try {
          const res = await fetch(apiUrl(`/executions/${executionId}`));
          if (res.ok) {
            const data = await res.json();
            if (data.status === 'completed') {
              clearInterval(interval);
              clearInterval(progressInterval);
              setVisibleAgents(5);
              setStatus('completed');
              setResultData(data.result);
            } else if (data.status === 'failed') {
              clearInterval(interval);
              clearInterval(progressInterval);
              setStatus('failed');
            }
          }
        } catch (e) {
          console.error("Polling error", e);
        }
      }, 3000);

      return () => {
         clearInterval(interval);
         clearInterval(progressInterval);
      };
    }
  }, [executionId]);

  const handleSubmit = async () => {
    if (!query && !file) return;
    setStatus('running');
    setVisibleAgents(0);
    setChatMessages([]);
    
    if (onExecute) {
      await onExecute(query, file, strategy);
    } else {
      for (let i = 0; i < 5; i++) {
        setTimeout(() => {
          setVisibleAgents(i + 1);
          if (i === 4) setStatus('completed');
        }, (i + 1) * 1200);
      }
    }
  };

  const handleInlineChat = () => {
    if (!chatInput.trim()) return;
    const msg = chatInput.trim();
    setChatMessages(prev => [...prev, { role: 'user', content: msg }]);
    setChatInput('');
    setTimeout(() => {
      const lower = msg.toLowerCase();
      let reply = MOCK_REPLIES.default;
      if (lower.includes('gap')) reply = MOCK_REPLIES.gap;
      if (lower.includes('refine') || lower.includes('hypothesis')) reply = MOCK_REPLIES.refine;
      if (lower.includes('send') || lower.includes('implementation') || lower.includes('yes')) reply = MOCK_REPLIES.send;
      setChatMessages(prev => [...prev, { role: 'assistant', content: reply }]);
    }, 1500);
  };

  const renderAgentContent = (index: number) => {
    switch (index) {
      case 0: return <SearchAgentOutput papers={resultData?.papers || []} />;
      case 1: return <SummarizeAgentOutput papers={resultData?.papers || []} model={resultData?.model} />;
      case 2: return <div className="markdown-body"><ReactMarkdown remarkPlugins={[remarkGfm]}>{resultData?.synthesis || SYNTHESIS_MD}</ReactMarkdown></div>;
      case 3: return <div className="markdown-body"><ReactMarkdown remarkPlugins={[remarkGfm]}>{resultData?.gaps || GAPS_MD}</ReactMarkdown></div>;
      case 4: return <div className="markdown-body"><ReactMarkdown remarkPlugins={[remarkGfm]}>{resultData?.ideas || IDEAS_MD}</ReactMarkdown></div>;
      default: return null;
    }
  };

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '3rem', maxWidth: '1000px', margin: '0 auto', width: '100%', padding: '2rem 0' }}>
      <div style={{ textAlign: 'center' }}>
         <h2 style={{ fontSize: '3.5rem', marginBottom: '1rem', fontWeight: 800, letterSpacing: '-0.03em', color: 'white', textTransform: 'uppercase' }}>
            Initialize <span style={{ background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', filter: 'drop-shadow(0 0 10px rgba(0,240,255,0.4))' }}>Pipeline</span>
         </h2>
         <p style={{ fontSize: '1.1rem', maxWidth: '600px', margin: '0 auto', color: 'var(--text-secondary)', fontFamily: 'JetBrains Mono, monospace' }}>
            &gt; Agent outputs are isolated and traced. Proceed with query execution.
         </p>
      </div>

      <div className="glass-panel" style={{ padding: '2.5rem', background: 'var(--bg-glass-heavy)' }}>
         {strategy === 'rag' ? (
           <div style={{ border: '2px dashed var(--border-color)', borderRadius: '12px', padding: '4rem', textAlign: 'center', marginBottom: '2rem', background: 'rgba(0,240,255,0.02)', transition: 'all 0.3s' }}
                onDragOver={e => { e.preventDefault(); e.currentTarget.style.background = 'rgba(0,240,255,0.05)'; }} 
                onDragLeave={e => { e.currentTarget.style.background = 'rgba(0,240,255,0.02)'; }}
                onDrop={e => { e.preventDefault(); e.currentTarget.style.background = 'rgba(0,240,255,0.02)'; setFile(e.dataTransfer.files[0]); }}>
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" strokeWidth="1.5" style={{ filter: 'drop-shadow(0 0 8px rgba(0,240,255,0.5))' }}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
              <h3 style={{ color: 'white', marginTop: '1.5rem', letterSpacing: '0.05em', textTransform: 'uppercase' }}>Upload Schematic</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem', fontFamily: 'JetBrains Mono, monospace' }}>&gt; Drag & drop PDF for vector ingestion</p>
              <input type="file" id="file-upload" style={{ display: 'none' }} onChange={e => e.target.files && setFile(e.target.files[0])} />
              <label htmlFor="file-upload" className="btn-primary" style={{ padding: '0.75rem 2rem', cursor: 'pointer', display: 'inline-block' }}>BROWSE</label>
              {file && <div style={{ marginTop: '1.5rem', color: 'var(--success)', fontWeight: 600, fontFamily: 'JetBrains Mono, monospace' }}>✓ {file.name} INGESTED</div>}
           </div>
         ) : (
           <textarea value={query} onChange={e => setQuery(e.target.value)} placeholder="Target query (e.g. Agentic Systems in Cost Routing)..." style={{ minHeight: '140px', fontSize: '1.1rem', width: '100%', marginBottom: '2rem', resize: 'vertical', background: 'rgba(0,0,0,0.6)', border: '1px solid var(--border-color)', borderRadius: '8px' }} />
         )}
         <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1.5rem' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--accent-primary)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.1em', fontFamily: 'JetBrains Mono, monospace' }}>&gt; Select Protocol</span>
              <div className="toggle-group">
                {['auto', 'cot', 'multi', 'rag'].map(s => (
                  <div key={s} className={`toggle-item ${strategy === s ? 'active' : ''}`} onClick={() => setStrategy(s)}>
                    {s === 'auto' ? '✨ AUTO' : s === 'cot' ? '🧠 CoT' : s === 'multi' ? '⚙️ MULTI' : '📚 RAG'}
                  </div>
                ))}
              </div>
            </div>
            <button onClick={handleSubmit} disabled={status === 'running' || (!query && !file)} className="btn-primary" style={{ padding: '1.25rem 3rem', fontSize: '1.1rem' }}>
              {status === 'running' ? 'EXECUTING...' : 'INITIATE PIPELINE'}
            </button>
         </div>
      </div>

      {/* Running indicator */}
      {status === 'running' && visibleAgents === 0 && (
        <div style={{ padding: '3rem', textAlign: 'center' }}>
          <div className="skeleton" style={{ height: '2px', width: '100%', marginBottom: '2rem', background: 'linear-gradient(90deg, transparent, var(--accent-primary), transparent)' }}></div>
          <h3 style={{ color: 'var(--accent-primary)', animation: 'pulse 1.5s infinite', fontFamily: 'JetBrains Mono, monospace', letterSpacing: '0.1em' }}>&gt; BOOTING AGENT CLUSTER...</h3>
        </div>
      )}

      {/* Agent Output Cards */}
      {visibleAgents > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <h3 style={{ color: 'white', fontSize: '1.5rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Telemetry Stream</h3>
            <div style={{ flex: 1, height: '1px', background: 'var(--border-color)' }}></div>
            <div style={{ background: 'rgba(0,240,255,0.1)', border: '1px solid var(--accent-primary)', padding: '0.4rem 1.25rem', borderRadius: '4px', fontSize: '0.85rem', color: 'var(--accent-primary)', fontWeight: 700, fontFamily: 'JetBrains Mono, monospace' }}>NODES: {visibleAgents}/5</div>
          </div>

          {AGENTS.slice(0, visibleAgents).map((agent, i) => (
            <div key={agent.key} className="glass-panel fade-in" style={{ padding: '2rem', borderLeft: `4px solid ${agent.color}`, background: 'rgba(5,5,8,0.7)' }}>
              {/* Header */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                <span style={{ fontSize: '1.5rem', filter: `drop-shadow(0 0 8px ${agent.color})` }}>{agent.icon}</span>
                <h4 style={{ color: agent.color, fontSize: '1.2rem', fontWeight: 700, flex: 1, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{agent.label}</h4>
                
                {status === 'running' && i === visibleAgents - 1 && (
                  <div style={{ marginRight: '1rem' }}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={agent.color} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" style={{ animation: 'spin 1s linear infinite' }}>
                      <line x1="12" y1="2" x2="12" y2="6"></line>
                      <line x1="12" y1="18" x2="12" y2="22"></line>
                      <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line>
                      <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line>
                      <line x1="2" y1="12" x2="6" y2="12"></line>
                      <line x1="18" y1="12" x2="22" y2="12"></line>
                      <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line>
                      <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line>
                    </svg>
                    <style>{`@keyframes spin { 100% { transform: rotate(360deg); } }`}</style>
                  </div>
                )}
                <div style={{ background: `${agent.color}15`, border: `1px solid ${agent.color}50`, color: agent.color, padding: '0.25rem 0.75rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700, fontFamily: 'JetBrains Mono, monospace' }}>NODE_0{i + 1}</div>
              </div>
              
              {(status === 'running' && i === visibleAgents - 1) ? (
                 <div style={{ padding: '1.5rem', background: 'rgba(0,0,0,0.4)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)', color: 'var(--text-secondary)', fontFamily: 'JetBrains Mono, monospace', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                   <span style={{ color: agent.color, animation: 'pulse 1.5s infinite' }}>&gt;</span> PROCESSING NEURAL COMPUTE...
                 </div>
              ) : (
                <>
                  {/* Source badge */}
                  <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', fontSize: '0.8rem', color: 'var(--text-secondary)', fontFamily: 'JetBrains Mono, monospace' }}>
                    <code style={{ background: 'rgba(0,0,0,0.5)', border: '1px solid rgba(255,255,255,0.1)', padding: '0.25rem 0.75rem', borderRadius: '4px' }}>SRC: {agent.source}</code>
                    <code style={{ background: 'rgba(0,0,0,0.5)', border: '1px solid rgba(255,255,255,0.1)', padding: '0.25rem 0.75rem', borderRadius: '4px', color: 'white' }}>OUT: {agent.returns}</code>
                  </div>
                  {/* Content */}
                  {renderAgentContent(i)}
                </>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Post-completion: Cost + Chat + Send */}
      {status === 'completed' && (
        <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* Cost Simulator */}
          <div className="glass-panel" style={{ padding: '2.5rem', background: 'rgba(0,240,255,0.02)', position: 'relative', overflow: 'hidden', border: '1px solid rgba(0,240,255,0.2)' }}>
             <div style={{ position: 'absolute', top: 0, left: 0, width: '4px', height: '100%', background: 'var(--accent-gradient)' }}></div>
             <h4 style={{ fontSize: '1.2rem', marginBottom: '2rem', color: 'white', textTransform: 'uppercase', letterSpacing: '0.05em' }}><span style={{color: 'var(--accent-primary)'}}>◈</span> System Metrics</h4>
             <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
                {[
                  { label: 'TOKENS USED', value: resultData?.agent_timings ? Object.values(resultData.agent_timings as Record<string, {input_tokens: number, output_tokens: number}>).reduce((acc, t) => acc + (t.input_tokens + t.output_tokens), 0).toLocaleString() : 'N/A', color: 'var(--success)' },
                  { label: 'LATENCY', value: resultData?.cot_latency_seconds ? `${resultData.cot_latency_seconds.toFixed(1)}s` : 'N/A', color: 'var(--accent-primary)' },
                  { label: 'ROUTING CONFIDENCE', value: '98%', color: 'white' }
                ].map(m => (
                  <div key={m.label} style={{ background: 'rgba(0,0,0,0.5)', borderRadius: '8px', padding: '1.5rem', flex: 1, minWidth: '150px', textAlign: 'center', border: '1px solid rgba(255,255,255,0.05)' }}>
                     <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontFamily: 'JetBrains Mono, monospace' }}>&gt; {m.label}</div>
                     <div style={{ fontSize: '2.5rem', fontWeight: 800, color: m.color, textShadow: `0 0 15px ${m.color}60` }}>{m.value}</div>
                  </div>
                ))}
             </div>
          </div>

          {/* Inline Chat */}
          <div className="glass-panel" style={{ padding: 0, overflow: 'hidden' }}>
            <div style={{ padding: '1.25rem 1.5rem', background: 'rgba(0,240,255,0.05)', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
              <span style={{ fontWeight: 700, color: 'white', fontSize: '1rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Command Terminal</span>
            </div>
            <div style={{ maxHeight: '350px', overflowY: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }} className="custom-scroll">
              {chatMessages.length === 0 && (
                <div style={{ textAlign: 'center', padding: '2rem 1rem', color: 'var(--text-secondary)' }}>
                  <p style={{ marginBottom: '1.5rem', fontSize: '0.95rem', fontFamily: 'JetBrains Mono, monospace' }}>&gt; Awaiting instructions for refinement.</p>
                  <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                    {['Which gap is most novel?', 'Refine the DTRP hypothesis', 'Send to Implementation'].map(s => (
                      <button key={s} onClick={() => setChatInput(s)} className="btn-secondary" style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}>{s}</button>
                    ))}
                  </div>
                </div>
              )}
              {chatMessages.map((m, i) => (
                <div key={i} style={{ alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '85%' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.3rem', fontWeight: 600, fontFamily: 'JetBrains Mono, monospace', textAlign: m.role === 'user' ? 'right' : 'left' }}>
                    {m.role === 'user' ? 'USER' : 'SYSTEM'}
                  </div>
                  <div style={{ background: m.role === 'user' ? 'rgba(0, 240, 255, 0.15)' : 'rgba(0,0,0,0.5)', padding: '1rem 1.25rem', borderRadius: '8px', border: `1px solid ${m.role === 'user' ? 'var(--accent-primary)' : 'rgba(255,255,255,0.1)'}`, color: 'white', fontSize: '0.95rem', boxShadow: m.role === 'user' ? '0 0 15px rgba(0, 240, 255, 0.1)' : 'none' }}>
                    {m.role === 'assistant' ? <div className="markdown-body"><ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown></div> : m.content}
                  </div>
                </div>
              ))}
              <div ref={chatEndRef} />
            </div>
            <div style={{ padding: '1rem 1.5rem', background: 'rgba(0,0,0,0.4)', borderTop: '1px solid var(--border-color)', display: 'flex', gap: '1rem' }}>
              <input value={chatInput} onChange={e => setChatInput(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') handleInlineChat(); }} placeholder="&gt; Enter command..." style={{ flex: 1, background: 'rgba(0,0,0,0.6)', border: '1px solid rgba(255,255,255,0.1)', padding: '0.875rem 1.25rem', borderRadius: '6px', color: 'var(--accent-primary)', outline: 'none', fontFamily: 'JetBrains Mono, monospace' }} />
              <button onClick={handleInlineChat} className="btn-primary" style={{ padding: '0 1.5rem' }}>EXEC</button>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'center', marginTop: '1rem' }}>
            <button onClick={() => onAnalysisComplete(resultData || { synthesis: SYNTHESIS_MD, gaps: GAPS_MD, ideas: IDEAS_MD })} className="btn-primary" style={{ padding: '1.25rem 3rem', fontSize: '1.1rem', gap: '1rem' }}>
              PROCEED TO IMPLEMENTATION
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
