# ai-powered-financial-news-intelligence-system-using-langgraph
# 📈 AI-Powered Financial News Intelligence System
### Using Multi-Agent Architecture + LangGraph + Vector Search + Local LLMs
 
## 🚀 Overview  
 
This project implements a fully functional AI-powered financial news intelligence system designed for traders, analysts, and investment platforms.

It automatically:

✔ Processes raw financial news  
✔ Removes duplicate & redundant articles  
✔ Extracts market entities (companies, sectors, regulators)  
✔ Maps news to impacted stocks with confidence levels  
✔ Ranks news based on semantic relevance + entity impact  
✔ Allows natural-language queries  
✔ Summarizes articles + explains impact using a local LLM (Ollama)  
✔ Provides both API endpoints (FastAPI) and UI (Streamlit)  
✔ Uses LangGraph multi-agent architecture  

This system is built following the structure required for the hackathon challenge.

## 🧠 Key Features

### 1. Multi-Agent News Processing Pipeline (LangGraph)

The ingestion pipeline consists of 6 coordinated agents:

| Agent                | Responsibility                           |
|----------------------|-------------------------------------------|
| Ingestion Agent      | Reads raw news item                       |
| Deduplication Agent  | Groups similar articles into stories      |
| NER Agent            | Extracts companies, sectors, regulators   |
| Impact Mapping Agent | Maps entities → stocks with confidence    |
| Storage Agent        | Stores enriched articles in SQLite        |
| Vector Index Agent   | Embeds & indexes docs in ChromaDB         |

---

### 2. Intelligent, Impact-Aware Search

Users can ask:

- “Show me news affecting HDFC Bank”
- “What RBI decisions impact the banking sector?”

The ranking engine combines:

✔ Semantic similarity  
✔ Direct ticker/company matches  
✔ Strict company-mention verification  
✔ Recency scoring  
✔ Impact confidence score  

### 3. Local LLM Summaries & Explanations (Ollama)

Top articles receive:

- A summary (extractive, no hallucination)
- An impact explanation (why news matters to the company)

LLM runs locally → No internet → Zero API cost.

---

### 4. FastAPI Backend

Available routes:

| Method | Route   | Description                      |
|--------|---------|----------------------------------|
| POST   | /query  | Returns ranked news + summaries  |
| GET    | /health | Health check                     |

---

### 5. Streamlit Frontend

A clean UI lets users:

✔ Enter queries  
✔ View ranked results  
✔ Read summaries & explanations  
✔ Explore entity impacts  

---

### 6. Evaluation Framework Included

Located in `/evaluation/`:

- `ner_eval.py` → checks NER accuracy  
- `ranking_eval.py` → precision@k for ranking  
- `impact_eval.py` → tests correct ticker mapping  
- `dedupe_eval.py` → story grouping quality  
- `evaluate_pipeline.py` → generates `evaluation_results.json`

## 📁 Project Structure
```bash
ai-powered-financial-news-intelligence-system-using-langgraph/
│
├── api/
│ ├── main.py
│ ├── routes.py
│ └── schemas.py
│
├── chroma_db/
│ ├── chroma.sqlite3
│ └── <collection-folders>/
│
├── chroma_store/
│ └── chroma.sqlite3
│
├── data/
│ ├── company_to_ticker.csv
│ ├── news_final.json
│ ├── news_final_with_story.json
│ ├── news_final_enriched.json
│ └── news_raw.json
│
├── evaluation/
│ ├── dedupe_eval.py
│ ├── impact_eval.py
│ ├── ner_eval.py
│ ├── ranking_eval.py
│ ├── run_all.py
│ ├── evaluation_results.json
│ └── evaluation_report.md
│
├── notebooks/
│ ├── dataset_builder.ipynb
│ ├── dataset_test.ipynb
│ ├── db_test.ipynb
│ ├── dedupe_test.ipynb
│ ├── ner_impact_test.ipynb
│ ├── pipeline_test.ipynb
│ ├── query_test.ipynb
│ ├── test_llm.ipynb
│ ├── test_script.ipynb
│ └── vector_test.ipynb
│
├── src/
│ ├── api/
│ │ ├── main.py
│ │ ├── routes.py
│ │ └── schemas.py
│ │
│ ├── config/
│ │ └── config.py
│ │
│ ├── db/
│ │ ├── crud.py
│ │ ├── db.py
│ │ ├── init_db.py
│ │ ├── load_data.py
│ │ └── models.py
│ │
│ ├── dedupe/
│ │ ├── deduper.py
│ │ └── run_dedupe.py
│ │
│ ├── impact/
│ │ └── impact_mapper.py
│ │
│ ├── ingestion/
│ │ └── ingestion_agent.py
│ │
│ ├── llm/
│ │ ├── llm_client.py
│ │ ├── prompts.py
│ │ └── service.py
│ │
│ ├── ner/
│ │ ├── custom_ner.py
│ │ ├── ner_agent.py
│ │ └── run_ner_and_impact.py
│ │
│ ├── pipeline/
│ │ ├── init.py
│ │ ├── agents.py
│ │ ├── batch_ingest.py
│ │ └── graph.py
│ │
│ ├── query/
│ │ ├── answer_formatter.py
│ │ ├── query_agent.py
│ │ └── query_engine.py
│ │
│ ├── utils/
│ │ ├── logger.py
│ │ └── init.py
│ │
│ └── vector/
│ ├── embedding_service.py
│ └── vector_store.py
│
├── requirements.txt
├── news.db
└── README.md
```

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/ai-powered-financial-news-intelligence-system-using-langgraph
cd ai-powered-financial-news-intelligence-system-using-langgraph
```

### 2. Create & activate virtual environment
```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Start Ollama (Local LLM)

Install Ollama from https://ollama.com/download
Then pull a local lightweight model:
```bash
ollama pull llama3.2
```

### 5. Run the news ingestion pipeline

This enriches all articles & creates the vector DB.

```bash
python -m src.pipeline.batch_ingest

```

### 6. Start the FastAPI backend
```bash
uvicorn src.api.main:app --reload
```
Runs at:
➡ http://127.0.0.1:8000

### 7. Start the Streamlit UI
```bash
streamlit run streamlit_app.py
```

Runs at:
➡ http://localhost:8501

## 🔍 Example Queries You Can Try

✔ “Show me news affecting HDFC Bank”  
✔ “What RBI policies impact the banking sector?”  
✔ “Latest news impacting Infosys”  
✔ “Which companies are affected by the Fed rate cut?”  

---

## 📊 Evaluation Metrics

Located at `/evaluation/`:

| Component       | Metric                     | File             |
|-----------------|----------------------------|------------------|
| NER             | Precision, Recall, F1      | ner_eval.py      |
| Ranking         | Precision@k, NDCG          | ranking_eval.py  |
| Deduplication   | Silhouette Score, Jaccard  | dedupe_eval.py   |
| Impact Mapping  | Accuracy@1                 | impact_eval.py   |

## 🏁 Final Notes

This project demonstrates:

🔥 Multi-agent AI design  
🔥 Real financial intelligence workflow  
🔥 Local LLM integration  
🔥 Production-ready API & UI  
🔥 Complete evaluation and documentation  
