#!/usr/bin/env python3
import json
import os

import pandas as pd
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from datasets import load_dataset
import chromadb
from chromadb.utils import embedding_functions

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing in environment variables")

# Configuration (can be overridden via env vars)
CONTEXT_PATH = os.getenv("CONTEXT_TXT_PATH", "data/context.txt")
KNOWLEDGE_JSON_PATH = os.getenv("KNOWLEDGE_JSON_PATH", "data/knowledge_base.json")
EMPATHY_CSV_PATH = os.getenv("EMPATHY_CSV_PATH", "data/empathetic_dialogues_train.csv")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 800))
MAX_EMPATHY_EXAMPLES = int(os.getenv("MAX_EMPATHY_EXAMPLES", 500))
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "agents/zoe/chroma_db")
ALLOWED_EMOTIONS = {
    "sad", "anxious", "afraid", "angry", "lonely",
    "guilty", "ashamed", "depressed", "stressed"
}

# Initialize embedding model
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)


def load_context_txt(path: str, chunk_size: int = CHUNK_SIZE) -> list[Document]:
    """
    Load a plain text file and split into chunks.
    """
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return [
        Document(
            page_content=text[i : i + chunk_size],
            metadata={"source": os.path.basename(path)},
        )
        for i in range(0, len(text), chunk_size)
    ]


def load_knowledge_json(path: str, chunk_size: int = CHUNK_SIZE) -> list[Document]:
    """
    Load JSON knowledge base of Q&A and split answers into chunks.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    docs: list[Document] = []
    for item in data:
        question = item.get("question", "")
        answer = item.get("answer", "")
        category = item.get("category", "general")
        for i in range(0, len(answer), chunk_size):
            chunk = answer[i : i + chunk_size]
            docs.append(
                Document(
                    page_content=f"{question}\n{chunk}",
                    metadata={"source": "knowledge_base", "category": category},
                )
            )
    return docs


def load_empathy_docs(
    path: str = EMPATHY_CSV_PATH, max_examples: int = MAX_EMPATHY_EXAMPLES
) -> list[Document]:
    df = pd.read_csv(path)
    docs: list[Document] = []

    for _, row in df.iterrows():
        situation = str(row.get("Situation", "")).strip()
        emotion = str(row.get("emotion", "")).strip().lower()
        dialogue_raw = str(row.get("empathetic_dialogues", "")).strip()
        response = str(row.get("labels", "")).strip()

        # ✅ Filter: only keep emotions Zoe should use
        if emotion not in ALLOWED_EMOTIONS:
            continue

        # Clean/structure the dialogue
        customer_text = dialogue_raw
        if "Customer :" in dialogue_raw:
            customer_text = dialogue_raw.split("Customer :", 1)[1].strip()
        if "\nAgent :" in customer_text:
            customer_text = customer_text.split("\nAgent :", 1)[0].strip()

        # ✅ Basic quality filters (optional but recommended)
        if len(customer_text) < 5 or len(response) < 5:
            continue

        text = (
            f"Emotion: {emotion}\n"
            f"Situation: {situation}\n"
            f"User said: {customer_text}\n"
            f"Zoe-style response example: {response}"
        )

        docs.append(
            Document(
                page_content=text,
                metadata={"source": "empathetic_dialogues", "emotion": emotion},
            )
        )

        # ✅ stop when we collected enough good examples
        if len(docs) >= max_examples:
            break

    return docs




def build_chroma_index():
    """
    Load all document sources and build a fresh Chroma vectorstore index.
    """
    # Remove old DB directory to avoid schema mismatch
    if os.path.exists(CHROMA_DB_DIR):
        print(
            f"Removing existing Chroma DB at '{CHROMA_DB_DIR}' "
            "to avoid schema issues..."
        )
        try:
            import shutil

            shutil.rmtree(CHROMA_DB_DIR)
        except Exception as e:
            print(f"Warning: could not remove old DB: {e}")

    print("Loading context documents...")
    context_docs = load_context_txt(CONTEXT_PATH)
    print(f"Loaded {len(context_docs)} context chunks.")

    print("Loading knowledge base documents...")
    kb_docs = load_knowledge_json(KNOWLEDGE_JSON_PATH)
    print(f"Loaded {len(kb_docs)} knowledge chunks.")

    print("Loading empathy documents...")
    empathy_docs = load_empathy_docs()
    print(f"Loaded {len(empathy_docs)} empathy examples.")

    all_docs = context_docs + kb_docs + empathy_docs
    print(f"Total documents to index: {len(all_docs)}.")

    # Create and save Chroma vectorstore
    Chroma.from_documents(
        documents=all_docs, embedding=embeddings, persist_directory=CHROMA_DB_DIR
    )

    print(f"Chroma index built and saved to '{CHROMA_DB_DIR}'.")

def build_counselchat_kb(limit=500):
    # 1) download dataset automatically
    ds = load_dataset("nbertagnolli/counsel-chat", split="train")

    # 2) keep only first rows (for testing)
    ds = ds.select(range(min(limit, len(ds))))

    # 3) open your chroma folder
    client = chromadb.PersistentClient(path="agents/zoe/chroma_db")

    # 4) embeddings (local)
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # 5) create collection
    col = client.get_or_create_collection(
        name="zoe_counsel_chat",
        embedding_function=embed_fn
    )

    # 6) save rows
    ids, docs = [], []
    for i, row in enumerate(ds):
        q = (row.get("questionText") or row.get("questionTitle") or "").strip()
        a = (row.get("answerText") or "").strip()
        text = f"Q: {q}\nA: {a}"
        ids.append(f"cc_{i}")
        docs.append(text)

    col.upsert(ids=ids, documents=docs)
    print("DONE. Saved:", len(ids), "rows into chroma_db")

if __name__ == "__main__":
    build_chroma_index()
