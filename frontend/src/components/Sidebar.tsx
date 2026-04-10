"use client";
import React from 'react';
import Link from 'next/link';

export default function Sidebar({ activeTab, setActiveTab }: { activeTab: string, setActiveTab: (tab: string) => void }) {
  const navItems = [
    { id: 'pipeline', label: 'Research Pipeline', icon: '🔬' },
    { id: 'stats', label: 'AgenticOps Stats', icon: '📊' }
  ];

  return (
    <aside className="glass-panel" style={{ width: '280px', margin: '1rem', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <div style={{ padding: '2rem 1.5rem', borderBottom: '1px solid var(--border-color)' }}>
        <h1 style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.75rem', margin: 0, background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          <span style={{ fontSize: '1.5rem', WebkitTextFillColor: 'initial' }}>🌌</span> ReAssist
        </h1>
        <p style={{ fontSize: '0.85rem', marginTop: '0.5rem', marginBottom: 0 }}>Research Intelligence Engine</p>
      </div>

      <nav style={{ padding: '1.5rem 1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', flex: 1 }}>
        {navItems.map(item => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.875rem 1rem',
              borderRadius: '8px',
              border: 'none',
              background: activeTab === item.id ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
              color: activeTab === item.id ? 'var(--text-primary)' : 'var(--text-secondary)',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              textAlign: 'left',
              fontWeight: activeTab === item.id ? 600 : 400,
              borderLeft: activeTab === item.id ? '3px solid var(--accent-primary)' : '3px solid transparent'
            }}
          >
            <span style={{ fontSize: '1.25rem' }}>{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>

      <div style={{ padding: '1.5rem', borderTop: '1px solid var(--border-color)', fontSize: '0.85rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
        Built with AgenticOps
      </div>
    </aside>
  );
}
