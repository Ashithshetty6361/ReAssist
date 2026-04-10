"use client";

import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

type Message = { role: 'user' | 'assistant', content: string };
type Session = { id: string, name: string, messages: Message[] };

export default function ChatPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string>('');
  const [input, setInput] = useState('');
  const [showHistory, setShowHistory] = useState(false);

  // Load from LocalStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('reassist_chat_sessions');
    if (saved) {
      const parsed = JSON.parse(saved);
      if (parsed.length > 0) {
        setSessions(parsed);
        setActiveSessionId(parsed[0].id);
      } else {
        createNewSession();
      }
    } else {
      createNewSession();
    }
  }, []);

  // Save to LocalStorage on sessions update
  useEffect(() => {
    if (sessions.length > 0) {
      localStorage.setItem('reassist_chat_sessions', JSON.stringify(sessions));
    }
  }, [sessions]);

  const createNewSession = () => {
    const newId = Date.now().toString();
    const newSession: Session = {
      id: newId,
      name: `Research Chat ${new Date().toLocaleDateString()}`,
      messages: [{ role: 'assistant', content: 'Hi there! I am connected to your RAG pipeline. Ask me anything about your generated synthesis!' }]
    };
    setSessions(prev => [newSession, ...prev]);
    setActiveSessionId(newId);
    setShowHistory(false);
  };

  const activeMessages = sessions.find(s => s.id === activeSessionId)?.messages || [];

  const handleSend = () => {
    if (!input.trim()) return;
    
    setSessions(prev => prev.map(s => {
      if (s.id === activeSessionId) {
        return { ...s, messages: [...s.messages, { role: 'user', content: input }] };
      }
      return s;
    }));
    setInput('');

    // Mock API Response mapped to local storage
    setTimeout(() => {
       setSessions(prev => prev.map(s => {
         if (s.id === activeSessionId) {
           return { ...s, messages: [...s.messages, { role: 'assistant', content: 'Based on our strict localized context, the AgenticOps router provides exactly 68% savings compared to traditional CoT methods. Anything else?' }] };
         }
         return s;
       }));
    }, 1500);
  };

  return (
    <>
      <button 
        onClick={() => setIsOpen(!isOpen)}
        style={{ position: 'fixed', bottom: '2rem', right: '2rem', width: '60px', height: '60px', borderRadius: '50%', background: 'var(--accent-gradient)', color: 'white', border: 'none', boxShadow: '0 8px 24px rgba(59,130,246,0.5)', zIndex: 90, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', transform: isOpen ? 'scale(0)' : 'scale(1)', transition: 'transform 0.3s ease' }}
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
      </button>

      {isOpen && (
        <div className="glass-panel fade-in" style={{ position: 'fixed', bottom: '2rem', right: '2rem', width: '400px', height: '650px', display: 'flex', flexDirection: 'column', zIndex: 90, overflow: 'hidden', boxShadow: '0 12px 48px rgba(0,0,0,0.8), 0 0 0 1px var(--border-color)' }}>
          <div style={{ padding: '1rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(255,255,255,0.02)' }}>
             <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
               <button onClick={() => setShowHistory(!showHistory)} style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: '4px' }}>
                 <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
               </button>
               <h3 style={{ fontSize: '1.1rem', background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                 ReAssist Intelligence
               </h3>
             </div>
             <button onClick={() => setIsOpen(false)} style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '1.2rem' }}>✕</button>
          </div>

          <div style={{ position: 'relative', flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
             
             {/* History Sidebar Drawer */}
             {showHistory && (
               <div className="fade-in" style={{ position: 'absolute', top: 0, left: 0, bottom: 0, width: '250px', background: 'rgba(3,7,18,0.95)', backdropFilter: 'blur(10px)', borderRight: '1px solid var(--border-color)', zIndex: 10, display: 'flex', flexDirection: 'column' }}>
                  <div style={{ padding: '1rem', borderBottom: '1px solid var(--border-color)' }}>
                    <button onClick={createNewSession} className="btn-primary" style={{ width: '100%', fontSize: '0.9rem', padding: '0.5rem' }}>+ New Session</button>
                  </div>
                  <div style={{ overflowY: 'auto', flex: 1, padding: '0.5rem' }}>
                    {sessions.map(s => (
                      <div 
                        key={s.id} 
                        onClick={() => { setActiveSessionId(s.id); setShowHistory(false); }}
                        style={{ padding: '0.75rem', borderRadius: '8px', cursor: 'pointer', marginBottom: '4px', background: activeSessionId === s.id ? 'rgba(59,130,246,0.1)' : 'transparent', color: activeSessionId === s.id ? 'white' : 'var(--text-secondary)', fontSize: '0.9rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}
                      >
                        {s.name}
                      </div>
                    ))}
                  </div>
               </div>
             )}

             {/* Main Chat Flow */}
             <div style={{ flex: 1, overflowY: 'auto', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
               {activeMessages.map((m, i) => (
                  <div key={i} style={{ alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '85%', background: m.role === 'user' ? 'var(--accent-primary)' : 'rgba(255,255,255,0.05)', padding: '0.75rem 1rem', borderRadius: '12px', borderBottomRightRadius: m.role === 'user' ? '0' : '12px', borderBottomLeftRadius: m.role === 'assistant' ? '0' : '12px', border: m.role === 'assistant' ? '1px solid var(--border-color)' : 'none' }}>
                    {m.role === 'assistant' ? (
                      <div className="markdown-body" style={{ fontSize: '0.9rem', color: 'var(--text-primary)' }}><ReactMarkdown>{m.content}</ReactMarkdown></div>
                    ) : (
                      <div style={{ fontSize: '0.9rem', color: 'white' }}>{m.content}</div>
                    )}
                  </div>
               ))}
             </div>
          </div>

          <div style={{ padding: '1rem', borderTop: '1px solid var(--border-color)', background: 'rgba(3,7,18,0.8)', display: 'flex', gap: '0.5rem' }}>
            <input 
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSend()}
              placeholder="Ask a question..."
              style={{ background: 'rgba(15,23,42,0.8)', border: '1px solid var(--border-color)', padding: '0.75rem', borderRadius: '12px', color: 'white', flex: 1, outline: 'none' }}
            />
            <button onClick={handleSend} style={{ background: 'var(--accent-gradient)', color: 'white', border: 'none', borderRadius: '12px', padding: '0 1rem', cursor: 'pointer', fontWeight: 600 }}>
              Send
            </button>
          </div>
        </div>
      )}
    </>
  );
}
