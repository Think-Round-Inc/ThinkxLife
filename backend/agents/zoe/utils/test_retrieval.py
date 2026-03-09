import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "agents/zoe/chroma_db")

embeddings = OpenAIEmbeddings()  # uses OPENAI_API_KEY from .env
db = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings)

query = "I feel anxious. What can I do right now?"
docs = db.similarity_search(query, k=3)

print("\nTop matches:\n")
for i, d in enumerate(docs, 1):
    print(f"--- Result {i} ---")
    print("metadata:", d.metadata)
    print(d.page_content[:400])
    print()
