from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.restaurant import Restaurant
from models.user_preference import UserPreference
import os, re
from dotenv import load_dotenv
load_dotenv()

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False

# ← ADDED: Initialize Tavily client
tavily_client = None
if TAVILY_AVAILABLE:
    tavily_key = os.getenv("TAVILY_API_KEY", "").strip()
    if tavily_key:
        tavily_client = TavilyClient(api_key=tavily_key)

CUISINE_KEYWORDS = {
    "italian":"Italian","pizza":"Italian","pasta":"Italian",
    "chinese":"Chinese","dim sum":"Chinese","dumpling":"Chinese",
    "mexican":"Mexican","taco":"Mexican","burrito":"Mexican","enchilada":"Mexican",
    "indian":"Indian","curry":"Indian","tandoor":"Indian","biryani":"Indian",
    "chaat":"Indian","samosa":"Indian","dosa":"Indian","naan":"Indian","tikka":"Indian",
    "japanese":"Japanese","sushi":"Japanese","ramen":"Japanese","tempura":"Japanese",
    "american":"American","burger":"American","bbq":"American","steak":"American",
    "french":"French","bistro":"French",
    "mediterranean":"Mediterranean","greek":"Greek","hummus":"Mediterranean","falafel":"Mediterranean",
    "thai":"Thai","pad thai":"Thai","tom yum":"Thai",
    "korean":"Korean","kbbq":"Korean","bulgogi":"Korean",
    "vietnamese":"Vietnamese","pho":"Vietnamese","banh mi":"Vietnamese",
    "ethiopian":"Ethiopian","afghan":"Afghan","portuguese":"Portuguese","burmese":"Burmese",
    "spanish":"Spanish","tapas":"Spanish",
}
ASIAN_CUISINES = ["Chinese","Japanese","Korean","Thai","Vietnamese","Indian","Burmese"]

def strip_markdown(text):
    text = re.sub(r'\*\*(.+?)\*\*',r'\1',text,flags=re.DOTALL)
    text = re.sub(r'\*(.+?)\*',r'\1',text,flags=re.DOTALL)
    text = re.sub(r'_(.+?)_',r'\1',text,flags=re.DOTALL)
    text = re.sub(r'`(.+?)`',r'\1',text)
    text = re.sub(r'^#{1,3}\s+','',text,flags=re.MULTILINE)
    text = re.sub(r'^[•\-\*]\s+','',text,flags=re.MULTILINE)
    text = re.sub(r'^\d+\.\s+','',text,flags=re.MULTILINE)
    text = re.sub(r'\n{3,}','\n\n',text)
    return text.strip()

def get_user_preferences(user_id,db):
    if not user_id: return None
    try: return db.query(UserPreference).filter(UserPreference.user_id==user_id).first()
    except: return None

def detect_cuisine(text):
    text = text.lower()
    if "asian" in text: return None, True
    for kw,cuisine in CUISINE_KEYWORDS.items():
        if kw in text: return cuisine, False
    return None, False

# ← ADDED: Detect if user is asking about real-time info
def should_search_web(message: str) -> bool:
    triggers = [
        "open now", "open late", "open tonight", "hours", "what time",
        "trending", "popular right now", "special event", "this weekend",
        "today", "currently", "best right now", "new restaurant",
        "just opened", "closing time", "reservation"
    ]
    msg = message.lower()
    return any(t in msg for t in triggers)

# ← ADDED: Search web using Tavily
def search_web(query: str) -> str:
    if not tavily_client:
        return ""
    try:
        results = tavily_client.search(
            query=query,
            max_results=2,
            search_depth="basic"
        )
        if results and results.get("results"):
            # Take only the first result, clean it up
            first = results["results"][0]
            content = first.get("content", "")[:300]
            return content
        return ""
    except Exception:
        return ""

def query_restaurants(cuisine, is_asian_broad, city, db, limit=6):
    q = db.query(Restaurant)
    if cuisine:
        q = q.filter(Restaurant.cuisine == cuisine)
    elif is_asian_broad:
        q = q.filter(Restaurant.cuisine.in_(ASIAN_CUISINES))
    if city:
        q = q.filter(Restaurant.city.ilike(f"%{city}%"))
    results = q.order_by(Restaurant.avg_rating.desc()).limit(limit).all()
    if not results and city and (cuisine or is_asian_broad):
        q2 = db.query(Restaurant)
        if cuisine: q2 = q2.filter(Restaurant.cuisine==cuisine)
        elif is_asian_broad: q2 = q2.filter(Restaurant.cuisine.in_(ASIAN_CUISINES))
        results = q2.order_by(Restaurant.avg_rating.desc()).limit(limit).all()
    if not results and not cuisine and not is_asian_broad:
        results = db.query(Restaurant).order_by(Restaurant.avg_rating.desc()).limit(limit).all()
    return results

def format_for_ai(restaurants):
    lines = ["Available restaurants:\n"]
    for r in restaurants:
        line = f"- ID:{r.id} | {r.name} | {r.cuisine} | {r.city}"
        if r.price_tier: line += f" | {r.price_tier}"
        if r.avg_rating: line += f" | Rating:{r.avg_rating}"
        if r.description: line += f" | {r.description[:80]}"
        lines.append(line)
    return "\n".join(lines)

def format_for_response(restaurants):
    return [{"id":r.id,"name":r.name,"cuisine":r.cuisine,
             "rating":float(r.avg_rating) if r.avg_rating else 0,
             "avg_rating":float(r.avg_rating) if r.avg_rating else 0,
             "price":r.price_tier,"pricing_tier":r.price_tier,
             "city":r.city,"address":r.address,
             "description":r.description,"hours":r.hours} for r in restaurants]

def build_response(message, cuisine, is_asian_broad, restaurants):
    if not restaurants:
        label = cuisine or ("Asian" if is_asian_broad else "")
        return f"I couldn't find any {label} restaurants right now. Try the explore page!" if label else "I couldn't find matching restaurants. Try the explore page!"
    msg = message.lower()
    if cuisine: opener = f"Here are some great {cuisine} restaurants:"
    elif is_asian_broad: opener = "Here are some great Asian restaurant options:"
    elif any(w in msg for w in ["romantic","date","anniversary"]): opener = "For a romantic evening, here are some great options:"
    elif any(w in msg for w in ["cheap","budget","affordable"]): opener = "Here are some budget-friendly options:"
    elif any(w in msg for w in ["best","top","highest"]): opener = "Here are the highest-rated restaurants:"
    elif any(w in msg for w in ["vegan","vegetarian"]): opener = "Here are some great plant-based dining options:"
    else: opener = "Here are some restaurants you might enjoy:"
    lines = [opener]
    for i,r in enumerate(restaurants[:4],1):
        line = f"\n{i}. {r.name}"
        if r.cuisine:
            line += f" ({r.cuisine}"
            if r.price_tier: line += f", {r.price_tier}"
            line += ")"
        if r.avg_rating and r.avg_rating > 0: line += f" — rated {r.avg_rating}/5"
        if r.city: line += f" in {r.city}"
        lines.append(line)
    lines.append("\n\nWould you like more details or should I refine the search?")
    return "".join(lines)

async def chat(user_id, message, history, db):
    prefs = get_user_preferences(user_id, db) if user_id else None
    cuisine, is_asian_broad = detect_cuisine(message)
    city = None
    for c in ["san jose","santa clara","san francisco"]:
        if c in message.lower():
            city = "San Francisco" if c=="san francisco" else c.title()
            break

    # ← ADDED: Run Tavily web search if query needs real-time info
    web_context = ""
    if should_search_web(message):
        search_query = f"restaurants {message} San Jose CA"
        web_context = search_web(search_query)

    restaurants = query_restaurants(cuisine, is_asian_broad, city, db, limit=6)
    gemini_key = os.getenv("GEMINI_API_KEY","").strip()
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
                if prefs.cuisines: parts.append(f"Cuisines: {prefs.cuisines}")
                if prefs.price_range: parts.append(f"Price: {prefs.price_range}")
                if prefs.dietary_needs: parts.append(f"Dietary: {prefs.dietary_needs}")
                if parts: prefs_text = "\nUser preferences:\n" + "\n".join(parts)

            web_section = ""
            if web_context:
                web_section = f"\n\nCurrent web information:\n{web_context}"

            system = f"""You are a friendly restaurant assistant. Be warm and conversational.
Plain text only — no markdown, no asterisks, no bullet points, no bold.{cuisine_rule}{prefs_text}{web_section}
{format_for_ai(restaurants)}
Only recommend restaurants from the list above. Use web info only for hours/events context."""

            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=gemini_key
            )
            msgs = [SystemMessage(content=system)]
            for m in history[-6:]:
                if m["role"] == "user": msgs.append(HumanMessage(content=m["content"]))
                elif m["role"] == "assistant": msgs.append(AIMessage(content=m["content"]))
            msgs.append(HumanMessage(content=message))
            response = llm.invoke(msgs)
            text = strip_markdown(response.content)
            mentioned = [r for r in restaurants if r.name.lower() in text.lower()]
            if not mentioned: mentioned = restaurants[:3]
            return {"response": text,
                    "recommended_restaurants": format_for_response(mentioned[:4])}

        except Exception as e:
            print(f"GEMINI ERROR: {str(e)}")
            err = str(e).lower()
            if not("auth" in err or "api" in err or "invalid" in err): raise

    # Default database fallback
    base_response = build_response(message, cuisine, is_asian_broad, restaurants)
    return {"response": base_response,
            "recommended_restaurants": format_for_response(restaurants[:4])}