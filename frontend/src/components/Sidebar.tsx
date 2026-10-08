"use client";
import React from 'react';
import Link from 'next/link';

export default function Sidebar({ activeTab, setActiveTab }: { activeTab: string, setActiveTab: (tab: string) => void }) {
  const navItems = [
    { id: 'pipeline', label: 'Research Pipeline', icon: '⚡' },
    { id: 'stats', label: 'AgenticOps Stats', icon: '📊' }
  ];

  return (
    <aside className="glass-panel" style={{ width: '280px', margin: '1.5rem', display: 'flex', flexDirection: 'column', overflow: 'hidden', borderRight: '1px solid var(--border-color)' }}>
      <div style={{ padding: '2rem 1.5rem', borderBottom: '1px solid rgba(0, 240, 255, 0.1)', background: 'rgba(0, 240, 255, 0.02)' }}>
        <h1 style={{ fontSize: '1.4rem', display: 'flex', alignItems: 'center', gap: '0.75rem', margin: 0, textTransform: 'uppercase', letterSpacing: '0.1em', background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', textShadow: '0 0 20px rgba(0, 240, 255, 0.4)' }}>
          <span style={{ fontSize: '1.2rem', WebkitTextFillColor: 'var(--accent-primary)', textShadow: '0 0 10px var(--accent-primary)' }}>◈</span> REASSIST
        </h1>
        <p style={{ fontSize: '0.75rem', marginTop: '0.5rem', marginBottom: 0, color: 'var(--accent-primary)', opacity: 0.8, letterSpacing: '0.05em' }}>INTELLIGENCE ENGINE v2.0</p>
      </div>

      <nav style={{ padding: '2rem 1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem', flex: 1 }}>
        {navItems.map(item => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
              padding: '1rem',
              borderRadius: '8px',
              border: '1px solid',
              borderColor: activeTab === item.id ? 'rgba(0, 240, 255, 0.4)' : 'transparent',
              background: activeTab === item.id ? 'rgba(0, 240, 255, 0.08)' : 'transparent',
              color: activeTab === item.id ? 'var(--accent-primary)' : 'var(--text-secondary)',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              textAlign: 'left',
              fontWeight: activeTab === item.id ? 600 : 400,
              boxShadow: activeTab === item.id ? '0 0 15px rgba(0, 240, 255, 0.1) inset' : 'none',
              textTransform: 'uppercase',
              fontSize: '0.85rem',
              letterSpacing: '0.05em'
            }}
            onMouseOver={(e) => {
              if (activeTab !== item.id) {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)';
                e.currentTarget.style.color = 'var(--text-primary)';
              }
            }}
            onMouseOut={(e) => {
              if (activeTab !== item.id) {
                e.currentTarget.style.background = 'transparent';
                e.currentTarget.style.color = 'var(--text-secondary)';
              }
            }}
          >
            <span style={{ fontSize: '1.2rem', filter: activeTab === item.id ? 'drop-shadow(0 0 5px var(--accent-primary))' : 'none' }}>{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>

      <div style={{ padding: '1.5rem', borderTop: '1px solid rgba(0, 240, 255, 0.1)', fontSize: '0.75rem', color: 'var(--text-secondary)', textAlign: 'center', fontFamily: 'JetBrains Mono, monospace', opacity: 0.6 }}>
        SYSTEM: ONLINE<br/>
        NODE: AGENTICOPS
      </div>
    </aside>
  );
}
