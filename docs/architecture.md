# Architecture Specification — Yojana Sahayak (योजना सहायक)

## 1. Overview
Yojana Sahayak is an AI-powered Government Scheme & Benefits Navigator designed specifically for Indian citizens. It bridges the critical discovery and accessibility gap in welfare schemes through deterministic eligibility matching, official government data, and grounded conversational AI.

## 2. Core Architectural Principle
> **Accuracy and trustworthy government information precede AI-generated content.**
> The Large Language Model (LLM) is **NEVER** the source of truth for government scheme criteria, eligibility rules, benefit sums, or application links.

The authoritative layer consists of:
1. Verified government datasets (Data.gov.in, India.gov.in, state portals)
2. Structured PostgreSQL relational records
3. Deterministic rule-based matching engine
4. Retrieved scheme documents from ChromaDB

The LLM (Groq / Llama) acts strictly as a conversational, translation, and grounded explanation interface.

## 3. High-Level System Architecture
```text
                    +------------------------------------+
                    |       Citizen / User Device        |
                    +-----------------+------------------+
                                      |
                                      v
                    +------------------------------------+
                    |         Streamlit Frontend         |
                    |  - Guided Form & Progress Bar      |
                    |  - Responsive Civic Design System  |
                    |  - Bilingual (Hindi / English)     |
                    +-----------------+------------------+
                                      |
                                      | REST / JSON
                                      v
                    +------------------------------------+
                    |          FastAPI Backend           |
                    |  - API Routing & Business Logic    |
                    |  - Supabase Auth Verification      |
                    |  - Scheme Service Layer            |
                    +--------+------------------+--------+
                             |                  |
           +-----------------+                  +-----------------+
           v                                                      v
+-----------------------+                              +--------------------+
| PostgreSQL Relational |                              | Deterministic Rule |
| Database              |                              | Matching Engine    |
| - Users & Profiles    |                              | - Hard Eligibility |
| - Schemes & Rules     |                              | - Scored Ranking   |
| - Application Tracker |                              +---------+----------+
+-----------------------+                                        |
           |                                                     |
           v                                                     v
+-----------------------+                              +--------------------+
|  ChromaDB Vector DB   |                              | Groq LLM (Llama)   |
|  - Sentence Embeddings| ─── Grounded Context ──────> | - Grounded Explain |
|  - Semantic Search    |                              | - Hindi / English  |
+-----------------------+                              +--------------------+
```

## 4. Separation of Concerns
- **Streamlit (`frontend/`):** Responsible purely for rendering UI components, handling user interactions, multi-step navigation, form validations, session state, and dispatching requests to the backend API. It contains zero business or eligibility rules.
- **FastAPI (`backend/`):** Hosts REST API endpoints, coordinates persistence with PostgreSQL, orchestrates semantic search with ChromaDB, evaluates hard rules via the matching engine, and manages AI provider abstractions.
- **PostgreSQL Database:** Master store for verified scheme data, citizen profiles, saved schemes, and application progress stages.
- **ChromaDB:** Local vector database storing embeddings generated via Sentence Transformers for hybrid semantic search and RAG retrieval.
- **Matching Engine:** Pure Python deterministic evaluation engine that categorizes matches into `Eligible`, `Potentially Eligible`, or `Not Eligible` with explainable audit trails.
- **Groq Provider:** Modular LLM integration adhering to strict prompt grounding guardrails to prevent hallucination.

## 5. Security & Isolation
- All API keys (`GROQ_API_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `DATABASE_URL`) reside exclusively in backend environment variables and are never transmitted to or embedded within the frontend.
- Frontend talks to FastAPI via standard internal HTTP calls.
