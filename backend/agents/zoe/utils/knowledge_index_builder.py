#!/usr/bin/env python3
import json
import os

import pandas as pd
from dotenv import load_dotenv
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing in environment variables")

# Configuration (can be overridden via env vars)
CONTEXT_PATH = os.getenv("CONTEXT_TXT_PATH", "data/context.txt")
KNOWLEDGE_JSON_PATH = os.getenv("KNOWLEDGE_JSON_PATH", "data/knowledge_base.json")
EMPATHY_CSV_PATH = os.getenv("EMPATHY_CSV_PATH", "data/empathetic_dialogues_train.csv")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 300))
MAX_EMPATHY_EXAMPLES = int(os.getenv("MAX_EMPATHY_EXAMPLES", 500))
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "agents/zoe/chroma_db")

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
    """
    Load empathetic dialogues CSV and format into documents.
    """
    df = pd.read_csv(path)
    docs: list[Document] = []

    for _, row in df.head(max_examples).iterrows():
        situation = row.get("Situation", "")
        emotion = row.get("emotion", "")
        dialogue = row.get("empathetic_dialogues", "")
        response = row.get("labels", "")
        text = (
            f"Emotion: {emotion}\n"
            f"Situation: {situation}\n"
            f"Dialogue: {dialogue.strip()}\n"
            f"Agent Response: {response.strip()}"
        )
        docs.append(
            Document(
                page_content=text,
                metadata={
                    "source": "empathetic_dialogues",
                    "emotion": emotion,
                },
            )
        )
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


if __name__ == "__main__":
    build_chroma_index()
