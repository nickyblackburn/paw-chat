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
            "See you later, my brave pup!",
            "Hugggs, come back anytime!"
        ],
    },
    {
        "tag": "thanks",
        "patterns": [r"\b(thanks|thank you|ty|appreciate it)\b"],
        "keywords": ["thanks", "thank", "appreciate"],
        "responses": [
            "Anytime! I’ve got you. 💞",
            "You’re so welcome, angel.",
            "Anything for my puppy."
        ],
    },
    {
        "tag": "time",
        "patterns": [r"\b(what'?s|tell me) the time\b", r"\bcurrent time\b"],
        "keywords": ["time", "clock"],
        "responses": [],  # dynamic
    },
    {
        "tag": "date",
        "patterns": [r"\b(what'?s|tell me) the date\b", r"\btoday'?s date\b"],
        "keywords": ["date", "today"],
        "responses": [],  # dynamic
    },
    {
        "tag": "name_save",
        "patterns": [r"\b(my name is|i am|i'm)\s+([A-Za-z][A-Za-z\-']+)\b"],
        "keywords": ["name"],
        "responses": [],  # dynamic, we’ll acknowledge
    },
    {
        "tag": "help",
        "patterns": [r"\b(help|what can you do|commands)\b"],
        "keywords": ["help", "commands"],
        "responses": [
            "I can say hi/bye, remember your name, tell time/date, and answer a few basics.\nTry: 'hi', 'what time is it', 'my name is Luna', 'bye'.\nWe can add new skills so easily!"
        ],
    },
]

# Precompile regexes
for intent in INTENTS:
    intent["compiled"] = [re.compile(pat, re.I) for pat in intent["patterns"]]

# matches text via fuzzy search 
def fuzzy_match(text: str, samples: list[str], cutoff=0.8) -> bool:
    """If user text is close to any sample string."""
    text_norm = normalize(text)
    samples_norm = [normalize(s) for s in samples]
    match = difflib.get_close_matches(text_norm, samples_norm, n=1, cutoff=cutoff)
    return bool(match)

# matches users input 
def match_intent(user_text: str):
   
    for intent in INTENTS:
        for rx in intent["compiled"]:
            m = rx.search(user_text)
            if m:
                return intent, m

    # 2) quick keyword check
    text_simple = user_text.lower()
    for intent in INTENTS:
        if any(k in text_simple for k in intent["keywords"]):
            return intent, None

    # 3) fuzzy vs example phrases
    examples = []
    for intent in INTENTS:
        examples.extend(intent["keywords"])
    if fuzzy_match(user_text, examples, cutoff=0.85):
        # find which intent had that example
        for intent in INTENTS:
            if fuzzy_match(user_text, intent["keywords"], cutoff=0.85):
                return intent, None

    return None, None

# respoce generated 
def respond(intent, match, user_text):
    tag = intent["tag"]

    if tag == "time":
        now = datetime.now().strftime("%I:%M %p").lstrip("0")
        return f"It’s {now} right now ⏰"
    if tag == "date":
        today = datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {today} 📅"
    if tag == "name_save":
        # capture name from the pattern if we had a regex match
        name = None
        if match and match.groups():
            name = match.groups()[-1]
            memory["user_name"] = name
            return f"Got it, {name}! I’ll remember your name. 🐾"
        return "Tell me your name like: 'my name is Koda'!"
    if tag == "help":
        return random.choice(intent["responses"])
    if tag in ("greet", "thanks", "bye"):
        # personalize if we know their name
        base = random.choice(intent["responses"])
        if memory["user_name"]:
            return base.replace("!", f", {memory['user_name']}!")
        return base

    # fallback if something weird happens
    if intent["responses"]:
        return random.choice(intent["responses"])
    return "I feel a little confused, pup—can you say it another way? 🫣"

def banner():
    console.print(
        Panel.fit(
            "[bold magenta]Paw Chatbot[/bold magenta]\n"
            "[dim]Type 'help' to see options. Type 'quit' to exit.[/dim]",
            border_style="magenta",
        )
    )

def main():
    banner()
    while True:
        try:
            user = console.input("[bold cyan]You[/bold cyan]: ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Bye![/dim]")
            sys.exit(0)

        if not user:
            continue
        if user.lower() in {"quit", "exit"}:
            console.print("[dim]Shutting down. Hugs.[/dim]")
            break

        intent, match = match_intent(user)
        if intent:
            reply = respond(intent, match, user)
        else:
            reply = (
                "I’m not sure yet, but I’m learning! Try 'help', "
                "'what time is it', or 'my name is Luna'."
            )

        console.print(f"[bold green]Bot[/bold green]: {reply}")

if __name__ == "__main__":
    main()

