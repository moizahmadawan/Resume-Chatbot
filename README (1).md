# 🤖 Resume Chatbot (Python AI)

An AI chatbot that answers questions about a person's resume: skills, projects, education, experience and contact details. Works **fully offline** (no API key needed) and can optionally use the **Claude API** for more natural answers.

## How the AI works

```
User question
   │
   ├─ small-talk / intent rules (hello, thanks, bye)
   │
   ├─ query expansion (synonyms: "studied" → education, university)
   │
   ├─ TF-IDF vectorisation (unigrams + bigrams)
   ├─ cosine similarity against resume facts  → top matches
   │
   ├─ Offline mode : return the best matching facts
   └─ Claude mode  : send matches as context → natural, grounded answer
```

| Technique | Purpose |
|---|---|
| TF-IDF + cosine similarity | Find the resume facts most relevant to a question |
| Query expansion | Understand different wording of the same question |
| Similarity threshold | Say "not in resume" instead of guessing |
| RAG (optional) | LLM answers only from retrieved resume context |

## Project structure

```
resume-chatbot/
├── chatbot.py        # core AI engine + terminal chat
├── app.py            # Streamlit web chat UI
├── profile.json      # resume data (EDIT THIS)
├── requirements.txt
└── README.md
```

## Setup

```bash
pip install -r requirements.txt
```

**Terminal chat**
```bash
python chatbot.py
```

**Web UI**
```bash
streamlit run app.py
```

**Optional: Claude mode**
```bash
# Linux / macOS
export ANTHROPIC_API_KEY="your-key"
# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="your-key"
```
Restart the app; the header will show *Claude + retrieval*. Change the model with the `CLAUDE_MODEL` variable if needed. If the API fails, the bot falls back to offline mode automatically.

## Customise with your own data

Edit `profile.json`:
1. Replace the contact placeholders (email, LinkedIn, GitHub)
2. Add or change items in `chunks`. Each one is `{"topic": "...", "text": "..."}`
3. Keep each fact short and written in third person
4. Add new words people may use to `SYNONYMS` in `chatbot.py` if a question doesn't match

## Example questions

- Who is Moiz?
- What are his skills?
- Tell me about PET360
- What projects has he built?
- Does he have work experience?
- How can I contact him?

## Deploy for free (portfolio link)

1. Push this folder to GitHub
2. Go to **share.streamlit.io**, connect the repo and select `app.py`
3. (Optional) add `ANTHROPIC_API_KEY` in *Secrets* for Claude mode

## Future improvements
- Sentence embeddings (sentence-transformers) instead of TF-IDF
- Chat memory for follow-up questions
- Upload a PDF resume and auto-build `profile.json`
- Voice input and Urdu/Hinglish support

## Author
**Malik Moiz Ahmad Awan**, BS Computer Science, University of Gujrat
