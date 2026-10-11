"""
Resume Chatbot - core engine
----------------------------
AI techniques:
  * TF-IDF vectorisation (unigrams + bigrams) of resume facts
  * Cosine-similarity retrieval  (the "R" in RAG)
  * Rule-based small-talk / intent handling
  * Optional LLM mode (Claude API): retrieved facts are passed as context
    so the answer is natural but still grounded in the resume.

Run in terminal :  python chatbot.py
Run web UI      :  streamlit run app.py
"""
import json
import os
import random
import re
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

PROFILE_PATH = Path(__file__).with_name("profile.json")

# Simple query expansion: user word -> words that appear in the resume
SYNONYMS = {
    "study": "education university degree BS",
    "studied": "education university degree BS",
    "degree": "education university BS",
    "college": "education university",
    "qualification": "education degree university",
    "tech": "skills frontend backend languages",
    "technologies": "skills frontend backend languages",
    "stack": "skills frontend backend",
    "know": "skills",
    "good": "skills",
    "job": "experience internship goals",
    "work": "experience internship projects",
    "worked": "experience internship",
    "company": "experience internship",
    "intern": "internship experience",
    "built": "projects overview",
    "made": "projects overview",
    "created": "projects overview",
    "portfolio": "projects overview",
    "ai": "AI ML Gemini TensorFlow",
    "ml": "AI ML machine learning TensorFlow",
    "email": "contact",
    "phone": "contact",
    "hire": "contact experience skills",
    "reach": "contact",
    "linkedin": "contact",
    "github": "contact",
    "startup": "Blissful Art founder",
    "business": "Blissful Art startup",
    "leader": "leadership Project Manager society",
    "future": "career goals",
    "plan": "career goals",
    "plans": "career goals",
    "from": "location Gujrat Pakistan",
    "live": "location Gujrat Pakistan",
    "where": "location Gujrat Pakistan",
    "language": "languages programming",
    "languages": "programming languages",
    "cpp": "C++",
    "python": "languages AI",
    "who": "about",
    "projects": "projects overview",
    "project": "projects overview",
}

GREETINGS = {"hi", "hello", "hey", "salam", "assalamualaikum", "hola", "yo"}
THANKS = {"thanks", "thank", "thankyou", "shukriya", "thx"}
BYE = {"bye", "goodbye", "exit", "quit", "khuda"}


class ResumeBot:
    def __init__(self, profile_path=PROFILE_PATH, threshold=0.10):
        with open(profile_path, encoding="utf-8") as f:
            self.profile = json.load(f)
        self.chunks = self.profile["chunks"]
        self.name = self.profile.get("short_name", self.profile["name"])
        self.threshold = threshold
        docs = [f'{c["topic"]}. {c["text"]}' for c in self.chunks]
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english",
                                          sublinear_tf=True)
        self.matrix = self.vectorizer.fit_transform(docs)
        self.llm = self._init_llm()

    # ---------------- LLM (optional) ----------------
    def _init_llm(self):
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            return None
        try:
            import anthropic
            return anthropic.Anthropic(api_key=key)
        except Exception:
            return None

    @property
    def mode(self):
        return "Claude + retrieval" if self.llm else "Offline (TF-IDF retrieval)"

    # ---------------- NLP helpers ----------------
    @staticmethod
    def _tokens(text):
        return re.findall(r"[a-z+#]+", text.lower())

    def _expand(self, query):
        extra = [SYNONYMS[t] for t in self._tokens(query) if t in SYNONYMS]
        return query + " " + " ".join(extra)

    def retrieve(self, query, k=3):
        """Return top-k (score, chunk) pairs by cosine similarity."""
        vec = self.vectorizer.transform([self._expand(query)])
        scores = cosine_similarity(vec, self.matrix).ravel()
        order = scores.argsort()[::-1][:k]
        return [(float(scores[i]), self.chunks[i]) for i in order]

    # ---------------- answering ----------------
    def small_talk(self, query):
        toks = set(self._tokens(query))
        if toks & GREETINGS and len(toks) <= 3:
            return (f"Hello! I'm {self.name}'s resume assistant. "
                    f"Ask me about his skills, projects, education or experience.")
        if toks & THANKS:
            return "You're welcome! Ask me anything else about " + self.name + "."
        if toks & BYE and len(toks) <= 2:
            return "Goodbye! Have a great day."
        if {"who", "are", "you"} <= toks or {"your", "name"} <= toks:
            return (f"I'm an AI chatbot built in Python. I answer questions about "
                    f"{self.profile['name']} using his resume data.")
        return None

    def answer(self, query):
        query = query.strip()
        if not query:
            return "Please type a question."
        talk = self.small_talk(query)
        if talk:
            return talk

        hits = self.retrieve(query, k=4)
        best = hits[0][0]
        if best < self.threshold:
            return ("I couldn't find that in the resume. Try asking about skills, "
                    "projects, education, experience or contact details.")

        # keep only chunks close to the best match
        picked = [c for s, c in hits if s >= max(self.threshold, best * 0.55)][:3]

        if self.llm:
            try:
                return self._llm_answer(query, picked)
            except Exception:
                pass  # fall back to offline answer
        return self._offline_answer(picked)

    @staticmethod
    def _offline_answer(chunks):
        if len(chunks) == 1:
            return chunks[0]["text"]
        return "\n".join(f"- {c['text']}" for c in chunks)

    def _llm_answer(self, query, chunks):
        context = "\n".join(f"- [{c['topic']}] {c['text']}" for c in chunks)
        system = (f"You are a friendly assistant on {self.profile['name']}'s portfolio. "
                  "Answer ONLY using the context given. Be concise (max 4 sentences), "
                  "refer to him in the third person, and if the context doesn't "
                  "contain the answer say you don't have that information.")
        msg = self.llm.messages.create(
            model=os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5"),
            max_tokens=400,
            system=system,
            messages=[{"role": "user",
                       "content": f"Context:\n{context}\n\nQuestion: {query}"}],
        )
        return msg.content[0].text.strip()

    def suggestions(self):
        return self.profile.get("suggested_questions", [])


def main():
    bot = ResumeBot()
    print(f"=== {bot.profile['name']} - Resume Chatbot ===")
    print(f"Mode: {bot.mode}   (type 'exit' to quit)\n")
    print("Try:", random.choice(bot.suggestions()), "\n")
    while True:
        try:
            q = input("You : ")
        except (EOFError, KeyboardInterrupt):
            break
        if q.strip().lower() in {"exit", "quit"}:
            print("Bot : Goodbye!")
            break
        print("Bot :", bot.answer(q), "\n")


if __name__ == "__main__":
    main()
