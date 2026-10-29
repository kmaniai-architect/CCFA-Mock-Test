# CCFA Mock Test

Offline mock exam for the Claude Certified Associate (Foundations, CCAO-F) curriculum.

- `mock-exam/index.html` – the app (open directly in a browser; no server needed)
- `mock-exam/knowledge_base.json` – lesson passages used by the BM25 retriever
- `src/` – question bank (`q1.js`–`q7.js`), distractors, and the HTML template
- `text/` – plain-text lesson notes the knowledge base is built from
- `build.py` – rebuilds the app: `python build.py`

Questions are original practice items written from the study notes; they are not the real exam's question bank. Scores are estimates.
