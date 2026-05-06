# Think Round FAQ Bot (RAG-Based)

This folder contains the standalone RAG-based FAQ chatbot for Think Round.

The chatbot:

* Scrapes and processes Think Round website content
* Builds embeddings and a vector database
* Uses Retrieval-Augmented Generation (RAG)
* Supports conversation history
* Includes evaluator support for response quality testing

---

# Folder Structure

```text
faq-bot-rag/
├── app/
│   ├── api.py
│   ├── rag_chat.py
│   ├── ingest_site.py
│   ├── chunk_pages.py
│   ├── build_vector_db.py
│   ├── static_chat.html
│   └── static_chat.css
│
├── data/
│   ├── thinkround_pages.json
│   ├── thinkround_chunks.json
│   └── vector_db/
│
├── requirements.txt
└── README.md
```

---

# 1. Setup

Open terminal inside the `faq-bot-rag` folder.

## Create Virtual Environment

### Windows

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 3. Add OpenAI API Key

Create a `.env` file inside `faq-bot-rag/`

```env
OPENAI_API_KEY=your_openai_api_key_here
```

---

# 4. Build the RAG Data Pipeline

Run the following commands in order.

---

## Step 1 — Scrape Website Data

```bash
python -m app.ingest_site
```

This creates:

```text
data/thinkround_pages.json
```

---

## Step 2 — Chunk the Data

```bash
python -m app.chunk_pages
```

This creates:

```text
data/thinkround_chunks.json
```

---

## Step 3 — Build Vector Database

```bash
python -m app.build_vector_db
```

This creates:

```text
data/vector_db/
```

---

# 5. Run the FAQ Bot

Start the FastAPI backend:

```bash
uvicorn app.api:app --reload
```

Server URL:

```text
http://127.0.0.1:8000
```

Swagger API Docs:

```text
http://127.0.0.1:8000/docs
```

---

# 6. Open the Chat UI

Open the file below in your browser:

```text
app/static_chat.html
```

Make sure the FastAPI server is already running.

---

# 7. Example API Request

POST request to:

```text
http://127.0.0.1:8000/chat
```

Request Body:

```json
{
  "question": "What is Think Round?",
  "session_id": "test-session"
}
```

---

# Running Evaluators

The FAQ evaluators are located inside the ThinkLife backend.

Go to the backend folder:

```bash
cd backend
```

---

# 1. Activate Virtual Environment

### Windows

```powershell
.\venv\Scripts\activate
```

---

# 2. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

---

# 3. Add OpenAI API Key

Create/update `.env`

```env
OPENAI_API_KEY=your_openai_api_key_here
```

---

# 4. Run FAQ Evaluators (Live Mode)

Run:

```bash
python -m evaluators.runner --bot faq --input evaluators/test_cases.json --live
```

If Python version issues occur on Windows:

```powershell
.\venv\Scripts\python.exe -m evaluators.runner --bot faq --input evaluators/test_cases.json --live
```

---

# Evaluators Included

The evaluator framework checks:

* Safety / Harm
* Hallucination Risk
* Instruction Following
* Empathy & Tone
* Readability
* Retrieval Precision / Recall
* Faithfulness
* Citation Quality
* FAQ Exactness
* Abstention Handling
* Policy Consistency

---

# Common Issues

## OPENAI_API_KEY not set

If you see:

```text
OPENAI_API_KEY is not set
```

Add your API key to `.env`

---

## Python 2 Error

If terminal shows:

```text
C:\Python27\
```

Use the venv Python directly:

```powershell
.\venv\Scripts\python.exe
```

---

## Missing Vector Database

If retrieval fails:

Rebuild vector DB:

```bash
python -m app.build_vector_db
```

---

# Current Features

* RAG-based retrieval
* Multi-turn conversation history
* Citation-aware answers
* Hybrid retrieval scoring
* Evaluator integration
* FastAPI backend
* Static frontend UI

---

# Current Known Improvements in Progress

* Better empathy/tone handling
* Improved citation consistency
* Expanded Think Round page scraping
* Multi-provider LLM support (OpenAI/Gemini abstraction)
* Improved evaluator scores
