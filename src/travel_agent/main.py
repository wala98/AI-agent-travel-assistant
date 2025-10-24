# src/travel_agent/main.py
import os, sys, re, json, traceback
from typing import Union, List, Dict, Any
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from crew import Travel_agent_crew

TRIGGERS = re.compile(r"\b(ai_agent|walid_travel|GoAround)\b", re.IGNORECASE)

def trigger_word(message: Union[str, List[Dict[str, str]]]) -> bool:
    if isinstance(message, str):
        return bool(TRIGGERS.search(message))
    if isinstance(message, list):
        for msg in message:
            if TRIGGERS.search(msg.get("content", "")):
                return True
        return False
    raise ValueError("Invalid input type. Must be str or list of messages.")

def _extract_json(text: str) -> Dict[str, Any]:
    """Return parsed JSON object if found, else a safe default dict."""
    # Try full-body parse first
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    # Fallback: find first {...} block
    m = re.search(r"\{.*\}", text, re.S)
    if m:
        try:
            obj = json.loads(m.group(0))
            if isinstance(obj, dict):
                return obj
        except Exception:
            pass
    # Ultimate fallback: empty-shell structure
    return {
        "destination": {"city": None, "country": None, "assumed": True},
        "dates": {"start": None, "end": None, "assumed": True},
        "weather": None,
        "transport": None,
        "stay": None,
        "experiences": []
    }

def process_message(conversation_input) -> Dict[str, Any]:
    if isinstance(conversation_input, list):
        conversation_input = "\n".join(
            [f"{msg['sender']}: {msg['content']}" for msg in conversation_input]
        )
    if trigger_word(conversation_input):
        try:
            travel_agent = Travel_agent_crew().crew()
            result = travel_agent.kickoff(inputs={"conversation_input": conversation_input})
            # CrewAI returns an object; cast to str and extract JSON
            return _extract_json(str(result))
        except Exception:
            return {
                "error": "agent_execution_failed",
                "details": "".join(traceback.format_exc())[-2000:],  # trimmed
            }
    return {"info": "no_trigger_detected"}
