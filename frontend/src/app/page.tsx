"use client";
import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import TopNav from '@/components/TopNav';
import IdeationTab from '@/components/IdeationTab';
import DiscoveryTab from '@/components/DiscoveryTab';
import ImplementationTab from '@/components/ImplementationTab';
import SandboxTab from '@/components/SandboxTab';

// Session Types
type Message = { role: 'user' | 'assistant', content: string };
type ProjectSession = {
  id: string;
  name: string;
  activeStage: 'ideation' | 'discovery' | 'implementation';
  query: string;
  pipelineData: any;
  messages: Message[];
}

export default function Home() {
  const [sessions, setSessions] = useState<ProjectSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string>('');
  
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editingName, setEditingName] = useState('');

  // App Routes: 'session' | 'global_sandbox'
  const [viewMode, setViewMode] = useState<'session' | 'global_sandbox'>('session');

  const [chatInput, setChatInput] = useState('');

  // Load from LocalStorage
  useEffect(() => {
    const saved = localStorage.getItem('reassist_projects');
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

  // Sync to LocalStorage
  useEffect(() => {
    if (sessions.length > 0) {
      localStorage.setItem('reassist_projects', JSON.stringify(sessions));
    }
  }, [sessions]);

  const createNewSession = () => {
    const newId = Date.now().toString();
    const newSession: ProjectSession = {
      id: newId,
      name: `New Project`,
      activeStage: 'ideation',
      query: '',
      pipelineData: null,
      messages: [{ role: 'assistant', content: 'Hello! I am ReAssist. I can help you ideate topics, run deep literature synthesis, and guide you through implementation. What are we researching today?' }]
    };
    setSessions(prev => [newSession, ...prev]);
    setActiveSessionId(newId);
    setViewMode('session');
    setEditingSessionId(null);
  };

  const updateSession = (partialUpdate: Partial<ProjectSession>) => {
    setSessions(prev => prev.map(s => s.id === activeSessionId ? { ...s, ...partialUpdate } : s));
  };

  const activeSession = sessions.find(s => s.id === activeSessionId) || sessions[0];

  // Pipeline Flow Handlers
  const handleSelectTopic = (topic: string) => {
    updateSession({ query: topic, activeStage: 'discovery' });
  };

  const handleAnalysisComplete = (data: any) => {
    let newName = activeSession.name;
    // Auto-rename like GPT if it's still named "New Project"
    if (newName === 'New Project' && activeSession.query) {
      const words = activeSession.query.split(' ').slice(0, 4).join(' ');
      newName = words + (activeSession.query.split(' ').length > 4 ? '...' : '');
    }
    updateSession({ pipelineData: data, activeStage: 'implementation', name: newName });
  };

  // Chat Handler
  const sendChatMessage = (msg: string) => {
    if (!msg.trim() || !activeSession) return;
    
    const newMessages = [...activeSession.messages, { role: 'user', content: msg } as Message];
    updateSession({ messages: newMessages });

    // Contextual Mock Responses
    setTimeout(() => {
       let reply = "I can certainly help you adapt those results! Is there a specific architectural detail you'd like me to expand on?";
       if (msg.toLowerCase().includes('vue')) {
         reply = "Ah, you'd prefer **Vue.js** over React! No problem. I recommend using Nuxt 3 to replace the Next.js frontend requirements. Would you like me to rewrite the Implementation Guide for Nuxt?";
       } else if (activeSession.activeStage === 'implementation') {
         reply = "Looking at the generated Implementation Plan, we recommended FastAPI and React. I can modify this stack or write out the exact boilerplate code for any given section. What do you need?";
       }
       
       updateSession({ 
         messages: [...newMessages, { role: 'assistant', content: reply }] 
       });
    }, 1500);
  };

  const handleSendChat = () => {
    sendChatMessage(chatInput);
    setChatInput('');
  };

  const saveRename = (id: string) => {
    if (editingName.trim()) {
      setSessions(prev => prev.map(s => s.id === id ? { ...s, name: editingName.trim() } : s));
    }
    setEditingSessionId(null);
  };

  if (!activeSession) return null;

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', background: 'var(--bg-main)', overflow: 'hidden' }}>
      
      {/* LEFT SIDEBAR */}
      <div style={{ width: '260px', background: 'rgba(3,7,18,0.9)', borderRight: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', padding: '1rem', flexShrink: 0, zIndex: 50 }}>
         <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem', padding: '0.5rem' }}>
            <div style={{ width: '24px', height: '24px', background: 'var(--accent-gradient)', borderRadius: '6px' }}></div>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 800, color: 'white', letterSpacing: '-0.02em' }}>ReAssist</h2>
         </div>

         <button onClick={createNewSession} className="btn-primary" style={{ width: '100%', marginBottom: '1.5rem', justifyContent: 'center' }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
            New Project
         </button>

         <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem', paddingLeft: '0.5rem' }}>History</div>
         <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
            {sessions.map(s => (
              <div 
                key={s.id}
                onClick={() => { 
                  if (editingSessionId !== s.id) {
                    setActiveSessionId(s.id); 
                    setViewMode('session'); 
                  }
                }}
                onDoubleClick={() => {
                  setEditingSessionId(s.id);
                  setEditingName(s.name);
                }}
                style={{ 
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  padding: '0.6rem 0.75rem', borderRadius: '8px', cursor: 'pointer', fontSize: '0.9rem', color: activeSessionId === s.id && viewMode === 'session' ? 'white' : 'var(--text-secondary)',
                  background: activeSessionId === s.id && viewMode === 'session' ? 'rgba(59,130,246,0.1)' : 'transparent',
                  transition: 'all 0.2s'
                }}
                onMouseOver={e => { if (editingSessionId !== s.id) e.currentTarget.style.background = 'rgba(255,255,255,0.05)' }}
                onMouseOut={e => { if (editingSessionId !== s.id) e.currentTarget.style.background = activeSessionId === s.id && viewMode === 'session' ? 'rgba(59,130,246,0.1)' : 'transparent' }}
              >
                {editingSessionId === s.id ? (
                  <input 
                    autoFocus
                    value={editingName}
                    onChange={e => setEditingName(e.target.value)}
                    onBlur={() => saveRename(s.id)}
                    onKeyDown={e => { if (e.key === 'Enter') saveRename(s.id); }}
                    style={{ background: 'transparent', border: 'none', color: 'white', width: '100%', outline: 'none', padding: 0 }}
                  />
                ) : (
                  <>
                    <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{s.name}</span>
                    {activeSessionId === s.id && viewMode === 'session' && (
                      <svg onClick={(e) => { e.stopPropagation(); setEditingSessionId(s.id); setEditingName(s.name); }} width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, opacity: 0.5, cursor: 'pointer' }}><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>
                    )}
                  </>
                )}
              </div>
            ))}
         </div>

         <div style={{ marginTop: 'auto', borderTop: '1px solid var(--border-color)', paddingTop: '1rem' }}>
            <div 
              onClick={() => setViewMode('global_sandbox')}
              style={{ padding: '0.75rem', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.75rem', color: viewMode === 'global_sandbox' ? 'white' : 'var(--text-secondary)', background: viewMode === 'global_sandbox' ? 'rgba(59,130,246,0.1)' : 'transparent' }}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>
              Agentic Sandbox
            </div>
         </div>
      </div>

      {/* MAIN CONTENT AREA */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', position: 'relative', overflowY: 'auto' }}>
         {viewMode === 'session' && (
           <div style={{ position: 'sticky', top: 0, zIndex: 40, background: 'rgba(3,7,18,0.7)', backdropFilter: 'blur(12px)', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'center' }}>
             <div style={{ display: 'flex', gap: '3rem' }}>
               {[
                 { id: 'ideation', label: '1. Ideation' },
                 { id: 'discovery', label: '2. Synthesis' },
                 { id: 'implementation', label: '3. Implementation' }
               ].map(t => (
                  <button 
                    key={t.id}
                    onClick={() => updateSession({ activeStage: t.id as any })}
                    style={{ 
                      background: 'transparent', border: 'none', padding: '1.25rem 0', 
                      color: activeSession.activeStage === t.id ? 'white' : 'var(--text-secondary)', 
                      fontWeight: activeSession.activeStage === t.id ? 600 : 500, 
                      borderBottom: `2px solid ${activeSession.activeStage === t.id ? 'var(--accent-primary)' : 'transparent'}`,
                      cursor: 'pointer', transition: 'all 0.2s', fontSize: '0.95rem'
                    }}
                  >
                    {t.label}
                  </button>
               ))}
             </div>
           </div>
         )}
         
         <div style={{ padding: '2rem', flex: 1 }}>
            {viewMode === 'global_sandbox' ? (
               <SandboxTab />
            ) : (
               <>
                 {activeSession.activeStage === 'ideation' && <IdeationTab onSelectTopic={handleSelectTopic} />}
                 {activeSession.activeStage === 'discovery' && <DiscoveryTab initialQuery={activeSession.query} onAnalysisComplete={handleAnalysisComplete} />}
                 {activeSession.activeStage === 'implementation' && <ImplementationTab resultData={activeSession.pipelineData} onInlineChat={sendChatMessage} />}
               </>
            )}
         </div>
      </div>

      {/* RIGHT CHAT PANE (Claude Artifact Style) */}
      {viewMode === 'session' && (
        <div style={{ width: '400px', display: 'flex', flexDirection: 'column', borderLeft: '1px solid var(--border-color)', background: 'rgba(3,7,18,0.4)', flexShrink: 0 }}>
           <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ fontWeight: 600, color: 'white', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                 <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                 Copilot
              </div>
              {/* Added TopNav triggers here for space efficiency */}
              <TopNav />
           </div>

           <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {activeSession.messages.map((m, i) => (
                 <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', alignItems: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
                   <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase' }}>{m.role === 'user' ? 'You' : 'ReAssist AI'}</div>
                   <div style={{ maxWidth: '90%', background: m.role === 'user' ? 'var(--accent-primary)' : 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: '12px', border: m.role === 'assistant' ? '1px solid var(--border-color)' : 'none', color: m.role === 'user' ? 'white' : 'var(--text-primary)' }}>
                     {m.role === 'assistant' ? (
                       <div className="markdown-body" style={{ fontSize: '0.95rem' }}><ReactMarkdown>{m.content}</ReactMarkdown></div>
                     ) : (
                       <div style={{ fontSize: '0.95rem' }}>{m.content}</div>
                     )}
                   </div>
                 </div>
              ))}
           </div>

           <div style={{ padding: '1.5rem', borderTop: '1px solid var(--border-color)', background: 'var(--bg-main)' }}>
              <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '0.5rem', display: 'flex', flexDirection: 'column' }}>
                 <textarea 
                   value={chatInput}
                   onChange={e => setChatInput(e.target.value)}
                   onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSendChat(); } }}
                   placeholder="Ask about the implementation stack..."
                   style={{ background: 'transparent', border: 'none', color: 'white', padding: '0.5rem', minHeight: '60px', resize: 'none', outline: 'none' }}
                 />
                 <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0 0.5rem 0.5rem 0.5rem' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Shift+Enter for newline</div>
                    <button onClick={handleSendChat} style={{ background: chatInput.trim() ? 'white' : 'rgba(255,255,255,0.1)', color: chatInput.trim() ? 'black' : 'var(--text-secondary)', border: 'none', borderRadius: '8px', padding: '6px 16px', fontWeight: 600, cursor: chatInput.trim() ? 'pointer' : 'default', transition: 'all 0.2s' }}>
                      ↑
                    </button>
                 </div>
              </div>
           </div>
        </div>
      )}
    </div>
  );
}
