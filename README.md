# 📘 CenSQL – Text-to-SQL for Indian Census Data

This project implements a **Text-to-SQL system** for querying **Indian Census Data** using **LLaMA-3-SQLCoder + LoRA** with a **FastAPI backend**, **Supabase PostgreSQL database**, and **Next.js frontend**.

---

## 📂 File Structure

``` text
censql/
│
├── data/                   # All dataset-related files
│   ├── raw/                # Raw CSV / Excel / PDF downloads
│   ├── clean/              # Cleaned datasets (CSV)
│   ├── schema/             # Schema docs + CREATE TABLE SQL
│   └── census_demo.db      # Local SQLite (for quick testing)
│
├── src/                    # Core Python backend code
│   ├── data_ingest.py      # Data ingestion & cleaning classes
│   ├── sql_saver.py        # Save CSVs → SQL DB + dumps
│   ├── model_client.py     # Wrapper to call local/cloud model
│   ├── pipeline.py         # QueryRouter (templates + model path)
│   ├── backend_fastapi.py  # FastAPI server (API routes)
│   └── local_infer.py      # Local inference wrapper for SQLCoder
│
├── frontend/               # Next.js frontend
│   ├── app/                # Next.js app directory
│   └── components/         # UI components
│
├── notebooks/              # Jupyter/Colab notebooks for testing
│
├── logs/                   # Query logs + metrics
│   └── query_log.csv
│
├── environment.yml         # Conda environment definition
├── requirements.txt        # Pip dependencies
└── README.md               # Project overview (this file)
```

---

## ⚙️ Coding Conventions

### General

* Use **OOP principles**: each module should define a **class** (e.g., `DataIngestor`, `SQLSaver`, `ModelClient`, `QueryRouter`).
* Follow **snake_case** for file & function names.
* Follow **PascalCase** for class names.
* Add **docstrings** to every class and function.
* Keep **logging** (not print statements) for debugging.

### Data

* All raw files → `data/raw/`
* All cleaned files → `data/clean/`
* Schema docs (`schema.md`, `schema.sql`) → `data/schema/`
* Always export cleaned data as `.csv` and `.sql` dump for reproducibility.

### Backend

* API endpoints must be under `/api/` (e.g., `/api/query`).
* `run_pipeline()` should always return:

  ```json
  {
    "path": "template" | "model",
    "sql": "...",
    "result": [...],
    "latency_ms": 123
  }
  ```

### Frontend

* Use **Next.js (TypeScript)**.
* All API calls → `/api/query` endpoint.
* Show **Query, SQL, Result, Path, Latency**.

---

## 👥 Team Responsibilities

### **Nandhini & Gopikha** – Data & Database

* Collect datasets (CSV, Excel, PDF) from portals.
* Write ingestion + cleaning scripts (`data_ingest.py`).
* Normalize columns (snake_case).
* Load into Supabase Postgres via `sql_saver.py`.
* Maintain schema docs (`schema/schema.md`).

### **Sourish** – Model & Backend Integration

* Implement base model client (`local_infer.py` + `model_client.py`).
* Test LLaMA-3-SQLCoder inference without LoRA.
* Integrate with FastAPI backend (`backend_fastapi.py`).
* Prepare `ModelClient` for cloud access (LoRA later).

### **Maharajan** – Frontend

* Build Next.js UI (`frontend/`).
* Input: Natural language query.
* Output: SQL, result table, path (template/model), latency.
* Style UI (free choice of design).
* Deploy frontend (Vercel).

### **All Members**

* Follow file structure & conventions.
* Push work to respective folders.
* Update `README.md` with any new scripts.
* Work on PPT slides: Data, Model, Backend, Frontend, Evaluation.

---

## 🚀 Workflow

1. **Data** → Collect, clean, save to Supabase.
2. **Backend** → FastAPI pipeline (rule-based + model).
3. **Frontend** → Next.js app calling backend API.
4. **Integration** → End-to-end demo (NL → SQL → Census DB → Result).
5. **Evaluation** → Log metrics (Exact Match, Execution Accuracy, Latency).
