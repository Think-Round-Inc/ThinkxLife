import json
import os
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

INPUT_FILE = "data/thinkround_chunks.json"
VECTOR_DB_DIR = "data/vector_db"


def load_chunks():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def build_vector_db(chunks):
    texts = []
    metadatas = []

    for chunk in chunks:
        texts.append(chunk["text"])
        metadatas.append({
            "url": chunk["url"],
            "title": chunk["title"],
            "chunk_id": chunk["chunk_id"]
        })

    embeddings = OpenAIEmbeddings()

    print("Generating embeddings...")

    vector_db = FAISS.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas
    )

    return vector_db


if __name__ == "__main__":

    os.makedirs(VECTOR_DB_DIR, exist_ok=True)

    print("Loading chunks...")

    chunks = load_chunks()

    print(f"Total chunks: {len(chunks)}")

    vector_db = build_vector_db(chunks)

    vector_db.save_local(VECTOR_DB_DIR)

    print("\nVector database saved to:", VECTOR_DB_DIR)