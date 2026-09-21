# API Specification — Yojana Sahayak

## Overview
The Yojana Sahayak Backend is implemented with FastAPI and exposes modular, versioned REST endpoints prefixed with `/api`. Interactive OpenAPI documentation is accessible at `/docs` and ReDoc at `/redoc`.

---

## Endpoints

### 1. Health & Status Check
#### `GET /api/health`
Verifies operational readiness of the backend service and returns environment metadata.

- **Request:** None
- **Response `200 OK`:**
```json
{
  "status": "healthy",
  "service": "Yojana Sahayak",
  "version": "0.1.0",
  "environment": "development",
  "timestamp": "2026-09-21T06:50:00.000000+00:00"
}
```

---

### 2. Root Information
#### `GET /`
Provides root service metadata and documentation links.

- **Request:** None
- **Response `200 OK`:**
```json
{
  "name": "Yojana Sahayak",
  "version": "0.1.0",
  "status": "online",
  "docs": "/docs",
  "health": "/api/health"
}
```

---

### Upcoming API Endpoints (Phases 2 – 12)

| Method | Path | Description | Phase |
|---|---|---|---|
| `GET` | `/api/schemes` | Paginated scheme directory with keyword search and filters | Phase 6 |
| `GET` | `/api/schemes/{slug}` | Full scheme details, documents, and application steps | Phase 3 |
| `POST` | `/api/schemes/match` | Deterministic eligibility engine evaluation | Phase 5 |
| `GET` | `/api/profile` | Retrieve citizen profile | Phase 2 |
| `PUT` | `/api/profile` | Update citizen profile | Phase 2 |
| `GET` | `/api/saved` | List bookmarked schemes for authenticated citizen | Phase 10 |
| `POST` | `/api/saved/{scheme_id}` | Bookmark a scheme | Phase 10 |
| `DELETE` | `/api/saved/{scheme_id}` | Remove bookmark | Phase 10 |
| `GET` | `/api/tracking` | List citizen application tracker items | Phase 10 |
| `POST` | `/api/tracking` | Add application tracking entry | Phase 10 |
| `PUT` | `/api/tracking/{id}` | Update application status (`Planning`, `Applied`, etc.) | Phase 10 |
| `POST` | `/api/ai/explain` | Grounded explanation of scheme eligibility | Phase 8 |
| `POST` | `/api/ai/ask` | Contextual Q&A on schemes using RAG pipeline | Phase 12 |
