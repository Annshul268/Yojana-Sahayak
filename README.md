# Yojana Sahayak
### AI Government Scheme & Benefits Navigator for Indian Citizens

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.41+-FF4B4B.svg)](https://streamlit.io/)
[![Phase](https://img.shields.io/badge/Phase-0%20Foundation-green.svg)](#roadmap)

Yojana Sahayak helps Indian citizens discover government welfare schemes and benefits tailored to their personal circumstances. Built with a strict **accuracy-first** architectural philosophy, deterministic eligibility matching precedes all AI interactions, ensuring the LLM acts as an explanatory layer grounded purely in verified official government data.

---

## 🏛️ Core Architectural Principle
> **Accuracy and trustworthy government information come before AI-generated answers.**
> The LLM must **NEVER** be the source of truth for government scheme information.
> 
> The source of truth is:
> 1. Verified government data sources
> 2. Structured scheme database in PostgreSQL
> 3. Deterministic eligibility rules
> 4. Grounded retrieval via ChromaDB

---

## 🏗️ Architecture Stack
- **Frontend:** Streamlit (Python, responsive civic theme, bilingual EN/HI)
- **Backend:** FastAPI (REST API, deterministic matching engine, business services)
- **Database:** PostgreSQL (structured profile and scheme storage)
- **Authentication:** Supabase Auth
- **Vector DB & RAG:** ChromaDB + Sentence Transformers
- **LLM Engine:** Groq API (Llama models via provider abstraction)

---

## 🚀 Quick Start (Phase 0)

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Git

### 2. Setup Environment
```bash
# Clone the repository
git clone https://github.com/Annshul268/Yojana-Sahayak.git
cd Yojana-Sahayak

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 3. Run Backend (FastAPI)
```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Health Check: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
- Interactive Swagger Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 4. Run Frontend (Streamlit)
In a separate terminal:
```bash
source .venv/bin/activate
streamlit run frontend/app.py --server.port 8501
```
- Open browser at: [http://localhost:8501](http://localhost:8501)

### 5. Automated Runner Script
Alternatively, run both concurrently with:
```bash
./scripts/run_dev.sh
```

---

## 🧪 Testing

Run backend tests using `pytest`:
```bash
pytest -v
```

---

---

## 🎯 Intent-Driven Dynamic Eligibility Architecture

Yojana Sahayak replaces static, overwhelming forms with an **intent-first, adaptive discovery engine**:

$$\text{Citizen Intent} \longrightarrow \text{Adaptive Minimum Questions} \longrightarrow \text{Deterministic Rules Engine} \longrightarrow \text{Grounded AI Explanation} \longrightarrow \text{Official Action}$$

### Key Capabilities:
1. **Top-Level Intent Taxonomy (`backend/app/matching/taxonomy.py`):**
   - Covers Education & Scholarships, Business & Loans, Agriculture & Farming, Jobs & Employment, Skill Training, Housing, Healthcare, Senior Citizen & Pension, Women & Child, and Disability Support.
2. **Scheme Tagging:**
   - Schemes store structured tags (e.g., `["agriculture", "farmer", "income-support"]`) for fast candidate retrieval before rule matching.
3. **Adaptive Question Engine (`frontend/services/questionnaire_engine.py`):**
   - **Minimum-Information Principle:** Irrelevant questions are skipped automatically (e.g. Business applicants never see student questions; Gender is omitted if no candidate scheme restricts gender).
   - Preserves state on back/forward navigation and handles unknown/not-sure values gracefully.
4. **Deterministic 9-Step Matching Pipeline (`backend/app/matching/engine.py`):**
   - Normalization $\rightarrow$ Intent determination $\rightarrow$ Candidate retrieval $\rightarrow$ Hard rules checking $\rightarrow$ Missing info identification $\rightarrow$ Relevance scoring $\rightarrow$ Structured output (`matched_attributes`, `failed_conditions`, `important_conditions`).
5. **Grounded AI Explanations:**
   - Groq + Llama explain why the citizen qualifies based strictly on ChromaDB-retrieved facts without altering deterministic eligibility conclusions.

---

## 📚 Documentation
- [Architecture](docs/architecture.md)
- [API Reference](docs/api.md)
- [Database Schema](docs/database.md)
- [Matching Engine](docs/matching-engine.md)
- [RAG & Vector Retrieval](docs/rag.md)
- [Data Pipeline](docs/data-pipeline.md)
