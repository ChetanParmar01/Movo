# Movo

FastAPI backend + Streamlit UI for chatting with multiple providers (OpenAI / Anthropic / Google / Mistral / Groq).

---

## 🚀 Run (Windows / PowerShell)

### 1) Install dependencies (one-time)

```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
```

---

### 2) Start the backend

```powershell
.\venv\Scripts\activate
uvicorn app.main:app --reload
```

- Backend: http://127.0.0.1:8000  
- Health check: http://127.0.0.1:8000/health  

---

### 3) Start the UI (new terminal)

```powershell
.\venv\Scripts\activate
$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS="false"
streamlit run app\ui\main.py --server.address 127.0.0.1 --server.port 8501
```

- UI: http://localhost:8501  

---

## 🎥 Demo

[▶ Watch Demo Video](./Demo-video.mp4)

> Note: On GitHub, the video will open or download instead of playing inline.

---

## 🔑 API Keys

You can skip creating a `.env` file.

- **Recommended:** Paste your API keys into the UI sidebar (sent per request)
- **Alternative:** Set environment variables before running:

```powershell
$env:OPENAI_API_KEY="..."
$env:ANTHROPIC_API_KEY="..."
$env:GOOGLE_API_KEY="..."
```

---

## 📁 Project Structure

```
.
├── app/
│   ├── main.py
│   ├── api/
│   ├── db/
│   ├── services/
│   └── ui/
├── Demo-video.mp4
├── requirements.txt
└── README.md
```

---
