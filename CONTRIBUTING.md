# 🤝 Contributing Guidelines – CenSQL Project

Welcome to the **CenSQL (Text-to-SQL for Indian Census Data)** project!
This guide explains how we collaborate using **Git + GitHub**. Please read before contributing.

---

## 🛠️ Git Workflow

We follow a **branching model**:

* `main` → always stable, working code
* `dev` → integration branch (latest tested features)
* feature branches → for each member/task

### Workflow Steps

1. **Update local repo**

   ```bash
   git checkout dev
   git pull origin dev
   ```

2. **Create a feature branch**

   ```bash
   git checkout -b feature/data-cleaning
   ```

   Use `feature/<task-name>` or `fix/<bug-name>`.

3. **Do your work** (edit code, add files).

4. **Commit changes**

   ```bash
   git add .
   git commit -m "data: cleaned population csv and added schema"
   ```

5. **Push branch**

   ```bash
   git push origin feature/data-cleaning
   ```

6. **Create Pull Request (PR)** → target `dev`.

   * Add description: what you did, testing steps, related issue.
   * Request review from at least one teammate.

7. **Merge to dev** only after approval & testing.

   * Maintainers will merge `dev → main` at milestones (after stable demo checkpoints).

---

## ✍️ Commit Message Convention

Follow **type: short description** format.
Types:

* `data:` → dataset updates / cleaning
* `model:` → model code changes
* `api:` → backend routes / pipeline
* `ui:` → frontend changes
* `docs:` → README, schema, comments
* `fix:` → bug fixes
* `refactor:` → improve structure without feature change

**Examples:**

``` text
data: added literacy dataset cleaned CSV
model: integrated SQLCoder base model inference
api: added /api/query endpoint with pipeline router
ui: built Next.js query input and results panel
docs: updated README with Supabase schema
```

---

## 🧪 Testing Guidelines

* Run scripts **locally** before committing.
* Log outputs for new modules in `logs/`.
* For frontend: ensure `npm run dev` works before PR.
* For backend: test `uvicorn backend_fastapi:app --reload` locally.

---

## 📂 File Conventions

* Python code → `src/` (classes in OOP style).
* Data → `data/raw/`, `data/clean/`, `data/schema/`.
* Logs → `logs/`.
* Frontend → `frontend/`.
* Docs → `README.md`, `CONTRIBUTING.md`, `PPT/`.

---

## 👥 Roles Reminder

* **Nandhini & Gopikha** → Data ingestion & Supabase schema.
* **Sourish** → Model integration & backend pipeline.
* **Maharajan** → Frontend (Next.js + API calls).
* **All** → PPT & research writing.

---

## 🚀 Deployment Flow

* **Backend (FastAPI)** → Deploy on **Render/Railway/Fly.io**.
* **DB (Supabase)** → Online Postgres (managed).
* **Frontend (Next.js)** → Deploy on **Vercel**.
