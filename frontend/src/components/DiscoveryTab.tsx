"use client";
import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// ─── JSX-Rendered Agent Outputs (No broken markdown tables) ─────────────────

function SearchAgentOutput() {
  const papers = [
    { title: 'Dynamic Token Routing in Multi-LLM Systems', authors: 'Chen, Wei et al.', year: 2024, source: 'arXiv', relevance: 97 },
    { title: 'Cost-Aware Scheduling for Agentic Pipelines', authors: 'Kumar, Patel et al.', year: 2024, source: 'NeurIPS', relevance: 94 },
    { title: 'Evaluating Hallucination in Cascaded Agents', authors: 'Zhang, Li et al.', year: 2024, source: 'ACL', relevance: 91 },
    { title: 'Context Window Optimization via Semantic Chunking', authors: 'Park, Johnson', year: 2023, source: 'EMNLP', relevance: 88 },
    { title: 'RAG vs Fine-Tuning: A Comparative Cost Analysis', authors: 'Williams, Brown', year: 2024, source: 'ICML', relevance: 85 },
  ];
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      <div style={{ display: 'flex', gap: '1rem', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
        <span>📡 <strong style={{ color: 'white' }}>Sources:</strong> arXiv + Semantic Scholar</span>
        <span>📊 <strong style={{ color: 'white' }}>Found:</strong> {papers.length} papers</span>
      </div>
      {papers.map((p, i) => (
        <div key={i} className="paper-card">
          <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: 'rgba(34,197,94,0.15)', color: '#22c55e', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem', flexShrink: 0 }}>
            {i + 1}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontWeight: 600, color: 'white', marginBottom: '0.25rem' }}>{p.title}</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{p.authors} · {p.year}</div>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexShrink: 0 }}>
            <span style={{ fontSize: '0.8rem', padding: '0.2rem 0.6rem', borderRadius: '999px', background: 'rgba(59,130,246,0.15)', color: 'var(--accent-primary)', fontWeight: 600 }}>{p.source}</span>
            <span style={{ fontSize: '0.8rem', padding: '0.2rem 0.6rem', borderRadius: '999px', background: 'rgba(34,197,94,0.15)', color: '#22c55e', fontWeight: 600 }}>{p.relevance}%</span>
          </div>
        </div>
      ))}
    </div>
  );
}

function SummarizeAgentOutput() {
  const summaries = [
    { title: 'Dynamic Token Routing', contribution: 'Introduces a lightweight classifier that routes sub-queries to specialized models based on prompt complexity.', method: 'DistilBERT-based router trained on 10k prompt pairs', finding: 'Reduces inference cost by 40-68% with <2% ROUGE-L quality drop', limitation: 'Only tested on English-language prompts' },
    { title: 'Cost-Aware Scheduling', contribution: 'A scheduling algorithm that batches agent tasks by priority and predicted cost.', method: 'Modified priority queue with token-count heuristics', finding: 'Reduces per-query expense from $0.12 to $0.04', limitation: 'Assumes homogeneous agent latency' },
    { title: 'Hallucination in Cascaded Agents', contribution: 'First systematic study of hallucination propagation in multi-agent chains.', method: 'Controlled experiments across 3/5/7-agent depth chains', finding: 'Cascaded architectures reduce hallucination by 3.2x vs single-model CoT', limitation: 'Tested only on factual QA tasks' },
  ];
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>📋 Model: <code style={{ background: 'rgba(255,255,255,0.1)', padding: '2px 6px', borderRadius: '4px' }}>gpt-3.5-turbo</code> · Chunking: 2000 tokens/chunk</div>
      {summaries.map((s, i) => (
        <div key={i} style={{ background: 'rgba(0,0,0,0.25)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: '12px', padding: '1.25rem', borderLeft: '3px solid #06b6d4' }}>
          <div style={{ fontWeight: 700, color: '#06b6d4', marginBottom: '0.75rem', fontSize: '1rem' }}>Paper {i + 1} — {s.title}</div>
          <div style={{ display: 'grid', gap: '0.5rem', fontSize: '0.9rem' }}>
            <div><span style={{ color: 'var(--text-secondary)' }}>Main Contribution:</span> <span style={{ color: 'white' }}>{s.contribution}</span></div>
            <div><span style={{ color: 'var(--text-secondary)' }}>Methods:</span> <span style={{ color: 'white' }}>{s.method}</span></div>
            <div><span style={{ color: 'var(--text-secondary)' }}>Key Finding:</span> <span style={{ color: '#22c55e', fontWeight: 600 }}>{s.finding}</span></div>
            <div><span style={{ color: 'var(--text-secondary)' }}>Limitation:</span> <span style={{ color: '#f59e0b' }}>{s.limitation}</span></div>
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
  { key: 'search', label: 'Search Agent', icon: '🔍', color: '#22c55e', source: 'agents/search_agent.py', returns: '{ papers, count, success }' },
  { key: 'summarize', label: 'Summarization Agent', icon: '📄', color: '#06b6d4', source: 'agents/summarize_agent.py', returns: '{ papers (with summary), success }' },
  { key: 'synthesis', label: 'Synthesis Agent', icon: '🧬', color: '#8b5cf6', source: 'agents/synthesize_agent.py', returns: '{ synthesis, paper_count, success }' },
  { key: 'gaps', label: 'Gap Finder Agent', icon: '🔬', color: '#f59e0b', source: 'agents/gap_finder_agent.py', returns: '{ gaps, success }' },
  { key: 'ideas', label: 'Idea Generator Agent', icon: '💡', color: '#3b82f6', source: 'agents/idea_generator_agent.py', returns: '{ ideas, idea_count, success }' },
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

export default function DiscoveryTab({ initialQuery, onAnalysisComplete }: { initialQuery: string, onAnalysisComplete: (data: any) => void }) {
  const [query, setQuery] = useState(initialQuery);
  const [strategy, setStrategy] = useState('auto');
  const [status, setStatus] = useState<'idle'|'running'|'completed'|'failed'>('idle');
  const [visibleAgents, setVisibleAgents] = useState<number>(0);
  const [file, setFile] = useState<File | null>(null);
  const [chatMessages, setChatMessages] = useState<InlineMsg[]>([]);
  const [chatInput, setChatInput] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { if (initialQuery) setQuery(initialQuery); }, [initialQuery]);
  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [chatMessages]);

  const handleSubmit = async () => {
    if (!query && !file) return;
    setStatus('running');
    setVisibleAgents(0);
    setChatMessages([]);
    // Staggered reveal
    for (let i = 0; i < 5; i++) {
      setTimeout(() => {
        setVisibleAgents(i + 1);
        if (i === 4) setStatus('completed');
      }, (i + 1) * 1200);
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
      case 0: return <SearchAgentOutput />;
      case 1: return <SummarizeAgentOutput />;
      case 2: return <div className="markdown-body"><ReactMarkdown remarkPlugins={[remarkGfm]}>{SYNTHESIS_MD}</ReactMarkdown></div>;
      case 3: return <div className="markdown-body"><ReactMarkdown remarkPlugins={[remarkGfm]}>{GAPS_MD}</ReactMarkdown></div>;
      case 4: return <div className="markdown-body"><ReactMarkdown remarkPlugins={[remarkGfm]}>{IDEAS_MD}</ReactMarkdown></div>;
      default: return null;
    }
  };

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '950px', margin: '0 auto', width: '100%', padding: '2rem 0' }}>
      <div style={{ textAlign: 'center' }}>
         <h2 style={{ fontSize: '3rem', marginBottom: '1rem', fontWeight: 800, letterSpacing: '-0.02em', color: 'white' }}>
            Talk to <span style={{ background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Research.<br/>It Listens.</span>
         </h2>
         <p style={{ fontSize: '1.1rem', maxWidth: '600px', margin: '0 auto', color: 'var(--text-secondary)' }}>
            Each agent's output is traced individually so you can follow the reasoning chain.
         </p>
      </div>

      {/* Input Area */}
      <div className="glass-panel" style={{ padding: '2rem', background: 'var(--bg-glass-heavy)' }}>
         {strategy === 'rag' ? (
           <div style={{ border: '2px dashed var(--border-color)', borderRadius: '12px', padding: '3rem', textAlign: 'center', marginBottom: '1.5rem', background: 'rgba(0,0,0,0.2)' }}
                onDragOver={e => e.preventDefault()} onDrop={e => { e.preventDefault(); setFile(e.dataTransfer.files[0]); }}>
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" strokeWidth="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
              <h3 style={{ color: 'white', marginTop: '1rem' }}>Upload Document</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>Drag & drop your PDF, or click to browse.</p>
              <input type="file" id="file-upload" style={{ display: 'none' }} onChange={e => e.target.files && setFile(e.target.files[0])} />
              <label htmlFor="file-upload" className="btn-primary" style={{ padding: '0.5rem 1.5rem', cursor: 'pointer', display: 'inline-block' }}>Select File</label>
              {file && <div style={{ marginTop: '1rem', color: 'var(--success)', fontWeight: 600 }}>✓ {file.name}</div>}
           </div>
         ) : (
           <textarea value={query} onChange={e => setQuery(e.target.value)} placeholder="What do you want to research? (e.g. Agentic Systems in Cost Routing)" style={{ minHeight: '120px', fontSize: '1.1rem', width: '100%', marginBottom: '1.5rem', resize: 'vertical' }} />
         )}
         <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Pipeline</span>
              <div className="toggle-group">
                {['auto', 'cot', 'multi', 'rag'].map(s => (
                  <div key={s} className={`toggle-item ${strategy === s ? 'active' : ''}`} onClick={() => setStrategy(s)}>
                    {s === 'auto' ? '✨ Auto' : s === 'cot' ? '🧠 CoT' : s === 'multi' ? '⚙️ Multi-Agent' : '📚 RAG'}
                  </div>
                ))}
              </div>
            </div>
            <button onClick={handleSubmit} disabled={status === 'running' || (!query && !file)} className="btn-primary" style={{ padding: '1rem 2.5rem', fontSize: '1.1rem' }}>
              {status === 'running' ? 'Pipeline Active...' : 'Synthesize Research'}
            </button>
         </div>
      </div>

      {/* Running indicator */}
      {status === 'running' && visibleAgents === 0 && (
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <div className="skeleton" style={{ height: '4px', width: '100%', marginBottom: '2rem' }}></div>
          <h3 style={{ color: 'var(--accent-primary)', animation: 'pulse 2s infinite' }}>Initializing agent pipeline...</h3>
        </div>
      )}

      {/* Agent Output Cards */}
      {visibleAgents > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <h3 style={{ color: 'white', fontSize: '1.3rem', fontWeight: 700 }}>Pipeline Output</h3>
            <div style={{ flex: 1, height: '1px', background: 'var(--border-color)' }}></div>
            <div style={{ background: 'rgba(59,130,246,0.1)', padding: '0.35rem 1rem', borderRadius: '999px', fontSize: '0.85rem', color: 'var(--accent-primary)', fontWeight: 600 }}>{visibleAgents}/5 agents</div>
          </div>

          {AGENTS.slice(0, visibleAgents).map((agent, i) => (
            <div key={agent.key} className="glass-panel fade-in" style={{ padding: '1.75rem', borderLeft: `4px solid ${agent.color}` }}>
              {/* Header */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '1.4rem' }}>{agent.icon}</span>
                <h4 style={{ color: agent.color, fontSize: '1.1rem', fontWeight: 700, flex: 1 }}>{agent.label}</h4>
                <div style={{ background: `${agent.color}20`, color: agent.color, padding: '0.2rem 0.65rem', borderRadius: '999px', fontSize: '0.75rem', fontWeight: 700 }}>Agent {i + 1}</div>
              </div>
              {/* Source badge */}
              <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.25rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                <code style={{ background: 'rgba(255,255,255,0.06)', padding: '0.15rem 0.5rem', borderRadius: '4px' }}>{agent.source}</code>
                <code style={{ background: 'rgba(255,255,255,0.06)', padding: '0.15rem 0.5rem', borderRadius: '4px' }}>→ {agent.returns}</code>
              </div>
              {/* Content */}
              {renderAgentContent(i)}
            </div>
          ))}
        </div>
      )}

      {/* Post-completion: Cost + Chat + Send */}
      {status === 'completed' && (
        <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Cost Simulator */}
          <div className="glass-panel" style={{ padding: '2rem', background: 'rgba(59,130,246,0.04)', position: 'relative', overflow: 'hidden' }}>
             <div style={{ position: 'absolute', top: 0, left: 0, width: '4px', height: '100%', background: 'linear-gradient(to bottom, var(--accent-primary), var(--danger))' }}></div>
             <h4 style={{ fontSize: '1.1rem', marginBottom: '1.5rem', color: 'white' }}>AgenticOps Cost Comparison</h4>
             <div style={{ display: 'flex', gap: '1.5rem' }}>
                {[{ label: 'Cost Saved', value: '68%', color: 'var(--success)' }, { label: 'Latency', value: '4.2s', color: 'var(--accent-primary)' }, { label: 'Quality', value: '9.4/10', color: 'white' }].map(m => (
                  <div key={m.label} style={{ background: 'rgba(0,0,0,0.35)', borderRadius: '12px', padding: '1.25rem', flex: 1, textAlign: 'center', border: '1px solid rgba(255,255,255,0.05)' }}>
                     <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>{m.label}</div>
                     <div style={{ fontSize: '2.2rem', fontWeight: 800, color: m.color }}>{m.value}</div>
                  </div>
                ))}
             </div>
          </div>

          {/* Inline Chat */}
          <div className="glass-panel" style={{ padding: 0, overflow: 'hidden' }}>
            <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
              <span style={{ fontWeight: 700, color: 'white', fontSize: '0.95rem' }}>Discuss & Refine</span>
              <span style={{ marginLeft: 'auto', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Refine before sending to Implementation</span>
            </div>
            <div style={{ maxHeight: '280px', overflowY: 'auto', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {chatMessages.length === 0 && (
                <div style={{ textAlign: 'center', padding: '1.5rem 1rem', color: 'var(--text-secondary)' }}>
                  <p style={{ marginBottom: '0.75rem', fontSize: '0.9rem' }}>Ask about the outputs, refine hypotheses, or send results forward.</p>
                  <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                    {['Which gap is most novel?', 'Refine the DTRP hypothesis', 'Send to Implementation'].map(s => (
                      <button key={s} onClick={() => setChatInput(s)} style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border-color)', color: 'var(--text-secondary)', padding: '0.4rem 0.9rem', borderRadius: '999px', fontSize: '0.8rem', cursor: 'pointer' }}>{s}</button>
                    ))}
                  </div>
                </div>
              )}
              {chatMessages.map((m, i) => (
                <div key={i} style={{ alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '80%' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginBottom: '0.2rem', fontWeight: 600 }}>{m.role === 'user' ? 'You' : 'ReAssist AI'}</div>
                  <div style={{ background: m.role === 'user' ? 'var(--accent-primary)' : 'rgba(255,255,255,0.05)', padding: '0.6rem 0.9rem', borderRadius: '12px', border: m.role === 'assistant' ? '1px solid var(--border-color)' : 'none', color: 'white', fontSize: '0.9rem' }}>
                    {m.role === 'assistant' ? <div className="markdown-body"><ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown></div> : m.content}
                  </div>
                </div>
              ))}
              <div ref={chatEndRef} />
            </div>
            <div style={{ padding: '0.75rem 1.25rem', borderTop: '1px solid var(--border-color)', display: 'flex', gap: '0.5rem' }}>
              <input value={chatInput} onChange={e => setChatInput(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') handleInlineChat(); }} placeholder="Ask about gaps, refine a hypothesis..." style={{ flex: 1, background: 'rgba(15,23,42,0.8)', border: '1px solid var(--border-color)', padding: '0.6rem 0.9rem', borderRadius: '10px', color: 'white', outline: 'none' }} />
              <button onClick={handleInlineChat} style={{ background: chatInput.trim() ? 'white' : 'rgba(255,255,255,0.1)', color: chatInput.trim() ? 'black' : 'var(--text-secondary)', border: 'none', borderRadius: '10px', padding: '0 1rem', fontWeight: 700, cursor: chatInput.trim() ? 'pointer' : 'default', fontSize: '1.1rem' }}>↑</button>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <button onClick={() => onAnalysisComplete({ synthesis: SYNTHESIS_MD, gaps: GAPS_MD, ideas: IDEAS_MD })} className="btn-primary" style={{ padding: '1.25rem 3rem', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              Send to Implementation Pipeline
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
