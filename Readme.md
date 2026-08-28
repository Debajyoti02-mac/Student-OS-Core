# Student OS AI — Full-Stack Learning Agent & Task Planner

A production-grade AI learning agent application built with **FastAPI**, **LangGraph**, **Groq LLMs**, **SQLite Session Checkpointing**, and a responsive **Glassmorphism HTML5/CSS/JS** Web Interface.

---

## 🌟 Key Features

- **Goal Deconstruction & Analysis**: Translates high-level goals into prerequisite skills, ordered learning roadmap, and a practical starter project.
- **Dynamic Task Planning & Prioritization**: Automatically generates 10–15 actionable step-by-step learning tasks.
- **Persistent State & Progress Tracking**: SQLite checkpointer (`student_memory.db`) tracks individual student progress across sessions.
- **Adaptive Task Remediation**: If a student clicks *"I'm Stuck"*, the agent adaptively decomposes the task into simpler, bite-sized subtasks.
- **Unified Full-Stack Deployment**: FastAPI serves both the REST API and the interactive web interface directly with zero CORS issues.
- **One-Click Render Ready**: Preconfigured `render.yaml` for instant deployment on [Render](https://render.com).

---

## 📁 Project Structure

```
OS AI for students/
├── app/
│   ├── main.py              # FastAPI app instance, static mounting, lifespan
│   ├── core/
│   │   └── config.py        # Environment settings (PORT, GROQ_API_KEY, etc.)
│   ├── models/
│   │   └── schemas.py       # Pydantic validation & response models
│   ├── graph/
│   │   ├── state.py         # StudentState TypedDict & structured schemas
│   │   ├── nodes.py         # Node implementations & routing logic
│   │   └── builder.py       # StateGraph compilation with SqliteSaver
│   └── api/
│       └── routes.py        # API endpoints
├── static/
│   ├── index.html           # Modern glassmorphism UI layout
│   ├── style.css            # Responsive dark mode CSS design system
│   └── app.js               # Client state, API interactions & toasts
├── run.py                   # Server launcher script
├── render.yaml              # Render blueprint deployment file
├── requirements.txt         # Project dependencies
├── .env.example             # Environment template
└── Readme.md                # Documentation
```

---

## 💻 Local Development Setup

### 1. Configure Environment
```bash
cp .env.example .env
```
Ensure `.env` contains:
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

### 2. Activate Virtual Environment & Install Dependencies
```bash
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the Server
```bash
python run.py
```
Or directly with uvicorn:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Web Application**: [http://localhost:8000](http://localhost:8000)
- **API Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🚀 Deploying on Render

### Option A: Using Render Blueprints (Recommended)
1. Push your repository to **GitHub**.
2. Go to the [Render Dashboard](https://dashboard.render.com/) and click **New > Blueprint**.
3. Connect your repository. Render will automatically detect `render.yaml`.
4. Set the environment variable:
   - `GROQ_API_KEY`: `your_groq_api_key`
5. Click **Apply**. Render will build and deploy your service!

---

### Option B: Manual Web Service Setup on Render
1. Go to [Render Dashboard](https://dashboard.render.com/) > **New > Web Service**.
2. Connect your GitHub repository.
3. Configure the settings:
   - **Name**: `student-os-ai`
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
4. Add **Environment Variables**:
   - `GROQ_API_KEY`: *(Your Groq API key)*
   - `GROQ_MODEL`: `openai/gpt-oss-20b` (or `openai/gpt-oss-120b`)
   - `PYTHON_VERSION`: `3.12.0`
5. Click **Deploy Web Service**.

---

## 📡 API Endpoints Reference

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Serves the Web Dashboard |
| `GET` | `/health` | Server health check |
| `POST` | `/api/student/goal` | Initialize learning roadmap & task plan |
| `POST` | `/api/student/status` | Advance progress (`progressing`) or simplify task (`stuck`) |
| `GET` | `/api/student/state/{student_id}` | Retrieve current student state & milestones |
| `GET` | `/api/student/history/{student_id}` | Retrieve student interaction & reasoning logs |
| `GET` | `/docs` | Interactive Swagger API docs |
