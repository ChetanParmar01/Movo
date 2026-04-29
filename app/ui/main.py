"""
Movo - Streamlit Chat UI
Main Application Entry Point
"""

import streamlit as st
import os
from typing import List, Dict, Any
import uuid
import json

# Page config
st.set_page_config(
    page_title="Movo",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #0f0f0f;
    }
    .stChat {
        background-color: #1a1a1a;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #2d2d2d;
        border-left: 3px solid #3b82f6;
    }
    .assistant-message {
        background-color: #1a1a1a;
        border-left: 3px solid #10b981;
    }
    .sidebar-title {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .model-selector {
        padding: 0.5rem;
        border-radius: 0.5rem;
        background-color: #2d2d2d;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())

if "workspace_id" not in st.session_state:
    st.session_state.workspace_id = "default"

if "model" not in st.session_state:
    st.session_state.model = "gpt-4"

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7


# Available models
MODELS = {
    "OpenAI": [
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "o1-preview",
        "o1-mini"
    ],
    "Anthropic": [
        # Fallback list (UI will try to fetch the real list from Anthropic when a key is provided)
        "claude-3-5-sonnet-latest",
        "claude-3-5-sonnet-20240620",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ],
    "Google": [
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-pro"
    ],
    "Mistral": [
        "mistral-large-latest",
        "mistral-medium-latest",
        "mistral-small-latest"
    ],
    "Groq": [
        "mixtral-8x7b-32768",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant"
    ]
}


def get_anthropic_models() -> List[str] | None:
    """Best-effort fetch of available Anthropic models for the provided API key."""
    api_key = st.session_state.get("anthropic_key")
    if not api_key:
        return None

    try:
        import requests

        resp = requests.get(
            "https://api.anthropic.com/v1/models",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
            timeout=20,
        )

        if resp.status_code != 200:
            return None

        data = resp.json()
        models = [item.get("id") for item in data.get("data", []) if item.get("id")]
        return models or None
    except Exception:
        return None


def init_api():
    """Initialize API client"""
    api_base = os.getenv("MOVO_API_BASE", "http://localhost:8000")
    return api_base


def send_message(message: str, model: str, temperature: float) -> Dict[str, Any]:
    """Send message to API"""
    api_base = init_api()
    
    # Prepare messages
    messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    messages.append({"role": "user", "content": message})
    
    try:
        import requests

        api_keys = {}
        if st.session_state.get("openai_key"):
            api_keys["openai"] = st.session_state["openai_key"]
        if st.session_state.get("anthropic_key"):
            api_keys["anthropic"] = st.session_state["anthropic_key"]
        if st.session_state.get("google_key"):
            api_keys["google"] = st.session_state["google_key"]
        
        response = requests.post(
            f"{api_base}/api/chat/chat",
            json={
                "workspace_id": st.session_state.workspace_id,
                "chat_id": st.session_state.chat_id,
                "messages": messages,
                "model": model,
                "temperature": temperature,
                "api_keys": api_keys or None,
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def main():
    """Main application"""
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-title">💬 Movo</div>', unsafe_allow_html=True)
        
        # New chat button
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_id = str(uuid.uuid4())
            st.rerun()
        
        st.divider()
        
        # Model selection
        st.subheader("Model Settings")
        
        # Provider dropdown
        provider = st.selectbox(
            "Provider",
            options=list(MODELS.keys()),
            index=0
        )
        
        # Model dropdown (Anthropic: prefer live model list for the provided key)
        models_for_provider = MODELS[provider]
        if provider == "Anthropic":
            models_for_provider = get_anthropic_models() or models_for_provider

        model = st.selectbox(
            "Model",
            options=models_for_provider,
            index=0
        )
        st.session_state.model = model
        
        # Temperature slider
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
            help="Higher values make output more random, lower values more focused"
        )
        st.session_state.temperature = temperature
        
        st.divider()
        
        # API Keys section
        st.subheader("API Keys")
        
        openai_key = st.text_input("OpenAI API Key", type="password", key="openai_key")
        anthropic_key = st.text_input("Anthropic API Key", type="password", key="anthropic_key")
        google_key = st.text_input("Google API Key", type="password", key="google_key")
        
        if st.button("Save Keys", use_container_width=True):
            if openai_key:
                os.environ["OPENAI_API_KEY"] = openai_key
            if anthropic_key:
                os.environ["ANTHROPIC_API_KEY"] = anthropic_key
            if google_key:
                os.environ["GOOGLE_API_KEY"] = google_key
            st.success("Keys saved!")
        
        st.divider()
        
        # Quick prompts
        st.subheader("Quick Prompts")
        prompts = [
            "Help me write code",
            "Explain a concept",
            "Brainstorm ideas",
            "Write something creative"
        ]
        
        for prompt in prompts:
            if st.button(prompt, key=f"prompt_{prompt}"):
                st.session_state.prompt_input = prompt
    
    # Main chat area
    st.title("Movo")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = send_message(
                    prompt,
                    st.session_state.model,
                    st.session_state.temperature
                )
            
            if "error" in response:
                st.error(response["error"])
                # Fallback to mock response for demo
                content = f"This is a demo response. In production, connect to the FastAPI backend at http://localhost:8000\n\nYou said: {prompt}"
            else:
                content = response.get("message", {}).get("content", "No response")
            
            st.markdown(content)
            
            # Add to messages
            st.session_state.messages.append({
                "role": "assistant",
                "content": content
            })


if __name__ == "__main__":
    main()
