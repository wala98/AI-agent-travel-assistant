
import sys
import os
# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from travel.src.travel_agent.crew import Travel_agent_crew
import re  # Add this import

import re
from typing import Union, List, Dict


def trigger_word(message: Union[str, List[Dict[str, str]]]) -> bool:
    """
    Check if a message (string) or a list of messages contains any trigger words
    to start the AI agent.
    """

    # Define trigger words (case-insensitive)
    combined_triggers = re.compile(
        r"\b("
        r"ai_agent|walid_travel|GoAround"  # Add more triggers here if needed
        r")\b",
        flags=re.IGNORECASE
    )

    if isinstance(message, str):
        # Single string: check directly
        return bool(combined_triggers.search(message))
    
    elif isinstance(message, list):
        # List of messages: check each message's content
        for msg in message:
            content = msg.get("content", "")
            if combined_triggers.search(content):
                return True
        return False
    
    else:
        raise ValueError("Invalid input type. Must be str or list of messages.")


# ---------------- Main crew Function ----------------
def process_message(conversation_input) -> str:
    # Convert list of messages to text if needed
    if isinstance(conversation_input, list):
        conversation_input = "\n".join(
            [f"{msg['sender']}: {msg['content']}" for msg in conversation_input]
        )

    if trigger_word(conversation_input):
        try:
            travel_agent = Travel_agent_crew().crew()
            result = travel_agent.kickoff(inputs={"conversation_input": conversation_input})
            return result
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"

    return "No trigger words detected."
    
