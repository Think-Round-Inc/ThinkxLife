import chromadb
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "chroma_db"
client = chromadb.PersistentClient(path=str(DB_PATH))

col = client.get_collection("langchain")

res = col.query(
    query_texts=["You are Zoe ThinkLife trauma-informed empathetic AI companion"],
    n_results=3
)

print("Top matches:")
for doc, meta in zip(res["documents"][0], res["metadatas"][0]):
    print("metadata:", meta)
    print(doc[:250])
    print("----")
