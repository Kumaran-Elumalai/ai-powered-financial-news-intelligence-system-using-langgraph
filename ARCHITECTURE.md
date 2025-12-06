## 🏗️ System Architecture – Financial News Intelligence System

This document explains how the system works end-to-end, covering:

- Multi-agent processing pipeline
- Data model
- Vector search + ranking engine
- Local LLM integration (Ollama)
- API architecture
- Frontend architecture (Streamlit)

  ### 1. 🔄 Multi-Agent Pipeline (LangGraph)

The system processes raw news through six specialized agents, orchestrated with LangGraph.

Raw Article  
   │  
   ▼  
[1] Ingestion Agent  
   │  
   ▼  
[2] Deduplication Agent (story grouping)  
   │  
   ▼  
[3] NER Agent (entities → company, sector, regulator)  
   │  
   ▼  
[4] Impact Mapping Agent (entity → ticker)  
   │  
   ▼  
[5] Storage Agent (SQLite)  
   │  
   ▼  
[6] Vector Index Agent (ChromaDB)

### Agent Responsibilities

| Agent          | Description                                                         |
|----------------|---------------------------------------------------------------------|
| Ingestion      | Loads raw article fields                                            |
| Deduplication  | Uses embeddings + similarity threshold to group related articles    |
| NER            | Extracts ORG, SECTOR, PERSON, GPE, RBI, SEBI, etc.                  |
| Impact Mapper  | Converts ORG → ticker + sector using company_to_ticker.csv         |
| Storage        | Saves enriched article in SQLite                                    |
| Vector Index   | Embeds article, stores in ChromaDB for fast similarity search       |

### 2. 🧠 Data Model

Each enriched article is stored as:
```bash
{
  "id": 55,
  "story_id": 12,
  "title": "...",
  "description": "...",
  "published": "...",
  "entities": [...],
  "impacts": [
    {"ticker": "HDFCBANK", "company": "HDFC Bank", "confidence": 0.92, "type": "direct"}
  ]
}
```
### 3. 🔍 Search + Ranking Engine

When a user searches:  
“Show me news affecting HDFC Bank”

Steps:

1️⃣ **Extract entities from query**

→ "HDFC Bank" → Ticker → HDFCBANK  
→ Sector → BANKING  

2️⃣ **Vector search**

Top-k similar documents retrieved from ChromaDB.

3️⃣ **Ultra-Strict Ranking (final ordering)**

Score =

0.70 * semantic_similarity  
+ 0.25 * impact_score  
+ 0.05 * recency_score

Strict filters enforce:

✔ Company/ticker must appear in the article  
✔ Only direct impacts allowed  
✔ Penalize unrelated articles  

Result → High-precision relevant ranking  
Even if articles share keywords.


### 4. 🤖 Local LLM (Ollama) Integration

We use local models (llama3.2 or mistral) for:

1️⃣ Extractive summarization  
2️⃣ Explain why article impacts company  

The two functions:

```bash
summarize_article(title, body)
explain_impact(title, body, company)
```

Safety constraints:

- No hallucination  
- No invented facts  
- Output must be extractive  
- If insufficient info → explicit fallback string

### 5. ⚙️ API Architecture (FastAPI)

/query      POST   → returns ranked, enriched news  
/health     GET    → service health

Processing flow:

User Query  
    ↓  
QueryAgent  
    ↓  
QueryEngine.search()  
    ↓  
Ranking Engine  
    ↓  
LLM Summaries (top 2)  
    ↓  
Formatted Markdown Response  

### 6. 🎨 Frontend (Streamlit)

Provides a clean UI:

- Input query box
- Detected entities
- Ranked articles
- LLM-generated summaries
- Explanation of impact

The UI communicates with FastAPI using POST /query.

---

### 7. 📦 Storage Components

| Component               | Purpose                          |
|-------------------------|----------------------------------|
| SQLite                  | Persistent article DB             |
| ChromaDB                | Vector storage for semantic search |
| company_to_ticker.csv   | Mapping for impact agent          |

---

### 8. 🧪 Evaluation Framework

Files located in `/evaluation/` measure:

- NER accuracy
- Ranking performance (Precision@K, NDCG)
- Dedup quality
- Impact mapping correctness

Results stored in `evaluation_results.json`.

9. 🗺️ High-Level Architecture Diagram
<img width="1677" height="621" alt="image" src="https://github.com/user-attachments/assets/5598ed66-bef5-448f-b2aa-d7e4fe81fe14" />


  
             



