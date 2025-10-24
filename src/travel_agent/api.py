import sys
import os
import uvicorn 
from main import process_message

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.insert(0, project_root)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from pydantic import BaseModel  # Add this import
# Import your function
# ✅ Dynamically add the "travel_agent/src" folder to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, src_root)



from fastapi import FastAPI
import uvicorn

from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok", "message": "Simple test server"}

@app.get("/")
def root():
    return {"message": "Hello World"}


@app.post("/orchestrate")
def orchestrate(body: Dict[str, Any]):
    conversation_input = body.get("conversation_input")

    if not conversation_input:
        raise HTTPException(status_code=400, detail="conversation_input is required")

    # ✅ Ensure the input is a list (from Streamlit)
    if isinstance(conversation_input, list):
        # Join all message contents into one text block (for example)
        conversation_text = "\n".join(
            [f"{msg['sender']}: {msg['content']}" for msg in conversation_input]
        )
    elif isinstance(conversation_input, str):
        conversation_text = conversation_input
    else:
        raise HTTPException(status_code=400, detail="Invalid conversation_input format")

    # Process through your travel agent 
    response = process_message(conversation_text)
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)




    
