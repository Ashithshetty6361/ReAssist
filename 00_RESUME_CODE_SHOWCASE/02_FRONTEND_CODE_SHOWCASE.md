# 🎨 ReAssist — Frontend Architecture & Code Walkthrough Guide

> **Core Technology Stack:** Next.js 16 (App Router), React 19, TypeScript, TailwindCSS, CSS Variables Glassmorphic Tokens, Turbopack  
> **Frontend Root Folder:** [`frontend/`](file:///c:/Users/shett/MIT_BTech/ReAssist_Project/frontend/)  
> **Standalone Run Script:** Double-click [`start_frontend.bat`](file:///c:/Users/shett/MIT_BTech/ReAssist_Project/start_frontend.bat) (Runs on `http://localhost:3000`)

---

## 📂 Frontend Directory Structure

```
frontend/
├── package.json               <── Dependencies (Next 16, React 19, Lucide, KaTeX)
├── tsconfig.json              <── Strict TypeScript configuration
├── next.config.ts             <── Next.js Turbopack compiler config
├── .env.local                 <── NEXT_PUBLIC_API_URL (http://localhost:8000)
│
└── src/
    ├── app/                   <── Next.js App Router Core
    │   ├── layout.tsx         <── Root Layout & JetBrains Mono Font Loading
    │   ├── page.tsx           <── Single-Page Dashboard & Strategy Controller
    │   └── globals.css        <── Cyber/Dark Glassmorphic Design System
    │
    ├── components/            <── Modular UI Components
    │   ├── SandboxTab.tsx     <── 🧪 AgenticOps Sandbox & Parallel Benchmark
    │   ├── Charts.tsx         <── 📊 Routing Telemetry & SVG Cost Comparison Bars
    │   ├── DiscoveryTab.tsx   <── 📚 arXiv Literature Cards & Relevance Badges
    │   ├── IdeationTab.tsx    <── 💡 Research Gaps & Novel Hypothesis Cards
    │   ├── ImplementationTab.tsx <── 🛠️ Phased Execution Milestones & Code Steps
    │   ├── ChatPanel.tsx      <── 💬 Floating AI Intelligence Assistant
    │   ├── Dashboard.tsx      <── 📈 Top Metrics KPI Bar & Run Status
    │   ├── Sidebar.tsx        <── 📁 Workspace Selector & Document Ingestion
    │   └── TopNav.tsx         <── 🧭 Navigation Header & Model Status Indicator
    │
    └── lib/
        └── api.ts             <── 🌐 Dynamic API URL Resolver (Port 8000 / 8001 / Cloud)
```

---

## 🎯 Key Frontend Subsystems: What to Show in an Interview

### 1. 🧪 The AgenticOps Sandbox & Demo Tab
* **File:** [`frontend/src/components/SandboxTab.tsx`](file:///c:/Users/shett/MIT_BTech/ReAssist_Project/frontend/src/components/SandboxTab.tsx#L12-L60)
* **What to Highlight:**
  * **Asynchronous Non-Blocking Dispatch:** Calls `apiUrl('/simulate_comparison')` using `fetch` with `POST`.
  * **Resilient Polling Engine:** Uses `setInterval` (polling every 2000ms) on `/executions/${jobId}` to check for completion without freezing the browser thread or causing HTTP socket timeouts.
  * **Parallel Results Matrix:** Once completed, renders a side-by-side comparison of **Coverage**, **Specificity**, and **Actionability** scores between the **CoT baseline** and the **Multi-Agent pipeline**.

---

### 2. 📊 Real-Time Observability & Cost Savings Charts
* **File:** [`frontend/src/components/Charts.tsx`](file:///c:/Users/shett/MIT_BTech/ReAssist_Project/frontend/src/components/Charts.tsx#L9-L98)
* **What to Highlight:**
  * Fetches live telemetry from the backend router via `apiUrl('/stats/router')`.
  * **Pure SVG/CSS Visualizations:** Zero heavy external charting libraries. Renders animated proportional bar charts comparing:
    * **Legacy Costs (Always Multi-Agent)**: Red progress bar showing simulated costs if all queries triggered 11 agents.
    * **AgenticOps Router Costs**: Green progress bar showing the actual minimized cost achieved by dynamic routing.
  * Shows aggregate metrics: **Total Savings in USD**, **Queries Routed**, and **Fast CoT Paths Chosen**.

---

### 3. 🧭 Central Strategy Controller & Tab Architecture
* **File:** [`frontend/src/app/page.tsx`](file:///c:/Users/shett/MIT_BTech/ReAssist_Project/frontend/src/app/page.tsx#L45-L120)
* **What to Highlight:**
  * Acts as the main mission control for the user.
  * Manages active strategy states:
    * `discovery`: Literature retrieval and paper cards.
    * `ideation`: Research gaps and novel hypothesis cards.
    * `implementation`: Phased execution roadmap.
    * `sandbox`: Live AgenticOps telemetry stress-testing.
    * `rag`: Private workspace vector ingestion and retrieval.
  * Dynamically queries the backend health probe to display the active model (`gpt-4o-mini`, `llama3.1:8b`, or `claude-3-5-sonnet`) directly in the UI.

---

### 4. 🌐 Dynamic API Configuration
* **File:** [`frontend/src/lib/api.ts`](file:///c:/Users/shett/MIT_BTech/ReAssist_Project/frontend/src/lib/api.ts#L6-L12)
* **What to Highlight:**
  * Reads `NEXT_PUBLIC_API_URL` from `.env.local` with automatic fallback to `http://localhost:8000`.
  * Sanitizes trailing slashes automatically via regex `.replace(/\/$/, '')`, preventing invalid double-slash URLs like `http://localhost:8000//simulate_comparison`.

---

### 5. 💎 Design System & Glassmorphic CSS Tokens
* **File:** [`frontend/src/app/globals.css`](file:///c:/Users/shett/MIT_BTech/ReAssist_Project/frontend/src/app/globals.css#L1-L60)
* **What to Highlight:**
  * Custom dark cybernetic theme built using CSS variables (`--bg-primary: #0a0c10`, `--accent-primary: #00f0ff`, `--bg-glass-heavy: rgba(16, 20, 28, 0.8)`).
  * Monospace typography using **JetBrains Mono** for academic research and code display.
  * Subtle backdrop blur (`backdrop-filter: blur(16px)`) and glowing status animations.

