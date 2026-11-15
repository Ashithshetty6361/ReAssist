/**
 * ============================================================================
 * FRONTEND SHOWCASE: OBSERVABILITY TELEMETRY CHARTS
 * ============================================================================
 * What to show in an interview:
 * 1. Demonstrates the live Router Observability UI in the frontend.
 * 2. Fetches routing telemetry from /stats/router.
 * 3. Renders pure CSS/SVG cost comparisons:
 *    - Legacy (Always Multi-Agent) vs AgenticOps Dynamic Router
 * 4. Displays real-time cost savings USD and path breakdown.
 *
 * ORIGINAL SOURCE FILE:
 *   - frontend/src/components/Charts.tsx
 * ============================================================================
 */

"use client";
import React, { useEffect, useState } from 'react';
import { apiUrl } from '@/lib/api';

export default function ObservabilityChartsShowcase() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        const res = await fetch(apiUrl('/stats/router'));
        if (res.ok) {
          const data = await res.json();
          setStats(data);
        }
      } catch (err) {
        console.error("Failed to load telemetry stats", err);
      } finally {
        setLoading(false);
      }
    }
    fetchStats();
  }, []);

  if (loading) return <div>Loading Observability Telemetry...</div>;

  const {
    total_queries = 0,
    cot_routed_count = 0,
    estimated_total_cost_usd = 0,
    simulated_always_multi_agent_cost = 0,
    total_savings_usd = 0
  } = stats || {};

  return (
    <div className="telemetry-dashboard">
      <h3>AgenticOps Routing Analytics</h3>
      
      {/* KPI Stats Cards */}
      <div className="stats-grid">
        <div className="card">
          <span>Total Savings Achieved</span>
          <strong>${total_savings_usd.toFixed(4)}</strong>
        </div>
        <div className="card">
          <span>Total Queries Processed</span>
          <strong>{total_queries}</strong>
        </div>
        <div className="card">
          <span>Fast CoT Paths Selected</span>
          <strong>{cot_routed_count}</strong>
        </div>
      </div>

      {/* Visual Cost Comparison Bar */}
      <div className="comparison-bar">
        <h4>Cost Comparison (Legacy vs AgenticOps Router)</h4>
        <div className="bar-row">
          <span>Always Multi-Agent: ${simulated_always_multi_agent_cost.toFixed(4)}</span>
        </div>
        <div className="bar-row">
          <span>AgenticOps Router: ${estimated_total_cost_usd.toFixed(4)}</span>
        </div>
      </div>
    </div>
  );
}

