"""
InnSight RAG chatbot — LLM-first architecture.

Every user message is routed through the LLM with:
  1.  RAG context   (always, from FAISS vector store)
  2.  Structured data (when city + month are known, from MongoDB)
  3.  Conversation history (last N turns for multi-turn memory)

The LLM handles conversation flow naturally — no hardcoded responses.
"""

import os
import re
import string
from datetime import date

from dateutil.relativedelta import relativedelta
from groq import Groq

from config import Config
from services.travel_planner import recommend_neighborhoods
from utils.db import get_db

# --- RAG import (graceful: chatbot works without it) ----------------------
try:
    from rag.retriever import retrieve_context, format_rag_context

    _RAG_AVAILABLE = True
except ImportError:
    _RAG_AVAILABLE = False

    def retrieve_context(*_a, **_kw):  # noqa: D103
        return []

    def format_rag_context(*_a, **_kw):  # noqa: D103
        return ""


# =========================================================================
# Constants
# =========================================================================

KNOWN_CITIES = Config.ALLOWED_CITIES  # {"amsterdam", "rome", …}
CITY_LIST_DISPLAY = ", ".join(c.title() for c in sorted(KNOWN_CITIES))

MONTHS = {
    "january": 1, "jan": 1, "february": 2, "feb": 2,
    "march": 3, "mar": 3, "april": 4, "apr": 4,
    "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
    "august": 8, "aug": 8, "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10, "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}

MONTH_REGEX = (
    r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|"
    r"nov(?:ember)?|dec(?:ember)?"
)

# Maximum conversation turns to send to the LLM
MAX_HISTORY_TURNS = 8


# =========================================================================
# System prompt — the personality and rules for the chatbot
# =========================================================================

SYSTEM_PROMPT = f"""\
You are **InnSight**, a friendly, knowledgeable travel assistant that helps
travelers discover neighborhoods and plan stays in these cities:
{CITY_LIST_DISPLAY}.

## Your personality
- Warm, concise, and enthusiastic (like a well-traveled friend).
- Keep answers to 4–8 lines unless the user asks for detail.
- Use emoji sparingly (1–2 per message max).

## Rules
1. **Use ONLY the provided context.**  You have two information sources:
   - CONTEXT CHUNKS: guest reviews and travel guide excerpts retrieved via
     semantic search.  Cite them naturally ("guests mention …",
     "our guide notes …") but never quote source numbers.
   - STRUCTURED DATA: occupancy rates and sentiment scores from our database.
2. **Do not invent** places, prices, distances, opening hours, or any fact
   not present in the context.  If you don't know, say so honestly.
3. If you don't yet know the **city** or **travel month**, ask for them
   naturally — but still answer any general question you can using the
   context (e.g. "which cities have beaches?" is answerable immediately).
4. When you have enough info for a recommendation, suggest 2–3
   neighborhoods with brief reasons drawn from context/data.
5. Ask at most **one** follow-up question per response.
6. The destination city, once established, is **fixed** — do not change it
   unless the user explicitly asks.
7. You only cover the cities listed above.  If someone asks about another
   city, politely explain your coverage.
"""


# =========================================================================
# Lightweight extraction helpers (kept from original code)
# =========================================================================

def extract_city(text: str) -> str | None:
    """Try to pull a supported city name from the user text."""
    t = (text or "").lower()
    # Direct match
    for c in KNOWN_CITIES:
        if re.search(rf"\b{re.escape(c)}\b", t):
            return c
    # Patterns like "go to X", "visit X"
    patterns = [
        r"\bgo(?:ing)? to\s+([a-z]+)\b",
        r"\bvisit\s+([a-z]+)\b",
        r"\btravel(?:ing)? to\s+([a-z]+)\b",
        r"\bstay(?:ing)? in\s+([a-z]+)\b",
        r"\blet'?s say\s+([a-z]+)\b",
    ]
    for p in patterns:
        m = re.search(p, t)
        if m and m.group(1) in KNOWN_CITIES:
            return m.group(1)
    return None


def parse_month(text: str) -> str | None:
    """Extract a YYYY-MM string from natural language."""
    t = (text or "").lower()

    # "march 2026"
    m = re.search(rf"\b({MONTH_REGEX})\b\s*(\d{{4}})", t)
    if m:
        return _month_str(MONTHS[m.group(1)], int(m.group(2)))

    # "next month"
    if "next month" in t:
        nm = date.today() + relativedelta(months=1)
        return nm.strftime("%Y-%m")

    # bare month name — assume next occurrence
    m = re.search(rf"\b({MONTH_REGEX})\b", t)
    if m:
        target = MONTHS[m.group(1)]
        today = date.today()
        year = today.year if target >= today.month else today.year + 1
        return _month_str(target, year)

    return None


def _month_str(month_num: int, year: int) -> str:
    return f"{year:04d}-{month_num:02d}"


def normalize_month(raw: str | None) -> str | None:
    if not raw:
        return None
    raw = raw.strip()
    if re.fullmatch(r"\d{4}-\d{2}", raw):
        return raw
    return parse_month(raw)


def extract_preferences(text: str) -> set[str]:
    t = (text or "").lower()
    prefs: set[str] = set()
    if any(w in t for w in ["beach", "sea", "coast"]):
        prefs.add("beach")
    if any(w in t for w in ["warm", "sun", "sunny"]):
        prefs.add("warm")
    if any(w in t for w in ["no beach", "not a beach", "avoid beach"]):
        prefs.add("no_beach")
    return prefs


def month_minus_one_year(ym: str) -> str:
    y, m = ym.split("-")
    return f"{int(y) - 1:04d}-{int(m):02d}"


# =========================================================================
# Anti-repeat helpers
# =========================================================================

_PUNCT_TABLE = str.maketrans("", "", string.punctuation)


def _norm(s: str) -> str:
    s = (s or "").lower().strip().translate(_PUNCT_TABLE)
    return re.sub(r"\s+", " ", s).strip()


def _jaccard(a: str, b: str) -> float:
    wa, wb = set(_norm(a).split()), set(_norm(b).split())
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / max(1, len(wa | wb))


# =========================================================================
# Main entry point
# =========================================================================

def chat_travel_recommendation(
    message: str,
    city: str | None = None,
    month: str | None = None,
    fallback: str = "last_year",
    context: dict | None = None,
    history: list[dict] | None = None,
):
    """Process a chat message and return a response.

    Args:
        message:  the user's latest message
        city:     city selected in the UI (if any)
        month:    month selected in the UI (if any)
        fallback: occupancy fallback strategy
        context:  conversation context dict (persisted across turns)
        history:  list of {"role": "user"|"assistant", "content": "..."} turns
    """
    context = context or {}
    history = history or []
    user_message = (message or "").strip()
    t = user_message.lower()

    # ------------------------------------------------------------------
    # 1. Lightweight extraction — update context
    # ------------------------------------------------------------------
    detected_city = (city or "").strip().lower() or extract_city(t)
    if detected_city and detected_city in KNOWN_CITIES:
        context["city"] = detected_city

    detected_month = normalize_month(month) or parse_month(user_message)
    if detected_month:
        context["month"] = detected_month

    # Preference tracking
    if re.search(r"\b(apartment|apartments)\b", t):
        context["lodging_type"] = "apartment"
    elif re.search(r"\b(hotel|hotels)\b", t):
        context["lodging_type"] = "hotel"

    m_budget = re.search(r"(€\s*)?(\d{2,4})\s*(eur|euro|euros)?\b", t)
    if m_budget:
        context["budget_per_night_eur"] = int(m_budget.group(2))

    active_city = context.get("city")
    active_month = context.get("month")

    # ------------------------------------------------------------------
    # 2. RAG retrieval — ALWAYS (if index exists)
    # ------------------------------------------------------------------
    rag_block = ""
    if _RAG_AVAILABLE:
        try:
            rag_results = retrieve_context(
                query=user_message,
                city=active_city,  # filter by city if known, else search all
                top_k=5,
            )
            rag_block = format_rag_context(rag_results)
        except Exception as exc:
            print(f"⚠️  RAG retrieval failed: {exc}")

    # ------------------------------------------------------------------
    # 3. Structured data — only when city + month are both known
    # ------------------------------------------------------------------
    structured_block = ""
    used_month = active_month
    fallback_note = ""

    if active_city and active_month:
        try:
            db = get_db()
            prefs = extract_preferences(user_message)
            neighborhoods = recommend_neighborhoods(
                db, active_city, active_month, preferences=prefs
            )

            if not neighborhoods and fallback == "last_year":
                alt = month_minus_one_year(active_month)
                neighborhoods = recommend_neighborhoods(
                    db, active_city, alt, preferences=prefs
                )
                if neighborhoods:
                    used_month = alt
                    fallback_note = (
                        f"Note: No data for {active_month}; "
                        f"showing {alt} (same month last year)."
                    )
                    context["month"] = used_month

            if neighborhoods:
                lines = []
                for n in neighborhoods:
                    sent = n.get("sentiment") or {}
                    lines.append(
                        f"- {n.get('neighborhood', '?')}: "
                        f"{n.get('occupancy_rate', 'N/A')}% occupancy, "
                        f"{sent.get('positive', 'N/A')}% positive "
                        f"({sent.get('total_reviews', 'N/A')} reviews)"
                    )
                structured_block = "\n".join(lines)
        except Exception as exc:
            print(f"⚠️  MongoDB query failed: {exc}")

    # ------------------------------------------------------------------
    # 4. Build the context block for the LLM
    # ------------------------------------------------------------------
    context_parts: list[str] = []

    # Current state
    state_lines = []
    if active_city:
        state_lines.append(f"City: {active_city.title()}")
    if used_month:
        state_lines.append(f"Month: {used_month}")
    if context.get("lodging_type"):
        state_lines.append(f"Lodging preference: {context['lodging_type']}")
    if context.get("budget_per_night_eur"):
        state_lines.append(f"Budget: ~€{context['budget_per_night_eur']}/night")

    if state_lines:
        context_parts.append(
            "CURRENT CONVERSATION STATE:\n" + "\n".join(state_lines)
        )
    else:
        context_parts.append(
            "CURRENT CONVERSATION STATE:\nNo city or month selected yet."
        )

    if fallback_note:
        context_parts.append(fallback_note)

    if structured_block:
        context_parts.append(
            "STRUCTURED DATA (neighborhood occupancy & sentiment):\n"
            + structured_block
        )

    if rag_block:
        context_parts.append(
            "CONTEXT CHUNKS (guest reviews & travel guides):\n" + rag_block
        )

    if not structured_block and not rag_block:
        context_parts.append(
            "No context data retrieved for this query. "
            "Answer based on your knowledge of the supported cities, "
            "but be transparent about what you're uncertain of."
        )

    injected_context = "\n\n".join(context_parts)

    # ------------------------------------------------------------------
    # 5. Build messages array with conversation history
    # ------------------------------------------------------------------
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add conversation history (last MAX_HISTORY_TURNS turns)
    recent = history[-MAX_HISTORY_TURNS:] if history else []
    for turn in recent:
        role = turn.get("role", "user")
        content = (turn.get("content") or "").strip()
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    # Current user message with injected context
    user_prompt = (
        f"{user_message}\n\n"
        f"---\n"
        f"{injected_context}"
    )
    messages.append({"role": "user", "content": user_prompt})

    # ------------------------------------------------------------------
    # 6. Call the LLM
    # ------------------------------------------------------------------
    api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.4,
    )

    llm_reply = response.choices[0].message.content.strip()

    # Anti-repeat check
    prev = context.get("_last_reply", "")
    if prev and _jaccard(prev, llm_reply) >= 0.85:
        llm_reply += "\n\n(Let me know if you'd like me to dig deeper or try a different angle!)"

    context["_last_reply"] = llm_reply

    # ------------------------------------------------------------------
    # 7. Build response payload
    # ------------------------------------------------------------------
    payload: dict = {"reply": llm_reply, "context": context}
    if active_city:
        payload["city"] = active_city
    if context.get("month"):
        payload["month"] = context["month"]

    return payload
