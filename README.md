# Yojana Sahayak (योजना सहायक)
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

## 🧭 Project Roadmap
- [x] **Phase 0:** Project Foundation (Architecture, FastAPI, Streamlit, Health API, Config)
- [ ] **Phase 1:** Streamlit UI Foundation (Guided Eligibility Form, Directory, Bilingual Layout)
- [ ] **Phase 2:** Database & Authentication (PostgreSQL Models, Supabase Auth)
- [ ] **Phase 3:** Scheme Data System (Structured Eligibility Rules & Seeding)
- [ ] **Phase 4:** Government Data Pipeline (ETL, Validation & Ingestion)
- [ ] **Phase 5:** Deterministic Matching Engine (Scoring, Hard Rules & Audit Trails)
- [ ] **Phase 6:** Scheme Search & Advanced Filters
- [ ] **Phase 7:** ChromaDB & RAG Retrieval Pipeline
- [ ] **Phase 8:** Groq / Llama Integration & Grounded Prompting
- [ ] **Phase 9:** Bilingual Localization (Hindi / English)
- [ ] **Phase 10:** Saved Schemes & Application Tracker
- [ ] **Phase 11:** Admin Dashboard
- [ ] **Phase 12:** AI Scheme Assistant
- [ ] **Phase 13:** Comprehensive Test Suite
- [ ] **Phase 14:** Security Review & Hardening
- [ ] **Phase 15:** Performance Optimization
- [ ] **Phase 16:** Final Civic UI Polish

---

## 📚 Documentation
- [Architecture](docs/architecture.md)
- [API Reference](docs/api.md)
- [Database Schema](docs/database.md)
- [Matching Engine](docs/matching-engine.md)
- [RAG & Vector Retrieval](docs/rag.md)
- [Data Pipeline](docs/data-pipeline.md)
>>>>>>> 88a3400 (feat: initialize yojana sahayak architecture)
