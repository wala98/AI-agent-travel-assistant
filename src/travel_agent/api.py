# src/travel_agent/api.py
import os, sys
from typing import Any, Dict, List, Optional, Union, Literal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..'))
sys.path.insert(0, SRC_ROOT)

try:
    from travel_agent.main import process_message
except ImportError:
    from main import process_message

class ChatMessage(BaseModel):
    sender: str
    content: str
    timestamp: Optional[str] = None

IntentLiteral = Literal["hotel_info","city_info","nearby","plan","weather"]

class OrchestrateRequest(BaseModel):
    conversation_input: Union[str, List[ChatMessage]]
    intent: IntentLiteral
    params: Dict[str, Any] = {}

class Destination(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None
    assumed: bool = False

class Dates(BaseModel):
    start: Optional[str] = None
    end: Optional[str] = None
    assumed: bool = False

class Hotel(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    amenities: Optional[List[str]] = None

class City(BaseModel):
    name: Optional[str] = None
    overview: Optional[str] = None
    highlights: Optional[List[str]] = None

class NearbyItem(BaseModel):
    name: str
    type: Optional[str] = None
    distance_km: Optional[float] = None
    note: Optional[str] = None

class PlanItem(BaseModel):
    date: str
    morning: Optional[str] = None
    afternoon: Optional[str] = None
    evening: Optional[str] = None

class OrchestrateStructuredResponse(BaseModel):
    intent: Optional[str] = None
    destination: Optional[Destination] = None
    dates: Optional[Dates] = None
    hotel: Optional[Hotel] = None
    city: Optional[City] = None
    nearby: Optional[List[NearbyItem]] = None
    plan: Optional[List[PlanItem]] = None
    weather: Optional[str] = None
    weather_range: Optional[List[Dict[str, str]]] = None
    transport: Optional[str] = None
    stay: Optional[str] = None
    experiences: Optional[List[str]] = None
    notes: Optional[str] = None
    # fallbacks
    error: Optional[str] = None
    details: Optional[str] = None
    info: Optional[str] = None

app = FastAPI(title="Travel Orchestrator", version="0.3.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/orchestrate", response_model=OrchestrateStructuredResponse)
def orchestrate(body: OrchestrateRequest):
    ci = body.conversation_input
    if isinstance(ci, list):
        conversation_text = "\n".join([f"{m.sender}: {m.content}" for m in ci])
    elif isinstance(ci, str):
        conversation_text = ci
    else:
        raise HTTPException(status_code=400, detail="Invalid conversation_input format")

    result = process_message(conversation_text, intent=body.intent, params=body.params)
    return result
