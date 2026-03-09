import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

DB_PATH = Path(__file__).resolve().parent.parent / "chroma_db"

emb = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

vs = Chroma(
    persist_directory=str(DB_PATH),
    embedding_function=emb,
    collection_name="langchain",
)

query = "You are Zoe, ThinkLife’s trauma-informed empathetic AI companion."
docs = vs.similarity_search(query, k=3)

print("Top matches:")
for d in docs:
    print("metadata:", d.metadata)
    print(d.page_content[:250])
    print("----")
