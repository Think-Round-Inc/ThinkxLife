import json
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter


INPUT_FILE = "data/thinkround_pages.json"
OUTPUT_FILE = "data/thinkround_chunks.json"


def load_pages():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def chunk_pages(pages):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""]
    )

    chunks = []

    for page_idx, page in enumerate(pages):
        page_text = page.get("text", "").strip()
        if not page_text:
            continue

        split_texts = splitter.split_text(page_text)

        for chunk_idx, chunk_text in enumerate(split_texts):
            chunks.append({
                "chunk_id": f"page{page_idx}_chunk{chunk_idx}",
                "text": chunk_text,
                "url": page.get("url", ""),
                "title": page.get("title", ""),
                "page_index": page_idx,
                "chunk_index": chunk_idx
            })

    return chunks


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    pages = load_pages()
    chunks = chunk_pages(pages)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"Loaded pages: {len(pages)}")
    print(f"Generated chunks: {len(chunks)}")
    print(f"Saved chunks to {OUTPUT_FILE}")

    if chunks:
        print("\n--- SAMPLE CHUNK ---")
        print("Chunk ID:", chunks[0]["chunk_id"])
        print("Title:", chunks[0]["title"])
        print("URL:", chunks[0]["url"])
        print("Text preview:", chunks[0]["text"][:500])