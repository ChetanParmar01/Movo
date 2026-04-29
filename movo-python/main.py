"""
Movo - AI Chat Application
Main FastAPI Application
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, assistants, keys, retrieval
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Movo API",
    description="Python-based AI Chat Application",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(assistants.router, prefix="/api/assistants", tags=["assistants"])
app.include_router(keys.router, prefix="/api/keys", tags=["keys"])
app.include_router(retrieval.router, prefix="/api/retrieval", tags=["retrieval"])


@app.get("/")
async def root():
    return {"message": "Movo API - Python AI Chat Application"}


@app.get("/health")
async def health():
    return {"status": "healthy"}