import os
import re
from typing import Any, List, Optional

from dotenv import load_dotenv
from pymongo.database import Database

import mongo_collections as C

load_dotenv()

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    from tavily import TavilyClient

    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False

tavily_client = None
if TAVILY_AVAILABLE:
    tavily_key = os.getenv("TAVILY_API_KEY", "").strip()
    if tavily_key:
        tavily_client = TavilyClient(api_key=tavily_key)

CUISINE_KEYWORDS = {
    "italian": "Italian",
    "pizza": "Italian",
    "pasta": "Italian",
    "chinese": "Chinese",
    "dim sum": "Chinese",
    "dumpling": "Chinese",
    "mexican": "Mexican",
    "taco": "Mexican",
    "burrito": "Mexican",
    "enchilada": "Mexican",
    "indian": "Indian",
    "curry": "Indian",
    "tandoor": "Indian",
    "biryani": "Indian",
    "chaat": "Indian",
    "samosa": "Indian",
    "dosa": "Indian",
    "naan": "Indian",
    "tikka": "Indian",
    "japanese": "Japanese",
    "sushi": "Japanese",
    "ramen": "Japanese",
    "tempura": "Japanese",
    "american": "American",
    "burger": "American",
    "bbq": "American",
    "steak": "American",
    "french": "French",
    "bistro": "French",
    "mediterranean": "Mediterranean",
    "greek": "Greek",
    "hummus": "Mediterranean",
    "falafel": "Mediterranean",
    "thai": "Thai",
    "pad thai": "Thai",
    "tom yum": "Thai",
    "korean": "Korean",
    "kbbq": "Korean",
    "bulgogi": "Korean",
    "vietnamese": "Vietnamese",
    "pho": "Vietnamese",
    "banh mi": "Vietnamese",
    "ethiopian": "Ethiopian",
    "afghan": "Afghan",
    "portuguese": "Portuguese",
    "burmese": "Burmese",
    "spanish": "Spanish",
    "tapas": "Spanish",
}
ASIAN_CUISINES = ["Chinese", "Japanese", "Korean", "Thai", "Vietnamese", "Indian", "Burmese"]
LOCAL_AREAS = {"san jose", "santa clara", "san francisco", "bay area"}


def strip_markdown(text):
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"\*(.+?)\*", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"_(.+?)_", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"^#{1,3}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[•\-\*]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def get_user_preferences(user_id, db: Database):
    if not user_id:
        return None
    try:
        return db[C.USER_PREFERENCES].find_one({"user_id": user_id})
    except Exception:
        return None


def detect_cuisine(text):
    text = text.lower()
    if "asian" in text:
        return None, True
    for kw, cuisine in CUISINE_KEYWORDS.items():
        if kw in text:
            return cuisine, False
    return None, False


def should_search_web(message: str) -> bool:
    triggers = [
        "open now",
        "open late",
        "open tonight",
        "hours",
        "what time",
        "trending",
        "popular right now",
        "special event",
        "this weekend",
        "today",
        "currently",
        "best right now",
        "new restaurant",
        "just opened",
        "closing time",
        "reservation",
        "travel",
        "travelling",
        "traveling",
        "trip",
        "vacation",
        "visiting",
        "in india",
        "in japan",
        "in france",
        "in italy",
        "in mexico",
        "in thailand",
        "in korea",
        "in vietnam",
        "in spain",
    ]
    msg = message.lower()
    return any(t in msg for t in triggers)


def extract_destination(message: str) -> str:
    msg = message.lower().strip()
    patterns = [
        r"\b(?:travel|travelling|traveling|visiting|trip to|vacation in)\s+(?:to\s+|in\s+)?([a-zA-Z\s]{2,40})",
        r"\b(?:restaurants|food|places)\s+in\s+([a-zA-Z\s]{2,40})",
        r"\bto\s+([a-zA-Z\s]{2,40})",
    ]
    for p in patterns:
        m = re.search(p, msg)
        if m:
            raw = m.group(1)
            raw = re.split(r"[,.!?;]", raw)[0].strip()
            cleaned = " ".join(raw.split()[:4])
            return cleaned.title()
    return ""


def search_web_results(query: str, max_results: int = 4):
    if not tavily_client:
        return []
    try:
        results = tavily_client.search(
            query=query, max_results=max_results, search_depth="basic"
        )
        if results and results.get("results"):
            return results["results"][:max_results]
        return []
    except Exception:
        return []


def search_web(query: str) -> str:
    web_results = search_web_results(query, max_results=2)
    if not web_results:
        return ""
    first = web_results[0]
    return first.get("content", "")[:300]


def build_travel_web_response(destination: str, web_results) -> str:
    lines = [
        f"Great choice. Here are some well-reviewed restaurant picks in {destination} from live web results:"
    ]
    for i, item in enumerate(web_results[:4], 1):
        title = (item.get("title") or "Restaurant pick").strip()
        content = (item.get("content") or "").strip().replace("\n", " ")
        snippet = content[:140] + ("..." if len(content) > 140 else "")
        lines.append(f"\n{i}. {title}")
        if snippet:
            lines.append(f"   {snippet}")
    lines.append("\nIf you want, I can narrow this by budget, veg options, or neighborhood.")
    return "".join(lines)


def _mongo_restaurant_sort_cursor(db: Database, q: dict, limit: int):
    return (
        db[C.RESTAURANTS]
        .find(q)
        .sort([("avg_rating", -1)])
        .limit(limit)
    )


def query_restaurants(
    cuisine, is_asian_broad, city, db: Database, limit=6
) -> List[dict]:
    q: dict[str, Any] = {}
    if cuisine:
        q["cuisine"] = cuisine
    elif is_asian_broad:
        q["cuisine"] = {"$in": ASIAN_CUISINES}
    if city:
        q["city"] = {"$regex": city, "$options": "i"}

    results = list(_mongo_restaurant_sort_cursor(db, q, limit))
    if not results and city and (cuisine or is_asian_broad):
        q2: dict[str, Any] = {}
        if cuisine:
            q2["cuisine"] = cuisine
        elif is_asian_broad:
            q2["cuisine"] = {"$in": ASIAN_CUISINES}
        results = list(_mongo_restaurant_sort_cursor(db, q2, limit))
    if not results and not cuisine and not is_asian_broad:
        results = list(
            db[C.RESTAURANTS].find({}).sort("avg_rating", -1).limit(limit)
        )
    return results


def format_for_ai(restaurants: List[dict]):
    lines = ["Available restaurants:\n"]
    for r in restaurants:
        rid = r.get("_id")
        line = f"- ID:{rid} | {r.get('name')} | {r.get('cuisine')} | {r.get('city')}"
        if r.get("price_tier"):
            line += f" | {r['price_tier']}"
        ar = r.get("avg_rating")
        if ar:
            line += f" | Rating:{ar}"
        desc = r.get("description") or ""
        if desc:
            line += f" | {desc[:80]}"
        lines.append(line)
    return "\n".join(lines)


def format_for_response(restaurants: List[dict]):
    out = []
    for r in restaurants:
        ar = r.get("avg_rating")
        out.append(
            {
                "id": r["_id"],
                "name": r.get("name"),
                "cuisine": r.get("cuisine"),
                "rating": float(ar) if ar is not None else 0,
                "avg_rating": float(ar) if ar is not None else 0,
                "price": r.get("price_tier"),
                "pricing_tier": r.get("price_tier"),
                "city": r.get("city"),
                "address": r.get("address"),
                "description": r.get("description"),
                "hours": r.get("hours"),
            }
        )
    return out


def build_response(message, cuisine, is_asian_broad, restaurants: List[dict]):
    if not restaurants:
        label = cuisine or ("Asian" if is_asian_broad else "")
        return (
            f"I couldn't find any {label} restaurants right now. Try the explore page!"
            if label
            else "I couldn't find matching restaurants. Try the explore page!"
        )
    msg = message.lower()
    if cuisine:
        opener = f"Here are some great {cuisine} restaurants:"
    elif is_asian_broad:
        opener = "Here are some great Asian restaurant options:"
    elif any(w in msg for w in ["romantic", "date", "anniversary"]):
        opener = "For a romantic evening, here are some great options:"
    elif any(w in msg for w in ["cheap", "budget", "affordable"]):
        opener = "Here are some budget-friendly options:"
    elif any(w in msg for w in ["best", "top", "highest"]):
        opener = "Here are the highest-rated restaurants:"
    elif any(w in msg for w in ["vegan", "vegetarian"]):
        opener = "Here are some great plant-based dining options:"
    else:
        opener = "Here are some restaurants you might enjoy:"
    lines = [opener]
    for i, r in enumerate(restaurants[:4], 1):
        line = f"\n{i}. {r.get('name')}"
        if r.get("cuisine"):
            line += f" ({r['cuisine']}"
            if r.get("price_tier"):
                line += f", {r['price_tier']}"
            line += ")"
        ar = r.get("avg_rating")
        if ar and ar > 0:
            line += f" — rated {ar}/5"
        if r.get("city"):
            line += f" in {r['city']}"
        lines.append(line)
    lines.append("\n\nWould you like more details or should I refine the search?")
    return "".join(lines)


async def chat(user_id, message, history, db: Database):
    prefs = get_user_preferences(user_id, db) if user_id else None
    cuisine, is_asian_broad = detect_cuisine(message)
    city = None
    for c in ["san jose", "santa clara", "san francisco"]:
        if c in message.lower():
            city = "San Francisco" if c == "san francisco" else c.title()
            break

    destination = extract_destination(message)
    if destination and destination.lower() not in LOCAL_AREAS and tavily_client:
        travel_query = f"best restaurants in {destination} with ratings and popular local recommendations"
        live_results = search_web_results(travel_query, max_results=4)
        if live_results:
            return {
                "response": build_travel_web_response(destination, live_results),
                "recommended_restaurants": [],
            }

    web_context = ""
    if should_search_web(message):
        search_query = f"restaurants {message} San Jose CA"
        web_context = search_web(search_query)

    restaurants = query_restaurants(cuisine, is_asian_broad, city, db, limit=6)
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    gemini_ready = LANGCHAIN_AVAILABLE and bool(gemini_key)

    if gemini_ready:
        try:
            cuisine_rule = ""
            if cuisine:
                cuisine_rule = f"\nSTRICT: User wants {cuisine} food. ONLY recommend restaurants where cuisine='{cuisine}'. No exceptions."
            elif is_asian_broad:
                cuisine_rule = "\nSTRICT: User wants Asian food. Only recommend Chinese/Japanese/Korean/Thai/Vietnamese/Indian restaurants."

            prefs_text = ""
            if prefs:
                parts = []
                if prefs.get("cuisines"):
                    parts.append(f"Cuisines: {prefs['cuisines']}")
                if prefs.get("price_range"):
                    parts.append(f"Price: {prefs['price_range']}")
                if prefs.get("dietary_needs"):
                    parts.append(f"Dietary: {prefs['dietary_needs']}")
                if parts:
                    prefs_text = "\nUser preferences:\n" + "\n".join(parts)

            web_section = ""
            if web_context:
                web_section = f"\n\nCurrent web information:\n{web_context}"

            system = f"""You are a friendly restaurant assistant. Be warm and conversational.
Plain text only — no markdown, no asterisks, no bullet points, no bold.{cuisine_rule}{prefs_text}{web_section}
{format_for_ai(restaurants)}
Only recommend restaurants from the list above. Use web info only for hours/events context."""

            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=gemini_key,
            )
            msgs = [SystemMessage(content=system)]
            for m in history[-6:]:
                if m["role"] == "user":
                    msgs.append(HumanMessage(content=m["content"]))
                elif m["role"] == "assistant":
                    msgs.append(AIMessage(content=m["content"]))
            msgs.append(HumanMessage(content=message))
            response = llm.invoke(msgs)
            text = strip_markdown(response.content)
            tl = text.lower()
            mentioned = [
                r
                for r in restaurants
                if (r.get("name") or "").lower() and (r.get("name") or "").lower() in tl
            ]
            if not mentioned:
                mentioned = restaurants[:3]
            return {
                "response": text,
                "recommended_restaurants": format_for_response(mentioned[:4]),
            }

        except Exception as e:
            print(f"GEMINI ERROR: {str(e)}")
            err = str(e).lower()
            if not ("auth" in err or "api" in err or "invalid" in err):
                raise

    base_response = build_response(message, cuisine, is_asian_broad, restaurants)
    return {
        "response": base_response,
        "recommended_restaurants": format_for_response(restaurants[:4]),
    }
