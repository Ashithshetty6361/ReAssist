# ReAssist Architecture

## System Overview
ReAssist has shifted from an imperative monolithic router into a **LangGraph-backed declarative state machine**. The pipeline orchestrates 11 specialized AI Agents: 7 core intelligence agents + 4 QA/verification agents.

```mermaid
graph TD
    User([User Request]) --> NextJS[Next.js Frontend]
    NextJS <--> FastAPI[FastAPI Backend]
    
    FastAPI --> Router[AgenticOps Router]
    Router --> Orchestrator[LangGraph Orchestrator]
    
    subgraph RAG Pipeline
    Upload[PDF Upload] --> Chunking[Character Splitter]
    Chunking --> Embed[OpenAI Ada-002]
    Embed --> Chroma[(ChromaDB)]
    end
    
    subgraph LangGraph Pipeline
    Start((START)) --> Search[Search Agent]
    
    Search --> Grade[Relevance Grader]
    Grade --> GradeRouter{Relevant?}
    GradeRouter -- No --> Rewrite[Query Rewriter]
    Rewrite --> RewriteRouter{Attempt < Max}
    RewriteRouter -- Yes --> Search
    RewriteRouter -- No --> WebFallback[Web Search Fallback]
    WebFallback --> WebRouter{Found stuff?}
    WebRouter -- No --> END((END))
    
    GradeRouter -- Yes --> Summarize[Summarizer]
    WebRouter -- Yes --> Summarize
    
    Summarize --> Synthesize[Synthesizer]
    Synthesize --> Gap[Gap Finder]
    Gap --> Idea[Idea Generator]
    Idea --> Technique[Technique Agent]
    Technique --> Guidance[Guidance Agent]
    Guidance --> Verify[Answer Verifier]
    Verify --> END
    end
    
    Orchestrator --> Observability[JSONL Observability Logs]
```

## Database Schema
```mermaid
erDiagram
    Users ||--o{ Workspaces : owns
    Workspaces ||--o{ Documents : contains
    Workspaces ||--o{ PipelineExecutions : tracking
    Workspaces ||--o{ ChatMessages : holds
    PipelineExecutions ||--o{ AgentTraces : traces
```
