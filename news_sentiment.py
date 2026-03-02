"""
news_sentiment.py
Crypto Intelligence Pro — News Feed Parser & Sentiment Analyzer
Supports offline/demo mode when internet is unavailable.
"""

import feedparser
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
import time

_analyzer = SentimentIntensityAnalyzer()

# RSS feeds for crypto news
RSS_FEEDS = {
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "CoinTelegraph": "https://cointelegraph.com/rss",
    "CryptoSlate": "https://cryptoslate.com/feed/",
    "Decrypt": "https://decrypt.co/feed",
    "Bitcoin Magazine": "https://bitcoinmagazine.com/feed",
}

# Keywords to filter relevant crypto news
CRYPTO_KEYWORDS = [
    "bitcoin", "btc", "ethereum", "eth", "solana", "sol", "crypto",
    "blockchain", "defi", "nft", "altcoin", "stablecoin", "coinbase",
    "binance", "regulation", "etf", "sec", "fed", "inflation",
    "interest rate", "liquidation", "whale", "halving", "mining",
    "wallet", "exchange", "bnb", "xrp", "ripple",
]

# ── Offline demo data ─────────────────────────────────────────────────────────
DEMO_NEWS = [
    {"title": "Bitcoin Surges Past $90,000 as Institutional Demand Grows",
     "source": "CoinDesk [DEMO]", "published": "2025-03-01 10:00",
     "sentiment": "POSITIVE", "score": 0.65,
     "link": "https://coindesk.com"},
    {"title": "Ethereum ETF Approval Could Unlock $15B in Institutional Capital",
     "source": "CoinTelegraph [DEMO]", "published": "2025-03-01 09:30",
     "sentiment": "POSITIVE", "score": 0.58,
     "link": "https://cointelegraph.com"},
    {"title": "SEC Delays Decision on Spot Bitcoin ETF Applications",
     "source": "Decrypt [DEMO]", "published": "2025-03-01 08:45",
     "sentiment": "NEGATIVE", "score": -0.30,
     "link": "https://decrypt.co"},
    {"title": "Crypto Market Sees $2B in Liquidations Amid Volatility",
     "source": "CryptoSlate [DEMO]", "published": "2025-03-01 08:00",
     "sentiment": "NEGATIVE", "score": -0.42,
     "link": "https://cryptoslate.com"},
    {"title": "Solana Network Handles Record 50,000 TPS in Stress Test",
     "source": "Bitcoin Magazine [DEMO]", "published": "2025-03-01 07:30",
     "sentiment": "POSITIVE", "score": 0.72,
     "link": "https://bitcoinmagazine.com"},
    {"title": "BNB Chain Partners with Major Asian Bank for Blockchain Integration",
     "source": "CoinDesk [DEMO]", "published": "2025-02-28 20:00",
     "sentiment": "POSITIVE", "score": 0.55,
     "link": "https://coindesk.com"},
    {"title": "Crypto Regulation Talks Continue in US Congress — No Decision Yet",
     "source": "CoinTelegraph [DEMO]", "published": "2025-02-28 18:00",
     "sentiment": "NEUTRAL", "score": 0.02,
     "link": "https://cointelegraph.com"},
    {"title": "XRP Legal Victory: Court Rules Token Not a Security in Retail Sales",
     "source": "Decrypt [DEMO]", "published": "2025-02-28 16:00",
     "sentiment": "POSITIVE", "score": 0.80,
     "link": "https://decrypt.co"},
    {"title": "DeFi Protocol Loses $45M in Flash Loan Exploit",
     "source": "CryptoSlate [DEMO]", "published": "2025-02-28 14:00",
     "sentiment": "NEGATIVE", "score": -0.60,
     "link": "https://cryptoslate.com"},
    {"title": "Bitcoin Mining Difficulty Reaches All-Time High",
     "source": "Bitcoin Magazine [DEMO]", "published": "2025-02-28 12:00",
     "sentiment": "NEUTRAL", "score": 0.05,
     "link": "https://bitcoinmagazine.com"},
]


def score_sentiment(text: str) -> float:
    """Return VADER compound score from -1.0 (negative) to +1.0 (positive)."""
    try:
        scores = _analyzer.polarity_scores(str(text))
        return round(scores["compound"], 4)
    except Exception:
        return 0.0


def classify_sentiment(score: float) -> str:
    """Map compound score to a human-readable label."""
    if score >= 0.10:
        return "POSITIVE"
    elif score <= -0.10:
        return "NEGATIVE"
    else:
        return "NEUTRAL"


def is_relevant(title: str, summary: str = "") -> bool:
    """Check if headline matches any crypto keyword."""
    text = (title + " " + summary).lower()
    return any(kw in text for kw in CRYPTO_KEYWORDS)


def _is_online() -> bool:
    """Quick check: can we reach the internet?"""
    try:
        import urllib.request
        urllib.request.urlopen("https://www.google.com", timeout=3)
        return True
    except Exception:
        return False


def fetch_crypto_news(max_per_feed: int = 10) -> pd.DataFrame:
    """
    Fetch headlines from RSS feeds.
    Falls back to built-in demo data if offline.
    Returns DataFrame: title, source, published, sentiment, score, link
    """
    # ── Try online first ──────────────────────────────────────────────────────
    if _is_online():
        articles = []
        for source, url in RSS_FEEDS.items():
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
                    if not title or not is_relevant(title, summary):
                        continue
                    score = score_sentiment(title)
                    label = classify_sentiment(score)
                    articles.append({
                        "title": title, "source": source,
                        "published": published, "sentiment": label,
                        "score": score, "link": link,
                    })
                    count += 1
            except Exception as e:
                print(f"[news_sentiment] Failed to fetch {source}: {e}")

        if articles:
            df = pd.DataFrame(articles)
            df = df.sort_values("published", ascending=False).reset_index(drop=True)
            return df

    # ── Offline fallback ──────────────────────────────────────────────────────
    print("[news_sentiment] Offline mode — using demo data.")
    return pd.DataFrame(DEMO_NEWS)


def get_sentiment_summary(df: pd.DataFrame) -> dict:
    """Aggregate sentiment counts and overall market mood."""
    if df.empty:
        return {"positive": 0, "negative": 0, "neutral": 0, "mood": "NEUTRAL", "avg_score": 0.0}

    counts = df["sentiment"].value_counts().to_dict()
    positive = counts.get("POSITIVE", 0)
    negative = counts.get("NEGATIVE", 0)
    neutral = counts.get("NEUTRAL", 0)
    avg_score = round(float(df["score"].mean()), 4)

    if avg_score >= 0.10:
        mood = "BULLISH"
    elif avg_score <= -0.10:
        mood = "BEARISH"
    else:
        mood = "NEUTRAL"

    return {
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "mood": mood,
        "avg_score": avg_score,
    }
