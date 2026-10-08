"use client";
import { useState } from 'react';
import { apiUrl } from '@/lib/api';

export default function IdeationTab({ onSelectTopic }: { onSelectTopic: (topic: string, file?: File | null, strategy?: string) => void }) {
  const [field, setField] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [inputType, setInputType] = useState<'text' | 'file'>('text');
  const [loading, setLoading] = useState(false);
  const [topics, setTopics] = useState<string[]>([]);
  
  const handleIdeate = async () => {
    if (!field) return;
    setLoading(true);
    try {
      const res = await fetch(apiUrl('/ideate'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ field })
      });
      const data = await res.json();
      if (data.success && data.topics) {
        setTopics(data.topics);
      } else {
        setTopics(["Error generating topics - please try again."]);
      }
    } catch (e) {
      console.error("Ideation failed", e);
      setTopics(["Network error - please ensure backend is running."]);
    }
    setLoading(false);
  };

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '3rem', maxWidth: '850px', margin: '0 auto', width: '100%', padding: '2rem 0' }}>
      <div style={{ textAlign: 'center' }}>
         <h2 style={{ fontSize: '3.5rem', marginBottom: '1rem', fontWeight: 800, letterSpacing: '-0.03em', textTransform: 'uppercase', color: 'white' }}>
            Concept <span style={{ background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', filter: 'drop-shadow(0 0 10px rgba(157,78,221,0.4))' }}>Generator</span>
         </h2>
         <p style={{ fontSize: '1.1rem', maxWidth: '600px', margin: '0 auto', color: 'var(--text-secondary)', fontFamily: 'JetBrains Mono, monospace' }}>
            &gt; Enter a broad scientific domain. System will synthesize novel research vectors.
         </p>
      </div>

      <div className="glass-panel" style={{ padding: '2.5rem', background: 'var(--bg-glass-heavy)' }}>
         <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', justifyContent: 'center' }}>
            <button onClick={() => setInputType('text')} className={`btn-primary`} style={{ background: inputType === 'text' ? 'var(--accent-primary)' : 'rgba(255,255,255,0.05)', color: inputType === 'text' ? '#000' : 'white', padding: '0.5rem 1.5rem' }}>Text Prompt</button>
            <button onClick={() => setInputType('file')} className={`btn-primary`} style={{ background: inputType === 'file' ? 'var(--accent-primary)' : 'rgba(255,255,255,0.05)', color: inputType === 'file' ? '#000' : 'white', padding: '0.5rem 1.5rem' }}>RAG Upload</button>
         </div>

         {inputType === 'text' ? (
           <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
             <input 
               value={field}
               onChange={e => setField(e.target.value)}
               placeholder="&gt; Target domain (e.g. Quantum Computing)..." 
               style={{ flex: 1, padding: '1.25rem', fontSize: '1.1rem', background: 'rgba(0,0,0,0.6)', border: '1px solid var(--border-color)', borderRadius: '8px', fontFamily: 'JetBrains Mono, monospace', color: 'var(--accent-primary)' }}
               onKeyDown={e => e.key === 'Enter' && handleIdeate()}
             />
             <button onClick={handleIdeate} disabled={loading} className="btn-primary" style={{ padding: '0 2.5rem', height: '62px' }}>
               {loading ? 'GENERATING...' : 'EXECUTE'}
             </button>
           </div>
         ) : (
           <div style={{ border: '2px dashed var(--border-color)', borderRadius: '8px', padding: '3rem', textAlign: 'center', background: 'rgba(0,0,0,0.4)', transition: 'all 0.3s', cursor: 'pointer' }}>
              <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>📄</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 600, color: 'white', marginBottom: '0.5rem' }}>Upload Schematic</div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', fontFamily: 'JetBrains Mono, monospace' }}>&gt; Drag &amp; drop PDF for immediate RAG pipeline execution</div>
              <input type="file" accept=".pdf" onChange={e => {
                 if (e.target.files && e.target.files[0]) {
                    setFile(e.target.files[0]);
                    onSelectTopic(e.target.files[0].name, e.target.files[0], 'rag');
                 }
              }} style={{ display: 'none' }} id="ideation-file-upload" />
              <label htmlFor="ideation-file-upload" className="btn-primary" style={{ display: 'inline-block', marginTop: '1.5rem', padding: '0.75rem 2rem' }}>BROWSE PDF</label>
           </div>
         )}
      </div>

      {loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
           {[1,2,3].map(i => <div key={i} className="skeleton" style={{ height: '140px', background: 'linear-gradient(90deg, rgba(0,0,0,0.5) 25%, rgba(157,78,221,0.1) 50%, rgba(0,0,0,0.5) 75%)' }}></div>)}
        </div>
      )}

      {topics.length > 0 && (
         <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
           <h3 style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', fontWeight: 600, letterSpacing: '0.1em', textTransform: 'uppercase', marginTop: '1rem', fontFamily: 'JetBrains Mono, monospace' }}>&gt; Generated Research Vectors</h3>
           {topics.map((rawTopic, i) => {
              const cleanTopic = rawTopic.replace(/^\[\s*["']?/, '').replace(/["']?\s*\]$/, '').replace(/^["']/, '').replace(/["'],?$/, '').trim();
              const parts = cleanTopic.split(' - ');
              const title = parts[0]?.trim() || cleanTopic;
              const desc = parts[1]?.trim() || '';
              return (
                <div 
                  key={i} 
                  onClick={() => onSelectTopic(title)}
                  className="glass-panel" 
                  style={{ padding: '2rem', cursor: 'pointer', transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)', borderLeft: '4px solid var(--accent-purple)', position: 'relative', overflow: 'hidden', background: 'rgba(5,5,8,0.7)' }}
                  onMouseOver={e => {
                    e.currentTarget.style.transform = 'translateY(-5px)';
                    e.currentTarget.style.borderColor = 'var(--accent-primary)';
                    e.currentTarget.style.boxShadow = '0 10px 30px rgba(0, 240, 255, 0.15)';
                  }}
                  onMouseOut={e => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.borderColor = 'var(--accent-purple)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                   <div style={{ fontSize: '1.35rem', fontWeight: 700, color: 'white', marginBottom: '0.75rem', letterSpacing: '0.02em' }}>{title}</div>
                   <div style={{ color: 'var(--text-secondary)', lineHeight: 1.6, fontSize: '1rem' }}>{desc}</div>
                   
                   <div style={{ marginTop: '2rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                     <span style={{ color: 'var(--accent-primary)', fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>INITIATE DISCOVERY</span>
                     <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
                   </div>
                </div>
              );
           })}
         </div>
      )}
    </div>
  );
}
