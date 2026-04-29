# Movo

FastAPI backend + Streamlit UI for chatting with multiple providers (OpenAI / Anthropic / Google / Mistral / Groq).

## Run (Windows / PowerShell)

### 1) Install deps (one-time)

```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Start the backend

```powershell
.\venv\Scripts\activate
uvicorn app.main:app --reload
```

Backend: `http://127.0.0.1:8000` (health: `http://127.0.0.1:8000/health`)

### 3) Start the UI (new terminal)

```powershell
.\venv\Scripts\activate
$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS="false"
streamlit run app\ui\main.py --server.address 127.0.0.1 --server.port 8501
```

UI: `http://localhost:8501`

## Demo
[▶ Watch Demo Video](./Demo-video.mp4)

## API keys

You can skip creating a `.env` file.

- Recommended: paste your keys into the UI sidebar (they’re sent to the backend per-request).
- Alternative: export env vars before running:

```powershell
$env:OPENAI_API_KEY="..."
$env:ANTHROPIC_API_KEY="..."
$env:GOOGLE_API_KEY="..."
```

## Project structure

```
.
├── app/
│   ├── main.py
│   ├── api/
│   ├── db/
│   ├── services/
│   └── ui/
├── Demo.mp4
├── requirements.txt
└── README.md
```
