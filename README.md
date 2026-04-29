# Movo

Movo is a modern **FastAPI + Streamlit AI chat platform** that lets you interact with multiple LLM providers such as OpenAI, Anthropic, Google Gemini, Mistral, and Groq.

It provides a clean UI, modular backend, and easy multi-provider switching for building AI chat applications.

---

## ✨ Features

- ⚡ FastAPI backend for fast API performance  
- 🎨 Streamlit UI for simple chat interface  
- 🔌 Multi-provider support (OpenAI, Anthropic, Google, Mistral, Groq)  
- 💬 Real-time chat system  
- 🔐 API key support via UI or environment variables  
- 📦 Clean modular architecture (API, services, DB separation)  
- 🧪 Easy local setup and development  

---

## 🏗️ Project Structure


.
├── app/
│ ├── main.py # FastAPI entry point
│ ├── api/ # API routes (chat, keys, assistants, etc.)
│ ├── db/ # Database models & setup
│ ├── services/ # Core logic (LLM calls, chat handling)
│ └── ui/ # Streamlit frontend
│
├── Demo.mp4 # Demo video
├── requirements.txt # Python dependencies
└── README.md


---

## ⚙️ Installation

### 1️⃣ Clone repo
```bash
git clone https://github.com/your-username/movo.git
cd movo
2️⃣ Create virtual environment
python -m venv venv
.\venv\Scripts\activate
3️⃣ Install dependencies
pip install -r requirements.txt
🚀 Run Project
▶ Backend (FastAPI)
.\venv\Scripts\activate
uvicorn app.main:app --reload

Backend:

http://127.0.0.1:8000

Health check:

http://127.0.0.1:8000/health
💻 Frontend (Streamlit)

Open a new terminal:

.\venv\Scripts\activate
$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS="false"
streamlit run app\ui\main.py --server.address 127.0.0.1 --server.port 8501

UI:

http://localhost:8501
🔑 API Keys
Option 1 (Recommended)

Enter API keys in Streamlit sidebar.

Option 2 (Environment variables)
$env:OPENAI_API_KEY="your-key"
$env:ANTHROPIC_API_KEY="your-key"
$env:GOOGLE_API_KEY="your-key"
🎥 Demo

Demo file included:

Demo.mp4
❗ Why video is not playing on GitHub

GitHub does NOT support embedded video playback in README files.

Reasons:
README does not support inline video rendering
.mp4 files are shown as downloadable links only
GitHub does not auto-play videos for security reasons
✅ Solutions
✔ Best option

Upload video to YouTube (unlisted) or Loom and add link:

[Watch Demo](https://your-video-link)
✔ Alternative

Click the file directly in GitHub:

Demo.mp4
🚀 Future Improvements
Docker support
Authentication system
Chat history storage
Streaming responses
Cloud deployment (Render / Railway / AWS)
