# src/travel_agent/main.py
import os
import sys
import re
import traceback
from typing import Union, List, Dict

# Ensure project root on path (so 'crew' resolves)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crew import Travel_agent_crew  # after path tweak

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
# ... imports stay the same

def _only_final_line(text: str) -> str:
    if not text:
        return "ERROR: empty result"
    # Prefer an explicit "Final Answer:" line
    if "Final Answer:" in text:
        line = text.split("Final Answer:", 1)[1]
        line = line.splitlines()[0].strip()
        return f"Final Answer: {line}"
    # Fallback: collapse to first non-empty line
    first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    return f"Final Answer: {first[:180]}"  # hard cap just in case

def process_message(conversation_input) -> str:
    if isinstance(conversation_input, list):
        conversation_input = "\n".join(
            [f"{msg['sender']}: {msg['content']}" for msg in conversation_input]
        )
    if trigger_word(conversation_input):
        try:
            travel_agent = Travel_agent_crew().crew()
            result = travel_agent.kickoff(inputs={"conversation_input": conversation_input})
            return _only_final_line(str(result))
        except Exception:
            return "ERROR:\n" + "".join(traceback.format_exc())
    return "No trigger words detected."
