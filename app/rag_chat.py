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


def load_vector_db():
    embeddings = OpenAIEmbeddings()
    vector_db = FAISS.load_local(
        VECTOR_DB_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )
    return vector_db


def load_chunks():
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def tokenize(text):
    words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


def keyword_boost_search(question, max_results=8):
    question_lower = question.lower()
    question_words = tokenize(question)
    chunks = load_chunks()

    scored = []
    for chunk in chunks:
        title = chunk.get("title", "").lower()
        url = chunk.get("url", "").lower()
        text = chunk.get("text", "").lower()

        title_tokens = set(tokenize(title))
        url_tokens = set(tokenize(url.replace("-", " ").replace("/", " ")))
        text_tokens = set(tokenize(text))

        score = 0

        for word in question_words:
            if word in title_tokens:
                score += 6
            if word in url_tokens:
                score += 5
            if word in text_tokens:
                score += 2

        combined_text = f"{title} {url} {text}"

        if "volunteer" in question_lower:
            if "volunteer" in combined_text:
                score += 30
            if "opportunit" in combined_text:
                score += 12
            if "interested in volunteering" in combined_text:
                score += 18
            if "contact us" in combined_text:
                score += 6

        if "program" in question_lower or "offer" in question_lower:
            if "program" in combined_text:
                score += 12
            if "center for the human family" in combined_text:
                score += 8
            if "keep" in combined_text or "intergenerational afterschool program" in combined_text:
                score += 8

        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:max_results]]


def rewrite_question_with_history(chat_history, current_question):
    if not chat_history:
        return current_question

    history_text = ""
    for turn in chat_history[-6:]:
        history_text += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = f"""
You are helping convert a follow-up user question into a standalone question.

Given the conversation history and the latest user question, rewrite the latest question
so it is fully self-contained and clear on its own.

If the latest question is already standalone, return it unchanged.

Conversation history:
{history_text}

Latest user question:
{current_question}

Return only the rewritten standalone question.
"""

    response = llm.invoke(prompt)
    return response.content.strip()


def normalize_chunk(chunk):
    return {
        "text": chunk.get("text", ""),
        "title": chunk.get("title", "Unknown Title"),
        "url": chunk.get("url", "Unknown URL"),
        "chunk_id": chunk.get("chunk_id")
    }


def retrieve_context(question, k=10):
    vector_db = load_vector_db()

    faiss_docs = vector_db.similarity_search(question, k=k)
    boosted_chunks = keyword_boost_search(question, max_results=8)

    combined = []
    seen_chunk_ids = set()

    for chunk in boosted_chunks:
        chunk_id = chunk.get("chunk_id")
        if chunk_id not in seen_chunk_ids:
            combined.append(normalize_chunk(chunk))
            seen_chunk_ids.add(chunk_id)

    for doc in faiss_docs:
        chunk_id = doc.metadata.get("chunk_id")
        if chunk_id not in seen_chunk_ids:
            combined.append({
                "text": doc.page_content,
                "title": doc.metadata.get("title", "Unknown Title"),
                "url": doc.metadata.get("url", "Unknown URL"),
                "chunk_id": chunk_id
            })
            seen_chunk_ids.add(chunk_id)

    if "volunteer" in question.lower():
        chunks = load_chunks()
        volunteer_candidates = []
        for chunk in chunks:
            combined_text = (
                chunk.get("title", "") + " " +
                chunk.get("url", "") + " " +
                chunk.get("text", "")
            ).lower()

            if (
                "volunteer" in combined_text
                or "interested in volunteering" in combined_text
                or "opportunit" in combined_text
            ):
                volunteer_candidates.append(chunk)

        volunteer_candidates.sort(
            key=lambda c: (
                "volunteer" not in c.get("title", "").lower(),
                "volunteer" not in c.get("text", "").lower()
            )
        )

        for chunk in volunteer_candidates:
            chunk_id = chunk.get("chunk_id")
            if chunk_id not in seen_chunk_ids:
                combined.insert(0, normalize_chunk(chunk))
                seen_chunk_ids.add(chunk_id)
                break

    print("\n[DEBUG] Retrieved chunk titles:")
    for d in combined[:8]:
        print("-", d["title"])

    return combined[:8]


def build_prompt(question, docs, chat_history):
    context_parts = []
    for i, doc in enumerate(docs, start=1):
        context_parts.append(
            f"Source {i}:\n"
            f"Title: {doc['title']}\n"
            f"URL: {doc['url']}\n"
            f"Content: {doc['text']}\n"
        )

    context = "\n\n".join(context_parts)

    history_text = ""
    for turn in chat_history[-6:]:
        history_text += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"

    prompt = f"""
You are a strict Think Round FAQ assistant.

RULES:
1. Answer ONLY using the provided context.
2. Use ONLY information that is explicitly written in the context.
3. Do NOT infer, assume, or add extra details.
4. If possible, reuse exact phrases from the context.
5. Do NOT add suggestions like "contact them" unless explicitly stated.
6. Do NOT add emails, phone numbers, links, or contact details unless they appear in the context for this answer.
7. If the answer is not clearly present, say exactly:
   "I don't know based on the provided information."

STYLE:
- Be concise and natural
- Prefer 1–3 sentences
- Stay very close to the wording in the context
- Do not include a sources section
- Return only the answer text

Conversation history:
{history_text}

Current user question:
{question}

Context:
{context}
"""
    return prompt


def extract_safe_volunteer_answer(docs):
    for doc in docs:
        text = doc.get("text", "")
        sentences = re.split(r"(?<=[.!?])\s+", text)

        selected = []
        for sentence in sentences:
            s = sentence.strip()
            s_lower = s.lower()

            if not s:
                continue

            if "volunteer" in s_lower or "opportunit" in s_lower:
                selected.append(s)

            if len(selected) >= 2:
                break

        if selected:
            return " ".join(selected)

    return "I don't know based on the provided information."


def is_hallucinated_contact_answer(response_text):
    lowered = response_text.lower()
    forbidden_patterns = [
        "@",
        "email",
        "contact them",
        "contact us",
        "reach out",
        "phone",
        "call",
        "info@"
    ]
    return any(pattern in lowered for pattern in forbidden_patterns)


def answer_question(question, chat_history=None):
    if chat_history is None:
        chat_history = []

    standalone_question = rewrite_question_with_history(chat_history, question)
    docs = retrieve_context(standalone_question, k=10)
    prompt = build_prompt(standalone_question, docs, chat_history)

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    response = llm.invoke(prompt)
    response_text = response.content.strip()

    if "volunteer" in standalone_question.lower() and is_hallucinated_contact_answer(response_text):
        response_text = extract_safe_volunteer_answer(docs)

    if not response_text:
        response_text = "I don't know based on the provided information."

    return response_text, docs, standalone_question


if __name__ == "__main__":
    print("Think Round Conversational FAQ Bot")
    print("Type 'exit' to quit.\n")

    chat_history = []

    while True:
        question = input("You: ").strip()

        if question.lower() == "exit":
            print("Goodbye!")
            break

        answer, docs, rewritten = answer_question(question, chat_history)

        print("\n--- REWRITTEN QUESTION ---")
        print(rewritten)

        print("\nBot:")
        print(answer)

        print("\n--- SOURCES RETRIEVED ---")
        for i, doc in enumerate(docs, start=1):
            print(f"{i}. {doc['title']} - {doc['url']}")
        print()

        chat_history.append({
            "user": question,
            "assistant": answer
        })