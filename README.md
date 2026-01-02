# Juvenile Justice LangGraph POCs

AI-powered tools for juvenile justice case management using LangChain and LangGraph.

## Overview

This repository contains proof-of-concept (POC) implementations for various juvenile justice workflows, leveraging:
- **LangGraph** for multi-agent orchestration
- **LangChain** for RAG (Retrieval-Augmented Generation)
- **Patterns** from the Universal Business Solution Framework

## POC Applications

| POC | Name | Status | Description |
|-----|------|--------|-------------|
| 01 | [Intake Triage Assistant](poc_01_intake_triage/) | In Progress | Guided intake, eligibility checking, case summary generation |
| 02 | [Case Brief Summarizer](poc_02_case_brief/) | Planned | Document ingestion, role-specific briefs |
| 03 | [Family Virtual Assistant](poc_03_family_assistant/) | Planned | 24/7 FAQ chatbot with guardrails |
| 04 | [Program Matching](poc_04_program_matching/) | Planned | Match youth to programs with eligibility/conflict checks |
| 05 | [JJDPA Compliance](poc_05_compliance/) | Planned | Regulatory compliance checking and audit trails |

## Project Structure

```
juvenile-justice-langgraph/
├── poc_01_intake_triage/      # Intake Triage Assistant
│   ├── src/                   # Source code
│   ├── knowledge_base/        # Policy documents, FAQs
│   ├── tests/                 # Unit and integration tests
│   └── README.md
├── poc_02_case_brief/         # Case Brief Summarizer (future)
├── poc_03_family_assistant/   # Family Virtual Assistant (future)
├── poc_04_program_matching/   # Program Matching (future)
├── poc_05_compliance/         # JJDPA Compliance (future)
├── shared/                    # Shared utilities across POCs
│   ├── patterns/              # Reusable patterns from Universal Framework
│   └── utils/                 # Common utilities
├── docs/                      # Documentation
├── requirements.txt           # Python dependencies
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/Texasdada13/juvenile-justice-langgraph.git
cd juvenile-justice-langgraph

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Running POC 01 - Intake Triage

```bash
cd poc_01_intake_triage
python src/main.py
```

## Technology Stack

- **LangChain**: Document loading, text splitting, embeddings, RAG pipelines
- **LangGraph**: Multi-agent orchestration, state management, human-in-the-loop
- **ChromaDB**: Vector store for development
- **Claude API**: LLM for reasoning and generation
- **FastAPI**: API endpoints (future)

## Architecture

Each POC follows a similar architecture:

```
┌─────────────────────────────────────┐
│     Knowledge Base (LangChain RAG)  │
│  - Policy documents                 │
│  - Eligibility rules                │
│  - Prior case patterns              │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   LangGraph Multi-Agent Pipeline    │
│  - Specialized agent nodes          │
│  - Conditional routing              │
│  - State management                 │
│  - Human-in-the-loop (HITL)        │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│         Output & Audit              │
│  - Case summaries                   │
│  - Citations                        │
│  - Audit trails                     │
└─────────────────────────────────────┘
```

## Contributing

This is a proof-of-concept project. Contributions welcome!

## License

MIT License
