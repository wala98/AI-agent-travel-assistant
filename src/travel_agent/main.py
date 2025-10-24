# src/travel_agent/main.py
import os, sys, re, json, traceback
from datetime import datetime, timedelta
from typing import Union, List, Dict, Any, Optional

# ----------------------------
# Mode toggle: "static" (no LLM) or "dynamic" (CrewAI)
# ----------------------------
TRAVEL_AGENT_MODE = os.getenv("TRAVEL_AGENT_MODE", "static").lower()  # "static" by default

# Only import CrewAI if we really need it (dynamic mode)
def _lazy_import_crew():
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from crew import Travel_agent_crew
    return Travel_agent_crew

# ----------------------------
# Helpers
# ----------------------------
def _safe_city_country(city: Optional[str]) -> Dict[str, Any]:
    # Very lightweight country inference just for Sousse demo; extend as needed.
    country = "Tunisia" if city and city.lower() in {"sousse", "tunis", "monastir", "hammamet"} else None
    return {"city": city, "country": country, "assumed": country is None}

def _date_range(start: str, end: str) -> List[str]:
    if not start or not end:
        return []
    try:
        s = datetime.strptime(start, "%Y-%m-%d")
        e = datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        return []
    days = []
    d = s
    while d <= e:
        days.append(d.strftime("%Y-%m-%d"))
        d += timedelta(days=1)
    return days

def _base_response(intent: Optional[str] = None) -> Dict[str, Any]:
    return {
        "intent": intent,
        "destination": {"city": None, "country": None, "assumed": True},
        "dates": {"start": None, "end": None, "assumed": True},
        "hotel": {"name": None, "address": None, "description": None, "amenities": []},
        "city": {"name": None, "overview": None, "highlights": []},
        "nearby": [],
        "plan": [],
        "weather": None,
        "weather_range": [],
        "transport": None,
        "stay": None,
        "experiences": [],
        "notes": None
    }

# ----------------------------
# Static handlers (NO LLM, NO TOKENS)
# ----------------------------
def _handle_hotel_info(params: Dict[str, Any]) -> Dict[str, Any]:
    hotel_name = params.get("hotel_name")
    city = params.get("city")
    out = _base_response("hotel_info")
    out["destination"] = _safe_city_country(city)
    out["destination"]["assumed"] = city is None
    out["hotel"] = {
        "name": hotel_name,
        "address": None,  # keep null unless you wire a real provider
        "description": "4-star, beach access, pool, breakfast, family-friendly",
        "amenities": ["beach access", "pool", "breakfast", "family-friendly"]
    }
    out["city"] = {"name": city, "overview": None, "highlights": []}
    out["dates"]["assumed"] = False
    return out

def _handle_city_info(params: Dict[str, Any]) -> Dict[str, Any]:
    city = params.get("city")
    out = _base_response("city_info")
    out["destination"] = _safe_city_country(city)
    out["destination"]["assumed"] = city is None
    out["city"] = {
        "name": city,
        "overview": f"{city}: coastal city known for beaches, medina, and historic sites." if city else None,
        "highlights": ["Medina", "Beachfront", "Ribat Fortress"] if city else []
    }
    out["dates"]["assumed"] = False
    return out

def _handle_nearby(params: Dict[str, Any]) -> Dict[str, Any]:
    place_type = params.get("place_type") or "place"
    near = params.get("near") or {}
    near_name = near.get("hotel_name")
    near_city = near.get("city")
    label = near_name or near_city or "the area"
    out = _base_response("nearby")
    out["destination"] = _safe_city_country(near_city)
    out["destination"]["assumed"] = near_city is None
    out["nearby"] = [
        {"name": f"{place_type.title()} A", "type": place_type, "distance_km": 0.4, "note": f"Near {label}"},
        {"name": f"{place_type.title()} B", "type": place_type, "distance_km": 0.9, "note": f"Near {label}"},
        {"name": f"{place_type.title()} C", "type": place_type, "distance_km": 1.3, "note": f"Near {label}"},
    ]
    out["dates"]["assumed"] = False
    return out

def _handle_plan(params: Dict[str, Any]) -> Dict[str, Any]:
    city = params.get("city")
    start = params.get("start")
    end = params.get("end")
    out = _base_response("plan")
    out["destination"] = _safe_city_country(city)
    out["destination"]["assumed"] = city is None
    out["dates"] = {"start": start, "end": end, "assumed": False if start and end else True}
    items = []
    for d in _date_range(start, end):
        items.append({
            "date": d,
            "morning": f"Old town walk in {city}" if city else None,
            "afternoon": f"Beach time at {city} coast" if city else None,
            "evening": "Local dinner & cafe hopping"
        })
    out["plan"] = items
    return out

def _handle_weather(params: Dict[str, Any]) -> Dict[str, Any]:
    city = params.get("city")
    start = params.get("start")
    end = params.get("end")
    out = _base_response("weather")
    out["destination"] = _safe_city_country(city)
    out["destination"]["assumed"] = city is None

    if start and end:
        out["dates"] = {"start": start, "end": end, "assumed": False}
        out["weather_range"] = [{"date": d, "summary": "Mild, partly cloudy (stub)"} for d in _date_range(start, end)]
        out["weather"] = None
    else:
        out["dates"]["assumed"] = True
        out["weather"] = "24–28°C, partly cloudy (stub)"
    return out

STATIC_INTENT_HANDLERS = {
    "hotel_info": _handle_hotel_info,
    "city_info": _handle_city_info,
    "nearby": _handle_nearby,
    "plan": _handle_plan,
    "weather": _handle_weather,
}

# ----------------------------
# Public entry
# ----------------------------
def process_message(
    conversation_input: Union[str, List[Dict[str, str]]],
    intent: str | None = None,
    params: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    # 1) Normalize the conversation to a string (for future dynamic use)
    if isinstance(conversation_input, list):
        conversation_input = "\n".join(
            [f"{msg.get('sender','User')}: {msg.get('content','')}" for msg in conversation_input]
        )

    params = params or {}

    # 2) STATIC (default) — zero-token path
    if TRAVEL_AGENT_MODE == "static" and intent in STATIC_INTENT_HANDLERS:
        try:
            return STATIC_INTENT_HANDLERS[intent](params)
        except Exception:
            return {"error": "static_handler_failed", "details": "".join(traceback.format_exc())[-2000:]}

    # 3) DYNAMIC (optional) — use CrewAI if you need LLM behavior
    try:
        Travel_agent_crew = _lazy_import_crew()
        travel_agent = Travel_agent_crew().crew()
        result = travel_agent.kickoff(
            inputs={
                "conversation_input": conversation_input or "",
                "intent": intent or "",
                "params": params or {}
            }
        )
        # Try parsing JSON; if the LLM returns text, keep a safe fallback:
        try:
            obj = json.loads(str(result))
            if isinstance(obj, dict):
                return obj
        except Exception:
            pass
        # fallback
        return _base_response(intent) | {"notes": "dynamic_result_unparsed"}
    except Exception:
        return {"error": "agent_execution_failed", "details": "".join(traceback.format_exc())[-2000:]}
