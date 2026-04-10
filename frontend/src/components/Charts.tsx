"use client";
import React, { useEffect, useState } from 'react';

export default function Charts() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        const res = await fetch('http://localhost:8000/stats/router');
        if (res.ok) {
          const data = await res.json();
          setStats(data);
        }
      } catch (err) {
        console.error("Failed to load stats", err);
      } finally {
        setLoading(false);
      }
    }
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="glass-panel" style={{ padding: '2rem' }}>
        <div className="skeleton" style={{ height: '300px', width: '100%', borderRadius: '12px' }}></div>
      </div>
    );
  }

  const {
    total_queries = 0,
    cot_routed_count = 0,
    multi_agent_routed_count = 0,
    estimated_total_cost_usd = 0,
    simulated_always_multi_agent_cost = 0,
    total_savings_usd = 0
  } = stats || {};

  // Pure SVG/CSS visualizations
  const maxCost = Math.max(simulated_always_multi_agent_cost, estimated_total_cost_usd, 0.01);
  const agenticCostPct = (estimated_total_cost_usd / maxCost) * 100;
  const legacyCostPct = (simulated_always_multi_agent_cost / maxCost) * 100;

  return (
    <div style={{ padding: '1rem' }}>
      <header style={{ marginBottom: '2.5rem' }}>
        <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem', background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', display: 'inline-block' }}>
          AgenticOps Intelligence
        </h2>
        <p>Routing analytics and dynamic cost savings achieved by the LLM routing system.</p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2.5rem' }}>
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '1px' }}>Total Savings</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--success)' }}>${total_savings_usd.toFixed(4)}</div>
        </div>
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '1px' }}>Queries Routed</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 700 }}>{total_queries}</div>
        </div>
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '1px' }}>CoT Paths Chosen</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--accent-primary)' }}>{cot_routed_count}</div>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '2rem' }}>
        <h3 style={{ marginBottom: '2rem', fontSize: '1.25rem' }}>Cost Comparison (Legacy vs AgenticOps)</h3>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* Bar 1 */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontWeight: 500, color: 'var(--text-secondary)' }}>Legacy (Always Multi-Agent)</span>
              <span style={{ fontWeight: 600 }}>${simulated_always_multi_agent_cost.toFixed(4)}</span>
            </div>
            <div style={{ width: '100%', height: '24px', background: 'var(--bg-secondary)', borderRadius: '12px', overflow: 'hidden' }}>
              <div style={{ width: `${legacyCostPct}%`, height: '100%', background: 'var(--danger)', borderRadius: '12px', transition: 'width 1s ease-in-out' }}></div>
            </div>
          </div>
          
          {/* Bar 2 */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontWeight: 500, color: 'var(--accent-primary)' }}>AgenticOps Router</span>
              <span style={{ fontWeight: 600, color: 'var(--success)' }}>${estimated_total_cost_usd.toFixed(4)}</span>
            </div>
            <div style={{ width: '100%', height: '24px', background: 'var(--bg-secondary)', borderRadius: '12px', overflow: 'hidden' }}>
              <div style={{ width: `${agenticCostPct}%`, height: '100%', background: 'var(--success)', borderRadius: '12px', transition: 'width 1s ease-in-out' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
