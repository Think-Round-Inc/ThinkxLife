from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from app.rag_chat import answer_question

app = FastAPI(title="Think Round FAQ API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# simple in-memory session store
chat_sessions = {}


class QueryRequest(BaseModel):
    question: str
    session_id: str


@app.get("/")
def home():
    return {"message": "Think Round FAQ API is running. Go to /docs to test the API."}


@app.post("/ask")
def ask_question(request: QueryRequest):
    session_id = request.session_id

    if session_id not in chat_sessions:
        chat_sessions[session_id] = []

    chat_history = chat_sessions[session_id]

    answer, docs, rewritten = answer_question(request.question, chat_history)

    # save conversation turn
    chat_history.append({
        "user": request.question,
        "assistant": answer
    })

    # keep sources clean and unique
    sources = []
    seen_urls = set()

    for doc in docs:
        url = doc["url"]
        if url not in seen_urls:
            sources.append({
                "title": doc["title"],
                "url": url
            })
            seen_urls.add(url)

    sources = sources[:3]

    return {
        "question": request.question,
        "rewritten_question": rewritten,
        "answer": answer,
        "sources": sources
    }