from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from app.rag_chat import answer_question

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {}


class ChatRequest(BaseModel):
    question: str
    session_id: str


@app.post("/chat")
def chat(request: ChatRequest):
    session_id = request.session_id

    if session_id not in sessions:
        sessions[session_id] = []

    chat_history = sessions[session_id]

    answer, docs, standalone = answer_question(
        request.question,
        chat_history
    )

    chat_history.append({
        "user": request.question,
        "assistant": answer
    })

    # limit history
    if len(chat_history) > 8:
        sessions[session_id] = chat_history[-8:]

    return {
        "answer": answer,
        "standalone_question": standalone,
        "sources": list(set(d["url"] for d in docs if d.get("url")))
    }