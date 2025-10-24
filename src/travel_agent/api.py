# src/travel_agent/api.py
import os, sys
from typing import Any, Dict, List, Optional, Union
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..'))
sys.path.insert(0, SRC_ROOT)

# Import after path fix
try:
    from travel_agent.main import process_message
except ImportError:
    from main import process_message

class ChatMessage(BaseModel):
    sender: str
    content: str
    timestamp: Optional[str] = None

class OrchestrateRequest(BaseModel):
    conversation_input: Union[str, List[ChatMessage]]

# ▶ Structured response models
class Destination(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None
    assumed: bool = False

class Dates(BaseModel):
    start: Optional[str] = None  # "YYYY-MM-DD" or null
    end: Optional[str] = None
    assumed: bool = False

class OrchestrateStructuredResponse(BaseModel):
    destination: Optional[Destination] = None
    dates: Optional[Dates] = None
    weather: Optional[str] = None
    transport: Optional[str] = None
    stay: Optional[str] = None
    experiences: Optional[List[str]] = None
    # Optionals for error/info cases:
    error: Optional[str] = None
    details: Optional[str] = None
    info: Optional[str] = None

app = FastAPI(title="Travel Orchestrator", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "message": "Simple test server"}

@app.post("/orchestrate", response_model=OrchestrateStructuredResponse)
def orchestrate(body: OrchestrateRequest):
    ci = body.conversation_input
    if isinstance(ci, list):
        conversation_text = "\n".join([f"{m.sender}: {m.content}" for m in ci])
    elif isinstance(ci, str):
        conversation_text = ci
    else:
        raise HTTPException(status_code=400, detail="Invalid conversation_input format")

    result = process_message(conversation_text)
    return result  # already a dict with the structured fields
