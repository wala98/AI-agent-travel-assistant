import streamlit as st
import requests
from datetime import datetime

# --- Page setup ---
st.set_page_config(page_title="Group Chat", page_icon="💬", layout="centered")
st.title("💬 Group Chat — Friends Planning a Trip")

# --- Initialize session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "participants" not in st.session_state:
    st.session_state.participants = ["You", "Alice", "Bob", "Sarah"]

if "agent_responses" not in st.session_state:
    st.session_state.agent_responses = []  # Scrollable list of AI responses

# --- Sidebar (participants list) ---
st.sidebar.header("👥 Participants")
for user in st.session_state.participants:
    st.sidebar.write(f"• {user}")

st.sidebar.markdown("---")
st.sidebar.info("This is a group chat simulation. Each message appears in order of sending.")

# --- Display scrollable AI notification popup ---
if st.session_state.agent_responses:
    responses_html = "<br>".join(
        [f"💡 <b>Travel Assistant:</b> {resp}" for resp in st.session_state.agent_responses]
    )
    st.markdown(
        f"""
        <div style="
            position: fixed;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            background-color: #e6f7ff;
            border: 1px solid #91d5ff;
            padding: 12px 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            z-index: 9999;
            max-width: 80%;
            max-height: 150px;   /* limit the height */
            overflow-y: auto;     /* enable scrolling */
        ">
            {responses_html}
        </div>
        """,
        unsafe_allow_html=True
    )

from typing import Dict, Any, List, Literal, Optional
import json, re
_MD_OPEN = re.compile(r"^\s*```[a-zA-Z0-9_-]*", re.M)
_MD_CLOSE = re.compile(r"```\s*$", re.M)
def _strip_md_fences(s: str) -> str:
    s = s.strip()
    s = _MD_OPEN.sub("", s)
    s = _MD_CLOSE.sub("", s)
    return s.strip()

def _first_json_obj(text: str) -> Optional[str]:
    m = re.search(r"\{.*\}", text, re.S)
    return m.group(0) if m else None

def parse_jsonish(raw: Any) -> Any:
    if raw is None:
        return None
    if isinstance(raw, dict):
        if "raw" in raw and isinstance(raw["raw"], str):
            raw = raw["raw"]
        else:
            return raw
    if not isinstance(raw, str):
        return raw
    cleaned = _strip_md_fences(raw)
    try:
        return json.loads(cleaned)
    except Exception:
        pass
    first = _first_json_obj(cleaned)
    if first:
        try:
            return json.loads(first)
        except Exception:
            return cleaned
    return cleaned


# --- Display chat history ---
st.markdown("### 💭 Conversation")
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        align = "flex-end" if msg["sender"] == "You" else "flex-start"
        color = "#DCF8C6" if msg["sender"] == "You" else "#FFF"
        st.markdown(
            f"""
            <div style="display: flex; justify-content: {align}; margin-bottom: 8px;">
                <div style="background-color: {color};
                            padding: 10px 14px;
                            border-radius: 14px;
                            max-width: 70%;
                            box-shadow: 0px 1px 2px rgba(0,0,0,0.1);">
                    <b style="color:#555;">{msg["sender"]}</b><br>
                    {msg["content"]}<br>
                    <small style="color:gray;">{msg.get("timestamp", "")}</small>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# --- Message input ---
st.markdown("---")
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([4, 1])
    with col1:
        message_text = st.text_input("Type your message...", key="chat_input")
    with col2:
        sender = st.selectbox("Sender", st.session_state.participants, label_visibility="collapsed")
    submitted = st.form_submit_button("Send")

# --- On send ---
if submitted and message_text.strip():
    # Add message locally
    st.session_state.messages.append({
        "sender": sender,
        "content": message_text,
        "timestamp": datetime.now().strftime("%H:%M")
    })

    # Send entire conversation to FastAPI for AI detection
    try:
        resp = requests.post(
            "http://127.0.0.1:8000/orchestrate",
            json={"conversation_input": st.session_state.messages},
        )
        if resp.status_code == 200:
            result = resp.json().get("response")
            result = parse_jsonish(result)
            if result:
                st.session_state.agent_responses.append(result)  # Add to scrollable popup
        else:
            st.session_state.agent_responses.append("⚠️ Backend returned an error.")
    except Exception as e:
        st.session_state.agent_responses.append(f"⚠️ Could not reach backend: {e}")

    st.rerun()
