import json
import pandas as pd

CSV_PATH = "data/20220401_counsel_chat.csv"
OUT_JSON = "data/knowledge_base.json"

MIN_ANSWER_CHARS = 200   # you can lower to 80 for smaller answers
LIMIT = None             # set e.g. 2000 for quick test

def main():
    df = pd.read_csv(CSV_PATH)

    # Keep only needed columns (your dataset has these)
    keep = ["questionTitle", "questionText", "topic", "answerText", "upvotes", "views"]
    df = df[[c for c in keep if c in df.columns]].copy()

    df["questionTitle"] = df["questionTitle"].fillna("").astype(str)
    df["questionText"]  = df["questionText"].fillna("").astype(str)
    df["topic"]         = df["topic"].fillna("general").astype(str)
    df["answerText"]    = df["answerText"].fillna("").astype(str)
    df["upvotes"]       = df.get("upvotes", 0)

    # Best answer per questionTitle: highest upvotes, then longest answer
    df["answer_len"] = df["answerText"].str.len()
    df = df.sort_values(["questionTitle", "upvotes", "answer_len"], ascending=[True, False, False])
    df = df.drop_duplicates(subset=["questionTitle"], keep="first")

    # Filter tiny answers
    df = df[df["answerText"].str.len() >= MIN_ANSWER_CHARS]

    if LIMIT is not None:
        df = df.head(LIMIT)

    kb = []
    for _, r in df.iterrows():
        title = r["questionTitle"].strip()
        details = r["questionText"].strip()
        topic = (r["topic"].strip() or "general")
        ans = r["answerText"].strip()

        question = title if not details else f"{title}\n\nDetails: {details}"

        kb.append({
            "question": question,
            "answer": ans,
            "category": topic
        })

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(kb, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(kb)} items to {OUT_JSON}")

if __name__ == "__main__":
    main()
