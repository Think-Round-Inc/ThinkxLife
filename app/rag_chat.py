import json
import re
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS

load_dotenv()

VECTOR_DB_DIR = "data/vector_db"
CHUNKS_FILE = "data/thinkround_chunks.json"

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "do", "does", "did",
    "what", "who", "when", "where", "why", "how", "can", "could", "should",
    "would", "i", "me", "my", "we", "our", "you", "your", "they", "them",
    "their", "it", "there", "with", "for", "of", "on", "in", "to", "and",
    "or", "at", "by", "from", "about", "here", "there"
}


def load_chunks():
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_vector_db():
    embeddings = OpenAIEmbeddings()
    return FAISS.load_local(
        VECTOR_DB_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )


CHUNKS = load_chunks()
VECTOR_DB = load_vector_db()
LLM = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def tokenize(text):
    words = re.findall(r"\b[a-zA-Z0-9]+\b", (text or "").lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


def normalize_chunk(chunk):
    return {
        "text": chunk.get("text", ""),
        "title": chunk.get("title", "Unknown Title"),
        "url": chunk.get("url", "Unknown URL"),
        "chunk_id": chunk.get("chunk_id")
    }


def is_definition_query(question: str) -> bool:
    q = question.lower().strip()
    triggers = [
        "what is think round",
        "who is think round",
        "tell me about think round",
        "about think round",
        "what does think round do",
        "what is the mission of think round"
    ]
    return any(t in q for t in triggers)


def is_founder_query(question: str) -> bool:
    q = question.lower().strip()
    triggers = [
        "who founded think round",
        "founder of think round",
        "who is the founder of think round"
    ]
    return any(t in q for t in triggers)


def is_program_query(question: str) -> bool:
    q = question.lower().strip()
    triggers = [
        "what programs do they offer",
        "what programs does think round offer",
        "programs of think round",
        "what does think round offer"
    ]
    return any(t in q for t in triggers)


def is_volunteer_query(question: str) -> bool:
    q = question.lower().strip()
    triggers = [
        "volunteer",
        "volunteering",
        "how can i volunteer",
        "how do i volunteer",
        "how to volunteer",
        "can i volunteer",
        "get involved",
        "help out",
        "join as a volunteer"
    ]
    return any(t in q for t in triggers)


def get_url_priority(url: str, question: str) -> int:
    url = (url or "").lower()
    q = question.lower()
    score = 0

    # Positive boosts
    if url.endswith(".org") or url.endswith(".org/") or url == "https://www.thinkround.org":
        score += 12

    if "about" in url:
        score += 10

    if "mission" in url:
        score += 8

    if "founder" in url:
        score += 10

    if "program" in url:
        score += 8

    if "volunteer" in url or "new-page-96" in url:
        score += 20

    if "contact" in url:
        score += 6

    if "our-board" in url:
        score += 6

    if "center-for-the-human-family" in url and "center for the human family" in q:
        score += 12

    # Negative penalties
    if "/blogs" in url or "blog" in url:
        score -= 8

    if "new-page" in url and "new-page-96" not in url:
        score -= 10

    if "installation" in url or "exhibition" in url or "paradise-project" in url:
        score -= 12

    # Query-specific boosts
    if is_definition_query(question):
        if "about" in url or url.endswith(".org/") or url == "https://www.thinkround.org":
            score += 12
        if "/blogs" in url or ("new-page" in url and "new-page-96" not in url):
            score -= 10

    if is_founder_query(question):
        if "founder" in url or "about" in url or "our-board" in url:
            score += 10

    if is_program_query(question):
        if "program" in url or "about" in url:
            score += 8

    if is_volunteer_query(question):
        if "volunteer" in url or "new-page-96" in url:
            score += 25
        if "contact" in url:
            score += 8
        if "about" in url:
            score += 2
        if "/blogs" in url or ("new-page" in url and "new-page-96" not in url):
            score -= 12

    return score


def keyword_boost_search(question, max_results=8):
    question_words = tokenize(question)
    scored = []

    for chunk in CHUNKS:
        title = chunk.get("title", "")
        text = chunk.get("text", "")
        url = chunk.get("url", "")

        title_tokens = set(tokenize(title))
        text_tokens = set(tokenize(text))
        full_text = f"{title} {text} {url}".lower()

        score = 0

        for word in question_words:
            if word in title_tokens:
                score += 8
            if word in text_tokens:
                score += 4

        score += get_url_priority(url, question)

        if is_volunteer_query(question):
            if "volunteer" in full_text:
                score += 20
            if "get involved" in full_text:
                score += 16
            if "join us" in full_text:
                score += 12
            if "contact" in full_text:
                score += 6
            if "opportunit" in full_text:
                score += 8
            if "creative skillsets" in full_text:
                score += 8

        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [normalize_chunk(item[1]) for item in scored[:max_results]]


def rewrite_question_with_history(chat_history, current_question):
    if not chat_history:
        return current_question

    history_text = ""
    for turn in chat_history[-4:]:
        history_text += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"

    prompt = f"""
You are an expert query rewriting assistant.

Rewrite follow-up questions into standalone questions.

Rules:
- If vague (e.g., "what about eligibility?"), include previous topic.
- Preserve the exact meaning.
- Do NOT answer.
- Keep it concise.
- Return only the rewritten question.

Conversation:
{history_text}

Question:
{current_question}

Rewritten:
"""

    response = LLM.invoke(prompt)
    return response.content.strip() or current_question


def retrieve_context(question, k=10, score_threshold=1.35):
    candidates = []

    # 1. FAISS retrieval
    try:
        faiss_results = VECTOR_DB.similarity_search_with_score(question, k=k)
    except Exception:
        faiss_results = [(doc, None) for doc in VECTOR_DB.similarity_search(question, k=k)]

    for doc, distance in faiss_results:
        url = doc.metadata.get("url", "")
        title = doc.metadata.get("title", "")
        chunk_id = doc.metadata.get("chunk_id")

        # Lower FAISS distance is better
        if distance is not None and distance > score_threshold:
            continue

        base_score = 100
        if distance is not None:
            base_score = 100 - (distance * 20)

        total_score = base_score + get_url_priority(url, question)

        candidates.append({
            "text": doc.page_content,
            "title": title,
            "url": url,
            "chunk_id": chunk_id,
            "score": total_score
        })

    # 2. Keyword retrieval
    keyword_results = keyword_boost_search(question, max_results=8)
    for chunk in keyword_results:
        total_score = 40 + get_url_priority(chunk.get("url", ""), question)
        candidates.append({
            **chunk,
            "score": total_score
        })

    # 3. Deduplicate by chunk_id/url/text prefix
    deduped = []
    used_keys = set()

    for item in candidates:
        key = (
            item.get("chunk_id"),
            item.get("url"),
            item.get("text", "")[:120]
        )
        if key in used_keys:
            continue
        used_keys.add(key)
        deduped.append(item)

    # 4. Query-specific filtering
    filtered = []
    for item in deduped:
        url = (item.get("url") or "").lower()

        if is_definition_query(question):
            if "/blogs" in url or ("new-page" in url and "new-page-96" not in url) or "installation" in url or "exhibition" in url:
                continue

        if is_volunteer_query(question):
            if "/blogs" in url or "installation" in url or "exhibition" in url:
                continue

        filtered.append(item)

    # fallback if filtering removes too much
    if len(filtered) < 3:
        filtered = deduped

    # 5. Final sort
    filtered.sort(key=lambda x: x["score"], reverse=True)

    print("\n[DEBUG] Question:", question)
    print("[DEBUG] Top retrieval results:")
    for item in filtered[:6]:
        print(
            f"- score={item['score']:.2f} | "
            f"title={item.get('title')} | "
            f"url={item.get('url')}"
        )

    # 6. Return final docs
    final_docs = []
    used_chunk_ids = set()

    for item in filtered:
        cid = item.get("chunk_id")
        # allow docs without chunk_id too
        dedupe_key = cid if cid is not None else (item.get("url"), item.get("text", "")[:120])

        if dedupe_key in used_chunk_ids:
            continue
        used_chunk_ids.add(dedupe_key)

        final_docs.append({
            "text": item.get("text", ""),
            "title": item.get("title", "Unknown Title"),
            "url": item.get("url", "Unknown URL"),
            "chunk_id": cid
        })

        if len(final_docs) >= 4:
            break

    return final_docs


def build_prompt(question, docs, chat_history):
    context = "\n\n".join([
        f"Title: {d['title']}\nURL: {d['url']}\nContent: {d['text']}"
        for d in docs
    ])

    return f"""
You are a strict Think Round FAQ assistant.

Answer only from the context below.

Rules:
- Use only information explicitly supported by the context.
- Prefer the most relevant sources for the question.
- For broad questions like "What is Think Round?", prioritize homepage/about/mission content.
- For volunteering questions, if the context mentions volunteering but does not provide detailed steps, explain what is available and say that the site content does not show detailed signup steps.
- Do NOT hallucinate details.
- If nothing relevant exists, say exactly:
I don't know based on the provided information.

Question:
{question}

Context:
{context}
"""


def answer_question(question, chat_history=None):
    if chat_history is None:
        chat_history = []

    standalone = rewrite_question_with_history(chat_history, question)
    docs = retrieve_context(standalone)
    prompt = build_prompt(standalone, docs, chat_history)

    response = LLM.invoke(prompt)
    answer = response.content.strip()

    if not answer:
        answer = "I don't know based on the provided information."

    return answer, docs, standalone