# mainfile
## base file for basic chatbot 

import re, random, sys
from datetime import date
import difflib
import spacy
from rich.console import Console
from rich.panel import Panel

console = Console()

#npl pipeline 
npl = spacey.load("en_core_web_sm",exclude=["ner","parser","textcat"])


# normalizes text
def normalize(text: str) -> str:
    doc = nlp(text.lower().strip())
    # keep only letters/numbers; lemmatize for simpler matching
    tokens = []
    for t in doc:
        if t.is_space or t.is_punct:
            continue
        lemma = t.lemma_.strip()
        if lemma:
            tokens.append(lemma)
    return " ".join(tokens)

# ---------- “Memory” (tiny, in-process) ----------
memory = {
    "user_name": None,
    "last_intent": None,
}

# ---------- Intents (rules + examples + responses) ----------
INTENTS = [
    {
        "tag": "greet",
        "patterns": [r"\b(hi|hey|hello|yo|sup)\b", r"\bgood (morning|afternoon|evening)\b"],
        "keywords": ["hi", "hello", "hey", "yo", "sup"],
        "responses": [
            "Hiii, puppy! 🐶 How can I help today?",
            "Hey sweetpea—what’s up? 💖",
            "Hello, cutie! Want to build or fix something?"
        ],
    },
    {
        "tag": "bye",
        "patterns": [r"\b(bye|goodbye|see ya|later|gtg)\b"],
        "keywords": ["bye", "goodbye", "later", "gtg"],
        "responses": [
            "Byeee—proud of you. 🫶",
            "See you],
            },

# Precompile regexes
for intent in INTENTS:
    intent["compiled"] = [re.compile(pat, re.I) for pat in intent["patterns"]]

