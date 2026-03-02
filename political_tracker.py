"""
political_tracker.py
Crypto Intelligence Pro — Political & Macro News Shock Detector
Supports offline/demo mode when internet is unavailable.
"""

import feedparser
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime

_analyzer = SentimentIntensityAnalyzer()

# News sources that cover political / macro events
POLITICAL_FEEDS = {
    "Reuters": "https://feeds.reuters.com/reuters/businessNews",
    "BBC Business": "https://feeds.bbci.co.uk/news/business/rss.xml",
    "CNBC": "https://www.cnbc.com/id/10000664/device/rss/rss.html",
    "CoinDesk Policy": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "CoinTelegraph": "https://cointelegraph.com/rss",
}

POLITICAL_KEYWORDS = [
    "trump", "biden", "federal reserve", "fed rate", "interest rate",
    "sec", "cftc", "regulation", "ban", "crackdown", "etf approval",
    "etf reject", "sanctions", "war", "inflation", "recession",
    "quantitative", "stimulus", "central bank", "treasury",
    "congress", "senate", "legislation", "crypto law", "cbdc",
    "irs", "tax", "mining ban", "china", "russia", "geopolit",
    "nuclear", "conflict", "nato",
]

BEARISH_SIGNALS = [
    "ban", "crackdown", "sanction", "reject", "tax", "restrict",
    "war", "nuclear", "recession", "crash", "crisis", "fear",
    "probe", "fraud", "hack", "arrest", "seized",
]

BULLISH_SIGNALS = [
    "approve", "etf", "adoption", "invest", "partnership", "launch",
    "legal", "regulated", "support", "stimulus", "relief",
    "bitcoin reserve", "strategic reserve", "treasury",
]

# ── Offline demo data ─────────────────────────────────────────────────────────
DEMO_POLITICAL = [
    {"title": "Trump Signs Executive Order Supporting US Bitcoin Strategic Reserve",
     "source": "Reuters [DEMO]", "published": "2025-03-01 11:00",
     "impact": "BULLISH", "link": "https://reuters.com"},
    {"title": "Federal Reserve Holds Rates Steady — Markets React Positively",
     "source": "CNBC [DEMO]", "published": "2025-03-01 10:30",
     "impact": "BULLISH", "link": "https://cnbc.com"},
    {"title": "SEC Opens New Investigation Into Crypto Exchange Practices",
     "source": "BBC Business [DEMO]", "published": "2025-03-01 09:15",
     "impact": "BEARISH", "link": "https://bbc.co.uk/news/business"},
    {"title": "China Reaffirms Crypto Mining Ban, Intensifies Enforcement",
     "source": "Reuters [DEMO]", "published": "2025-03-01 08:00",
     "impact": "BEARISH", "link": "https://reuters.com"},
    {"title": "US Congress Debates Bipartisan Crypto Regulation Framework",
     "source": "CNBC [DEMO]", "published": "2025-02-28 18:30",
     "impact": "NEUTRAL", "link": "https://cnbc.com"},
    {"title": "EU Approves MiCA Framework — Regulatory Clarity for Crypto",
     "source": "CoinDesk Policy [DEMO]", "published": "2025-02-28 16:00",
     "impact": "BULLISH", "link": "https://coindesk.com"},
    {"title": "IMF Warns of Systemic Risk from Unregulated Crypto Assets",
     "source": "Reuters [DEMO]", "published": "2025-02-28 14:00",
     "impact": "BEARISH", "link": "https://reuters.com"},
    {"title": "G20 Leaders Agree on Global Crypto Taxation Framework",
     "source": "BBC Business [DEMO]", "published": "2025-02-28 12:00",
     "impact": "NEUTRAL", "link": "https://bbc.co.uk/news/business"},
]


def assess_market_impact(headline: str) -> str:
    """
    Determine BULLISH / BEARISH / NEUTRAL impact on crypto markets
    based on keyword matching + VADER sentiment.
    """
    text = headline.lower()
    bearish_hits = sum(1 for kw in BEARISH_SIGNALS if kw in text)
    bullish_hits = sum(1 for kw in BULLISH_SIGNALS if kw in text)
    try:
        polarity = _analyzer.polarity_scores(headline)["compound"]
    except Exception:
        polarity = 0.0

    if bullish_hits > bearish_hits or (bullish_hits == bearish_hits and polarity > 0.1):
        return "BULLISH"
    elif bearish_hits > bullish_hits or polarity < -0.1:
        return "BEARISH"
    else:
        return "NEUTRAL"


def is_political(title: str, summary: str = "") -> bool:
    """Check if a headline contains political / macro keywords."""
    text = (title + " " + summary).lower()
    return any(kw in text for kw in POLITICAL_KEYWORDS)


def _is_online() -> bool:
    """Quick check: can we reach the internet?"""
    try:
        import urllib.request
        urllib.request.urlopen("https://www.google.com", timeout=3)
        return True
    except Exception:
        return False


def fetch_political_news(max_per_feed: int = 10) -> pd.DataFrame:
    """
    Fetch political / macro news from RSS feeds.
    Falls back to built-in demo data if offline.
    Returns DataFrame: title, source, published, impact, link
    """
    # ── Try online first ──────────────────────────────────────────────────────
    if _is_online():
        articles = []
        for source, url in POLITICAL_FEEDS.items():
            try:
                feed = feedparser.parse(url)
                count = 0
                for entry in feed.entries:
                    if count >= max_per_feed:
                        break
                    title = entry.get("title", "").strip()
                    summary = entry.get("summary", "")
                    link = entry.get("link", "")
                    published_parsed = entry.get("published_parsed")
                    if published_parsed:
                        published = datetime(*published_parsed[:6]).strftime("%Y-%m-%d %H:%M")
                    else:
                        published = datetime.now().strftime("%Y-%m-%d %H:%M")
                    if not title or not is_political(title, summary):
                        continue
                    impact = assess_market_impact(title)
                    articles.append({
                        "title": title, "source": source,
                        "published": published, "impact": impact, "link": link,
                    })
                    count += 1
            except Exception as e:
                print(f"[political_tracker] Failed to fetch {source}: {e}")

        if articles:
            df = pd.DataFrame(articles)
            df = df.sort_values("published", ascending=False).reset_index(drop=True)
            return df

    # ── Offline fallback ──────────────────────────────────────────────────────
    print("[political_tracker] Offline mode — using demo data.")
    return pd.DataFrame(DEMO_POLITICAL)


def get_political_summary(df: pd.DataFrame) -> dict:
    """Return counts and overall political climate for crypto."""
    if df.empty:
        return {"bullish": 0, "bearish": 0, "neutral": 0, "climate": "STABLE", "alert": False}

    counts = df["impact"].value_counts().to_dict()
    bullish = counts.get("BULLISH", 0)
    bearish = counts.get("BEARISH", 0)
    neutral = counts.get("NEUTRAL", 0)

    total = bullish + bearish + neutral
    bearish_ratio = bearish / total if total > 0 else 0

    if bearish_ratio >= 0.6:
        climate = "HOSTILE"
        alert = True
    elif bearish_ratio >= 0.4:
        climate = "CAUTIOUS"
        alert = False
    elif bullish > bearish:
        climate = "FAVORABLE"
        alert = False
    else:
        climate = "STABLE"
        alert = False

    return {
        "bullish": bullish, "bearish": bearish, "neutral": neutral,
        "climate": climate, "alert": alert,
    }
