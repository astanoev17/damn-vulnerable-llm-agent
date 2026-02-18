import os
from typing import Dict, List, Optional
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import litellm

API_TOKEN = os.getenv("REDTEAM_API_TOKEN", "")
MODEL = os.getenv("LITELLM_MODEL", "groq/llama-3.1-8b-instant")

app = FastAPI(title="DVLLM API", version="1.0.0")

# in-memory chat history (resets when Fly stops the machine)
CONV: Dict[str, List[dict]] = {}

class ChatRequest(BaseModel):
    conversation_id: str
    message: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 512

class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    model: str
    messages_count: int

def check_auth(auth: Optional[str]) -> None:
    if not API_TOKEN:
        return
    if not auth:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    token = auth.replace("Bearer ", "").strip()
    if token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest, authorization: Optional[str] = Header(default=None)):
    check_auth(authorization)

    msgs = CONV.get(req.conversation_id, [])

    if req.system_prompt and not any(m.get("role") == "system" for m in msgs):
        msgs.append({"role": "system", "content": req.system_prompt})

    msgs.append({"role": "user", "content": req.message})

    try:
        r = litellm.completion(
            model=MODEL,
            messages=msgs,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
        )
        reply = r["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    msgs.append({"role": "assistant", "content": reply})
    CONV[req.conversation_id] = msgs

    return ChatResponse(
        conversation_id=req.conversation_id,
        reply=reply,
        model=MODEL,
        messages_count=len(msgs),
    )
