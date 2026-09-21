# Vector Database & RAG Pipeline Specification

## Technology
- **Vector Database:** ChromaDB
- **Embedding Model:** Sentence Transformers (with modular `EmbeddingService` abstraction)
- **LLM Provider:** Groq API running Llama models (via `AIProvider` abstraction)

## Data Stored in ChromaDB
- Scheme descriptions (English and Hindi)
- Eligibility criteria text
- Benefit breakdown
- Required documents & procedures
- Metadata: `scheme_id`, `category`, `ministry`, `state`, `language`, `source`, `last_verified_at`

## Retrieval Workflow
```text
User Query ──> Embedding Model ──> ChromaDB Vector Similarity
                                          │
                                          v
                                 Top K Relevant Schemes
                                          │
                                          v
                              Context Augmented Prompt
                                          │
                                          v
                             Groq API (Llama 3.3 70B)
                                          │
                                          v
                              Grounded Explanations
```
