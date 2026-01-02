# POC #1: Intake Triage Assistant

**Status:** In Progress
**Complexity:** Medium
**Primary Value:** Consistent, thorough intake process with policy compliance

## Problem Statement

Intake staff need to conduct structured questioning of youth and families, check eligibility against complex program rules, and create comprehensive initial case summaries. Currently, this process:
- Varies by staff experience and knowledge
- May miss critical eligibility criteria
- Lacks consistent documentation
- Requires manual policy lookup
- Time-consuming (45-90 minutes per intake)

## Solution

A LangGraph agent that guides intake staff through structured questioning, automatically checks eligibility against program rules, and creates initial case summaries with explicit policy citations.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 INTAKE TRIAGE ASSISTANT                  │
└─────────────────────────────────────────────────────────┘

LAYER 1: Knowledge Base (LangChain RAG)
┌──────────────────────────────────────────────────┐
│ • Local county policies & procedures             │
│ • JJDPA guidance documents                       │
│ • State juvenile justice statutes                │
│ • Program eligibility rules                      │
│                                                  │
│ [Document Loaders] → [Text Splitters]           │
│        ↓                                         │
│ [Embeddings] → [Vector Store: ChromaDB]         │
└──────────────────────────────────────────────────┘

LAYER 2: LangGraph Multi-Agent Orchestration
┌──────────────────────────────────────────────────┐
│  START                                           │
│    ↓                                             │
│  [Case Intake Node]                              │
│    ↓                                             │
│  [Structured Questioning Agent]                  │
│    ↓                                             │
│  [Policy Retrieval Agent]                        │
│    ↓                                             │
│  [Eligibility Checking Agent]                    │
│    ↓                                             │
│  [Risk Assessment Agent]                         │
│    ↓                                             │
│  [Case Summary Generator]                        │
│    ↓                                             │
│  [Human Review & Approval] ◄─── INTERRUPT()     │
│    ↓                                             │
│  END → Case Created in System                   │
└──────────────────────────────────────────────────┘
```

## Project Structure

```
poc_01_intake_triage/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── graph.py                # LangGraph workflow definition
│   ├── state.py                # State schema
│   ├── nodes/                  # Agent nodes
│   │   ├── __init__.py
│   │   ├── intake.py           # Case intake node
│   │   ├── questioning.py      # Structured questioning agent
│   │   ├── policy_retrieval.py # Policy retrieval agent
│   │   ├── eligibility.py      # Eligibility checking agent
│   │   ├── risk_assessment.py  # Risk assessment agent
│   │   ├── summary.py          # Case summary generator
│   │   └── human_review.py     # Human review node
│   ├── rag/                    # RAG components
│   │   ├── __init__.py
│   │   ├── document_loader.py  # Load policy documents
│   │   ├── vector_store.py     # ChromaDB management
│   │   └── retriever.py        # Retrieval strategies
│   └── prompts/                # Prompt templates
│       ├── __init__.py
│       └── templates.py
├── knowledge_base/             # Policy documents
│   ├── policies/               # County/state policies
│   ├── eligibility/            # Program eligibility rules
│   └── assessment_tools/       # Risk assessment tools
├── tests/
│   ├── __init__.py
│   ├── test_graph.py
│   └── test_nodes.py
└── README.md
```

## Quick Start

```bash
# From project root
cd poc_01_intake_triage

# Run the intake assistant
python src/main.py

# Run tests
pytest tests/
```

## Agent Nodes

### 1. Case Intake Node
- Collects basic information (youth name, DOB, contact info)
- Validates required fields
- Initializes case state

### 2. Structured Questioning Agent
- Generates contextual questions based on responses
- Tracks question coverage
- Adapts questioning based on risk factors

### 3. Policy Retrieval Agent
- Retrieves relevant policies from vector store
- Finds similar prior cases
- Extracts eligibility rules

### 4. Eligibility Checking Agent
- Matches youth profile to program criteria
- Cites specific policy passages
- Flags potential barriers

### 5. Risk Assessment Agent
- Evaluates risk factors
- Applies validated risk tools (YLS/CMI, SAVRY)
- Generates risk summary with citations

### 6. Case Summary Generator
- Synthesizes all collected information
- Creates structured case summary
- Adds policy citations throughout

### 7. Human Review Node
- Displays summary to intake officer
- Allows editing and approval
- Logs decisions for audit trail

## Success Metrics

| Metric | Target |
|--------|--------|
| Intake Duration | 30-40 min (vs 60-90 manual) |
| Topic Coverage | 100% of required topics |
| Eligibility Accuracy | >90% agreement with supervisor |
| Citation Accuracy | >95% verified correct |
| Approval Rate | >80% without major edits |
