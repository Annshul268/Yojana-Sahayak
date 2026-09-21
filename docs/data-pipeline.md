# Government Data Ingestion Pipeline Specification

## Ingestion Architecture
```text
Government Sources (Data.gov.in, India.gov.in, State Portals, Curated Fallback)
                               │
                               v
                       Fetch & Ingest
                               │
                               v
                             Parse
                               │
                               v
                       Clean & Normalize
                               │
                               v
                           Validate
                               │
                               v
                          Deduplicate
                               │
               ┌───────────────┴───────────────┐
               v                               v
      PostgreSQL Storage               ChromaDB Vector Store
 (Structured Rules & Schemes)          (Semantic Embeddings)
```

## Data Traceability
Every ingested scheme record maintains:
- `source`: Name of the source (e.g. `data.gov.in`)
- `official_url`: Verified official government portal link
- `ministry`: Responsible government department/ministry
- `last_verified_at`: Timestamp of verification
- `verification_status`: Status indicating whether data was human-verified or automated
