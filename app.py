"""
app.py
Crypto Intelligence Pro — Main Streamlit Dashboard
Google Antigravity | A next-generation crypto decision support system
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime

from trading_logic import (
    COINS, PERIODS, fetch_price_data,
    calculate_rsi, calculate_ma,
    generate_signal, get_volatility, get_stop_loss_guidance
)
from news_sentiment import fetch_crypto_news, get_sentiment_summary
from political_tracker import fetch_political_news, get_political_summary
from email_alerts import send_alert, build_signal_alert, build_political_alert, EMAIL_CONFIGURED

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Crypto Intelligence Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #0f1923 50%, #0d1117 100%);
        color: #e6edf3;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #0d1117 100%);
        border-right: 1px solid #1f2937;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #161b22 0%, #1c2333 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 18px 20px;
        text-align: center;
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        border-color: #58a6ff;
        box-shadow: 0 0 20px rgba(88, 166, 255, 0.15);
        transform: translateY(-2px);
    }

    .metric-label {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #8b949e;
        margin-bottom: 6px;
    }

    .metric-value {
        font-size: 26px;
        font-weight: 800;
        color: #e6edf3;
    }

    /* Signal badges */
    .signal-buy {
        background: linear-gradient(135deg, #1a4731, #0d6638);
        color: #3fb950;
        border: 1px solid #3fb950;
        border-radius: 10px;
        padding: 14px 28px;
        font-size: 22px;
        font-weight: 800;
        letter-spacing: 3px;
        text-align: center;
        box-shadow: 0 0 30px rgba(63, 185, 80, 0.3);
        animation: pulse-green 2s infinite;
    }

    .signal-sell {
        background: linear-gradient(135deg, #4a1616, #7a1e1e);
        color: #f85149;
        border: 1px solid #f85149;
        border-radius: 10px;
        padding: 14px 28px;
        font-size: 22px;
        font-weight: 800;
        letter-spacing: 3px;
        text-align: center;
        box-shadow: 0 0 30px rgba(248, 81, 73, 0.3);
        animation: pulse-red 2s infinite;
    }

    .signal-hold {
        background: linear-gradient(135deg, #3a2d0d, #5a4a1a);
        color: #f0c040;
        border: 1px solid #f0c040;
        border-radius: 10px;
        padding: 14px 28px;
        font-size: 22px;
        font-weight: 800;
        letter-spacing: 3px;
        text-align: center;
        box-shadow: 0 0 30px rgba(240, 192, 64, 0.2);
    }

    @keyframes pulse-green {
        0%, 100% { box-shadow: 0 0 20px rgba(63, 185, 80, 0.3); }
        50% { box-shadow: 0 0 40px rgba(63, 185, 80, 0.6); }
    }

    @keyframes pulse-red {
        0%, 100% { box-shadow: 0 0 20px rgba(248, 81, 73, 0.3); }
        50% { box-shadow: 0 0 40px rgba(248, 81, 73, 0.6); }
    }

    /* Section headers */
    .section-header {
        font-size: 15px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #58a6ff;
        border-bottom: 1px solid #21262d;
        padding-bottom: 8px;
        margin: 20px 0 14px 0;
    }

    /* News rows */
    .news-positive { border-left: 3px solid #3fb950; padding-left: 10px; margin: 6px 0; }
    .news-negative { border-left: 3px solid #f85149; padding-left: 10px; margin: 6px 0; }
    .news-neutral  { border-left: 3px solid #8b949e; padding-left: 10px; margin: 6px 0; }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: #161b22;
        border-radius: 10px;
        padding: 4px;
        border: 1px solid #30363d;
        gap: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #8b949e;
        font-weight: 600;
        font-size: 13px;
        padding: 8px 18px;
    }

    .stTabs [aria-selected="true"] {
        background: #21262d;
        color: #e6edf3;
    }

    /* Dividers */
    hr { border-color: #21262d; margin: 16px 0; }

    /* Risk blocks */
    .risk-block {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px;
        margin: 8px 0;
    }

    /* Alert success / error */
    .alert-success {
        background: #1a4731;
        border: 1px solid #3fb950;
        border-radius: 8px;
        color: #3fb950;
        padding: 12px 16px;
        margin: 8px 0;
    }
    .alert-error {
        background: #4a1616;
        border: 1px solid #f85149;
        border-radius: 8px;
        color: #f85149;
        padding: 12px 16px;
        margin: 8px 0;
    }

    /* Hide Streamlit branding */
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 10px 0 20px 0;'>
        <div style='font-size: 36px; margin-bottom: 4px;'>🚀</div>
        <div style='font-size: 16px; font-weight: 800; color: #e6edf3; letter-spacing: 1px;'>
            Crypto Intelligence Pro
        </div>
        <div style='font-size: 11px; color: #58a6ff; letter-spacing: 2px; text-transform: uppercase; margin-top: 2px;'>
            Google Antigravity
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    coin_name = st.selectbox("🪙 Select Coin", list(COINS.keys()), index=0)
    ticker = COINS[coin_name]

    period_name = st.selectbox("📅 Timeframe", list(PERIODS.keys()), index=1)
    period = PERIODS[period_name]

    st.markdown("---")

    enable_alerts = st.toggle("📧 Enable Email Alerts", value=False)
    if enable_alerts and not EMAIL_CONFIGURED:
        st.warning("Update `email_config.py` with your Gmail App Password to enable alerts.")

    st.markdown("---")

    if st.button("🔄 Refresh All Data", use_container_width=True):
        st.cache_data.clear()

    st.markdown("""
    <div style='font-size: 11px; color: #8b949e; text-align: center; margin-top: 20px;'>
        Data: Yahoo Finance · RSS Feeds<br>
        Updated on demand
    </div>
    """, unsafe_allow_html=True)


# ─── Data Loading (cached) ────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_price_data(ticker, period):
    return fetch_price_data(ticker, period)

@st.cache_data(ttl=600)
def load_news():
    return fetch_crypto_news(max_per_feed=15)

@st.cache_data(ttl=600)
def load_political():
    return fetch_political_news(max_per_feed=10)


# ─── Header ───────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown(f"""
    <div style='padding: 8px 0;'>
        <span style='font-size: 28px; font-weight: 800; color: #e6edf3;'>{coin_name}</span>
        <span style='font-size: 14px; color: #8b949e; margin-left: 10px;'>{ticker} · {period_name}</span>
    </div>
    """, unsafe_allow_html=True)
with col_h2:
    st.markdown(f"""
    <div style='text-align: right; padding-top: 8px; color: #8b949e; font-size: 12px;'>
        {datetime.now().strftime('%b %d, %Y · %H:%M')}
    </div>
    """, unsafe_allow_html=True)


# ─── Offline Detection ────────────────────────────────────────────────────────
def _check_online() -> bool:
    try:
        import urllib.request
        urllib.request.urlopen("https://finance.yahoo.com", timeout=3)
        return True
    except Exception:
        return False

_online = _check_online()
if not _online:
    st.markdown("""
    <div style="background: #3a2d0d; border: 1px solid #f0c040; border-radius: 10px;
                padding: 12px 18px; margin-bottom: 16px; display:flex; align-items:center; gap:10px;">
        <span style="font-size:22px;">📡</span>
        <div>
            <span style="font-size:14px; font-weight:700; color:#f0c040;">OFFLINE MODE — Demo Data Active</span><br>
            <span style="font-size:12px; color:#8b949e;">
                Internet connection not detected. App is running with realistic sample data.
                Connect to internet and click <b style="color:#e6edf3;">🔄 Refresh All Data</b> to load live prices.
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Load price data early for top metrics ────────────────────────────────────
with st.spinner("Loading market data..."):
    df = load_price_data(ticker, period)

signal_data = generate_signal(df)
volatility = get_volatility(df)
risk_data = get_stop_loss_guidance(signal_data, volatility)

# Top metrics row
m1, m2, m3, m4, m5 = st.columns(5)
price = signal_data.get("price")
rsi = signal_data.get("rsi")

# Price change
if not df.empty and len(df) >= 2:
    close = df["Close"].squeeze()
    chg = float(close.iloc[-1] - close.iloc[-2])
    chg_pct = float(chg / close.iloc[-2] * 100)
    chg_str = f"{'▲' if chg >= 0 else '▼'} {abs(chg_pct):.2f}%"
    chg_color = "#3fb950" if chg >= 0 else "#f85149"
else:
    chg_str, chg_color = "N/A", "#8b949e"

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">💰 Price (USD)</div>
        <div class="metric-value">${price:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📈 24h Change</div>
        <div class="metric-value" style="color: {chg_color}; font-size: 20px;">{chg_str}</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    rsi_color = "#f85149" if rsi and rsi > 70 else ("#3fb950" if rsi and rsi < 30 else "#f0c040")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📊 RSI (14)</div>
        <div class="metric-value" style="color: {rsi_color};">{rsi if rsi else 'N/A'}</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    vol_color = {"LOW": "#3fb950", "MODERATE": "#f0c040", "HIGH": "#f85149"}.get(volatility["level"], "#8b949e")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">⚡ Volatility</div>
        <div class="metric-value" style="color: {vol_color}; font-size: 18px;">{volatility['level']}<br><span style='font-size:13px;'>{volatility['annual_vol']}% ann.</span></div>
    </div>
    """, unsafe_allow_html=True)

with m5:
    sig = signal_data.get("signal", "HOLD")
    sig_color = {"BUY": "#3fb950", "SELL": "#f85149", "HOLD": "#f0c040"}.get(sig, "#8b949e")
    sig_emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(sig, "⚪")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🎯 Signal</div>
        <div class="metric-value" style="color: {sig_color};">{sig_emoji} {sig}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─── Main Tabs ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Market Intelligence",
    "📰 News Sentiment",
    "🎤 Political Tracker",
    "🛡 Risk Management",
    "📧 Alert Center",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MARKET INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    if df.empty:
        st.error("⚠️ Failed to load price data. Check your internet connection and try refreshing.")
    else:
        close = df["Close"].squeeze()
        open_ = df["Open"].squeeze()
        high = df["High"].squeeze()
        low = df["Low"].squeeze()
        volume = df["Volume"].squeeze()

        ma50 = calculate_ma(close, 50)
        ma200 = calculate_ma(close, 200)
        rsi_series = calculate_rsi(close)

        # Build chart
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            row_heights=[0.7, 0.3],
            vertical_spacing=0.04,
            subplot_titles=("", "RSI (14)")
        )

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=open_, high=high, low=low, close=close,
            name="Price",
            increasing_line_color="#3fb950",
            decreasing_line_color="#f85149",
            increasing_fillcolor="#1a4731",
            decreasing_fillcolor="#4a1616",
        ), row=1, col=1)

        # MA lines
        if not ma50.dropna().empty:
            fig.add_trace(go.Scatter(
                x=df.index, y=ma50,
                name="50-MA", line=dict(color="#58a6ff", width=1.5, dash="dot"),
                hovertemplate="50-MA: $%{y:,.2f}<extra></extra>"
            ), row=1, col=1)

        if not ma200.dropna().empty:
            fig.add_trace(go.Scatter(
                x=df.index, y=ma200,
                name="200-MA", line=dict(color="#f0c040", width=1.5, dash="dash"),
                hovertemplate="200-MA: $%{y:,.2f}<extra></extra>"
            ), row=1, col=1)

        # RSI
        fig.add_trace(go.Scatter(
            x=df.index, y=rsi_series,
            name="RSI", line=dict(color="#bc8cff", width=2),
            hovertemplate="RSI: %{y:.1f}<extra></extra>"
        ), row=2, col=1)

        # RSI zones
        fig.add_hrect(y0=70, y1=100, row=2, col=1,
                      fillcolor="rgba(248,81,73,0.07)", line_width=0)
        fig.add_hrect(y0=0, y1=30, row=2, col=1,
                      fillcolor="rgba(63,185,80,0.07)", line_width=0)
        fig.add_hline(y=70, row=2, col=1, line=dict(color="#f85149", width=1, dash="dot"))
        fig.add_hline(y=30, row=2, col=1, line=dict(color="#3fb950", width=1, dash="dot"))

        fig.update_layout(
            height=580,
            paper_bgcolor="#0d1117",
            plot_bgcolor="#0d1117",
            font=dict(family="Inter", color="#8b949e", size=12),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02,
                bgcolor="rgba(22,27,34,0.8)",
                bordercolor="#30363d", borderwidth=1,
            ),
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=30, b=10),
            hovermode="x unified",
        )
        fig.update_xaxes(
            gridcolor="#1c2333", showgrid=True,
            zeroline=False, showspikes=True, spikecolor="#58a6ff", spikethickness=1
        )
        fig.update_yaxes(
            gridcolor="#1c2333", showgrid=True, zeroline=False,
            tickformat="$,.0f"
        )
        fig.update_yaxes(tickformat=".0f", row=2, col=1)

        st.plotly_chart(fig, use_container_width=True)

        # Signal explanation
        st.markdown('<div class="section-header">🎯 Signal Analysis</div>', unsafe_allow_html=True)
        css_class = f"signal-{sig.lower()}"
        c1, c2 = st.columns([1, 3])
        with c1:
            st.markdown(f'<div class="{css_class}">{sig_emoji} {sig}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="risk-block" style="text-align:left;">
                <div style="font-size: 13px; color: #8b949e; line-height: 1.8;">
                    {signal_data.get('reasoning', 'No analysis available.').replace(' | ', '<br>• ')}
                </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — NEWS SENTIMENT
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    with st.spinner("Fetching crypto news..."):
        news_df = load_news()

    summary = get_sentiment_summary(news_df)
    mood = summary["mood"]
    mood_color = {"BULLISH": "#3fb950", "BEARISH": "#f85149", "NEUTRAL": "#f0c040"}.get(mood, "#8b949e")
    mood_emoji = {"BULLISH": "🟢", "BEARISH": "🔴", "NEUTRAL": "🟡"}.get(mood, "⚪")

    # Sentiment summary metrics
    n1, n2, n3, n4 = st.columns(4)
    with n1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Overall Mood</div>
            <div class="metric-value" style="color:{mood_color}; font-size:20px;">{mood_emoji} {mood}</div>
        </div>""", unsafe_allow_html=True)
    with n2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🟢 Positive</div>
            <div class="metric-value" style="color:#3fb950;">{summary['positive']}</div>
        </div>""", unsafe_allow_html=True)
    with n3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🔴 Negative</div>
            <div class="metric-value" style="color:#f85149;">{summary['negative']}</div>
        </div>""", unsafe_allow_html=True)
    with n4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⚪ Neutral</div>
            <div class="metric-value" style="color:#8b949e;">{summary['neutral']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📰 Latest Headlines</div>', unsafe_allow_html=True)

    if news_df.empty:
        st.warning("No news articles loaded. Check your internet connection.")
    else:
        # Sentiment filter
        filter_col, _ = st.columns([1, 3])
        with filter_col:
            sent_filter = st.selectbox("Filter by sentiment", ["All", "POSITIVE", "NEGATIVE", "NEUTRAL"])

        display_df = news_df if sent_filter == "All" else news_df[news_df["sentiment"] == sent_filter]

        for _, row in display_df.iterrows():
            css = {"POSITIVE": "news-positive", "NEGATIVE": "news-negative"}.get(row["sentiment"], "news-neutral")
            badge_color = {"POSITIVE": "#3fb950", "NEGATIVE": "#f85149", "NEUTRAL": "#8b949e"}.get(row["sentiment"], "#8b949e")
            score_display = f"+{row['score']:.3f}" if row['score'] >= 0 else f"{row['score']:.3f}"
            st.markdown(f"""
            <div class="{css}" style="margin: 8px 0; padding: 10px 14px; background: #161b22; border-radius: 8px;">
                <div style="display:flex; justify-content: space-between; align-items: flex-start; gap: 10px;">
                    <div>
                        <a href="{row['link']}" target="_blank" style="color: #e6edf3; text-decoration: none; font-size: 13.5px; font-weight: 500; line-height: 1.5;">
                            {row['title']}
                        </a>
                        <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">
                            {row['source']} &bull; {row['published']}
                        </div>
                    </div>
                    <div style="white-space: nowrap; background: rgba(0,0,0,0.3); border: 1px solid {badge_color}; color: {badge_color}; border-radius: 6px; padding: 2px 10px; font-size: 11px; font-weight: 700; letter-spacing: 1px;">
                        {row['sentiment']}<br><span style="font-size: 10px; color:#8b949e;">{score_display}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — POLITICAL TRACKER
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    with st.spinner("Scanning political & macro news..."):
        pol_df = load_political()

    pol_summary = get_political_summary(pol_df)
    climate = pol_summary["climate"]
    climate_color = {
        "FAVORABLE": "#3fb950", "STABLE": "#58a6ff",
        "CAUTIOUS": "#f0c040", "HOSTILE": "#f85149"
    }.get(climate, "#8b949e")
    climate_emoji = {
        "FAVORABLE": "🟢", "STABLE": "🔵",
        "CAUTIOUS": "🟡", "HOSTILE": "🔴"
    }.get(climate, "⚪")

    if pol_summary["alert"]:
        st.markdown("""
        <div style="background: #4a1616; border: 1px solid #f85149; border-radius: 10px; padding: 14px 18px; margin-bottom: 16px;">
            ⚠️ <strong style="color: #f85149;">POLITICAL SHOCK ALERT</strong> — Multiple market-hostile headlines detected. 
            Review positions carefully.
        </div>
        """, unsafe_allow_html=True)

    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Political Climate</div>
            <div class="metric-value" style="color:{climate_color}; font-size:18px;">{climate_emoji} {climate}</div>
        </div>""", unsafe_allow_html=True)
    with p2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🟢 Bullish Events</div>
            <div class="metric-value" style="color:#3fb950;">{pol_summary['bullish']}</div>
        </div>""", unsafe_allow_html=True)
    with p3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🔴 Bearish Events</div>
            <div class="metric-value" style="color:#f85149;">{pol_summary['bearish']}</div>
        </div>""", unsafe_allow_html=True)
    with p4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⚪ Neutral Events</div>
            <div class="metric-value" style="color:#8b949e;">{pol_summary['neutral']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">🎤 Political & Macro Headlines</div>', unsafe_allow_html=True)

    if pol_df.empty:
        st.info("No political news found matching market-moving keywords at this time.")
    else:
        impact_filter_col, _ = st.columns([1, 3])
        with impact_filter_col:
            impact_filter = st.selectbox("Filter by impact", ["All", "BULLISH", "BEARISH", "NEUTRAL"])

        display_pol = pol_df if impact_filter == "All" else pol_df[pol_df["impact"] == impact_filter]

        for _, row in display_pol.iterrows():
            impact_color = {"BULLISH": "#3fb950", "BEARISH": "#f85149", "NEUTRAL": "#8b949e"}.get(row["impact"], "#8b949e")
            impact_emoji = {"BULLISH": "🟢", "BEARISH": "🔴", "NEUTRAL": "⚪"}.get(row["impact"], "⚪")
            border_color = impact_color
            st.markdown(f"""
            <div style="border-left: 3px solid {border_color}; padding: 10px 14px; background: #161b22; border-radius: 8px; margin: 8px 0;">
                <div style="display:flex; justify-content: space-between; align-items: flex-start; gap: 10px;">
                    <div>
                        <a href="{row['link']}" target="_blank" style="color: #e6edf3; text-decoration: none; font-size: 13.5px; font-weight: 500; line-height: 1.5;">
                            {row['title']}
                        </a>
                        <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">
                            {row['source']} &bull; {row['published']}
                        </div>
                    </div>
                    <div style="white-space: nowrap; background: rgba(0,0,0,0.3); border: 1px solid {impact_color}; color: {impact_color}; border-radius: 6px; padding: 3px 12px; font-size: 11px; font-weight: 700; letter-spacing: 1px;">
                        {impact_emoji} {row['impact']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Auto send political alert if enabled and hostile
        if enable_alerts and EMAIL_CONFIGURED and pol_summary["alert"]:
            hostile_rows = pol_df[pol_df["impact"] == "BEARISH"]
            if not hostile_rows.empty:
                top_row = hostile_rows.iloc[0]
                subj, body = build_political_alert(top_row["title"], top_row["impact"], top_row["source"])
                result = send_alert(subj, body)
                if result["success"]:
                    st.markdown('<div class="alert-success">📧 Political shock alert sent!</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — RISK MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">🛡 Risk Control Dashboard</div>', unsafe_allow_html=True)

    r1, r2, r3 = st.columns(3)
    with r1:
        sl = risk_data.get("stop_loss", "N/A")
        st.markdown(f"""
        <div class="risk-block" style="border-left: 3px solid #f85149;">
            <div style="font-size: 11px; letter-spacing: 1.5px; text-transform:uppercase; color:#f85149; margin-bottom:8px;">🛑 Stop Loss</div>
            <div style="font-size: 26px; font-weight: 800; color: #f85149;">${sl:,}</div>
            <div style="font-size: 12px; color:#8b949e; margin-top:6px;">Buffer: {risk_data.get('buffer_pct', 'N/A')} below entry<br>Exit if price drops to this level</div>
        </div>""", unsafe_allow_html=True)
    with r2:
        tp1 = risk_data.get("take_profit_1", "N/A")
        st.markdown(f"""
        <div class="risk-block" style="border-left: 3px solid #3fb950;">
            <div style="font-size: 11px; letter-spacing: 1.5px; text-transform:uppercase; color:#3fb950; margin-bottom:8px;">🎯 Take Profit 1</div>
            <div style="font-size: 26px; font-weight: 800; color: #3fb950;">${tp1:,}</div>
            <div style="font-size: 12px; color:#8b949e; margin-top:6px;">First exit target<br>Consider taking 50% profit here</div>
        </div>""", unsafe_allow_html=True)
    with r3:
        tp2 = risk_data.get("take_profit_2", "N/A")
        st.markdown(f"""
        <div class="risk-block" style="border-left: 3px solid #58a6ff;">
            <div style="font-size: 11px; letter-spacing: 1.5px; text-transform:uppercase; color:#58a6ff; margin-bottom:8px;">🚀 Take Profit 2</div>
            <div style="font-size: 26px; font-weight: 800; color: #58a6ff;">${tp2:,}</div>
            <div style="font-size: 12px; color:#8b949e; margin-top:6px;">Extended target<br>Let remaining 50% run here</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">⚡ Volatility Assessment</div>', unsafe_allow_html=True)

    vol_level = volatility.get("level", "MODERATE")
    vol_guidance = {
        "LOW": ("Markets are relatively calm. Standard position sizes acceptable. Wider stops less necessary.", "#3fb950"),
        "MODERATE": ("Moderate price swings expected. Use standard 8% stop-loss buffer. Don't over-leverage.", "#f0c040"),
        "HIGH": ("Extreme volatility detected. Reduce position sizes by 30–50%. Wide stops required. Capital preservation first.", "#f85149"),
    }
    vol_text, vol_color = vol_guidance.get(vol_level, ("Monitor closely.", "#8b949e"))

    st.markdown(f"""
    <div class="risk-block" style="border-left: 3px solid {vol_color};">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="font-size: 18px; font-weight: 800; color: {vol_color}; margin-bottom: 6px;">{vol_level} VOLATILITY</div>
                <div style="font-size: 13px; color: #8b949e;">{vol_text}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size: 28px; font-weight: 800; color: {vol_color};">{volatility['annual_vol']}%</div>
                <div style="font-size: 11px; color: #8b949e;">Annualised Vol</div>
                <div style="font-size: 14px; font-weight: 600; color: #8b949e; margin-top:4px;">{volatility['daily_vol']}% / day</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📐 Portfolio Allocation Guide</div>', unsafe_allow_html=True)

    al1, al2 = st.columns(2)
    with al1:
        st.markdown("""
        <div class="risk-block">
            <div style="font-size: 13px; font-weight: 700; color: #58a6ff; margin-bottom: 10px;">🎯 Recommended Allocation</div>
            <div style="font-size: 13px; color: #8b949e; line-height: 2;">
                🟢 BTC / ETH (Core) — 50–60% of portfolio<br>
                🔵 SOL / BNB / XRP (Mid-cap) — 20–30%<br>
                🟡 Altcoins / High-risk — max 10–15%<br>
                ⚪ Stablecoins (USDT/USDC) — 10–15% reserve
            </div>
        </div>""", unsafe_allow_html=True)
    with al2:
        st.markdown("""
        <div class="risk-block">
            <div style="font-size: 13px; font-weight: 700; color: #f0c040; margin-bottom: 10px;">⚠️ Risk Rules</div>
            <div style="font-size: 13px; color: #8b949e; line-height: 2;">
                🔴 Never risk more than 2–5% per trade<br>
                🔴 Never trade without a stop-loss<br>
                🟡 Don't chase pumps — wait for pullbacks<br>
                🟢 Scale in gradually — don't go all-in at once
            </div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — ALERT CENTER
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">📧 Email Alert Center</div>', unsafe_allow_html=True)

    if not EMAIL_CONFIGURED:
        st.markdown("""
        <div style="background: #3a2d0d; border: 1px solid #f0c040; border-radius: 10px; padding: 18px; margin-bottom: 16px;">
            <div style="font-size: 15px; font-weight: 700; color: #f0c040; margin-bottom: 8px;">⚙️ Setup Required</div>
            <div style="font-size: 13px; color: #8b949e; line-height: 1.8;">
                To enable email alerts, edit <strong style="color:#e6edf3;">email_config.py</strong> in your project folder:<br><br>
                1. Go to <a href="https://myaccount.google.com/apppasswords" target="_blank" style="color:#58a6ff;">myaccount.google.com/apppasswords</a><br>
                2. Generate a 16-character App Password<br>
                3. Fill in <code>SENDER_EMAIL</code>, <code>APP_PASSWORD</code>, and <code>RECEIVER_EMAIL</code>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.success("✅ Email alerts are configured and ready.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Manual alert trigger
    st.markdown('<div class="section-header">🚀 Manual Alert Trigger</div>', unsafe_allow_html=True)
    al_c1, al_c2 = st.columns([2, 1])
    with al_c1:
        st.info(f"Current signal: **{sig_emoji} {sig}** for {coin_name} @ ${price:,}")
    with al_c2:
        if st.button("📤 Send Signal Alert", use_container_width=True):
            if not EMAIL_CONFIGURED:
                st.error("Configure email_config.py first.")
            else:
                subj, body = build_signal_alert(coin_name, signal_data, risk_data)
                result = send_alert(subj, body)
                if result["success"]:
                    st.markdown(f'<div class="alert-success">✅ {result["message"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="alert-error">❌ {result["message"]}</div>', unsafe_allow_html=True)

    # Auto-alert on strong signals
    if enable_alerts and EMAIL_CONFIGURED and sig in ("BUY", "SELL"):
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">⚡ Auto-Alert Triggered</div>', unsafe_allow_html=True)
        subj, body = build_signal_alert(coin_name, signal_data, risk_data)
        result = send_alert(subj, body)
        if result["success"]:
            st.markdown(f'<div class="alert-success">✅ Auto-alert sent: {result["message"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-error">❌ Auto-alert failed: {result["message"]}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="risk-block">
        <div style="font-size: 13px; font-weight: 700; color: #e6edf3; margin-bottom: 10px;">📋 Alert Types</div>
        <div style="font-size: 13px; color: #8b949e; line-height: 2;">
            🟢 <strong style="color:#3fb950;">BUY Signal</strong> — Sent when RSI + MA analysis confirms buying opportunity<br>
            🔴 <strong style="color:#f85149;">SELL Signal</strong> — Sent when overbought conditions detected across indicators<br>
            ⚠️ <strong style="color:#f0c040;">Political Shock</strong> — Sent when hostile macro news is detected in Political Tracker<br>
            ⚪ <strong style="color:#8b949e;">HOLD Signal</strong> — No alert sent (no action required)
        </div>
    </div>
    """, unsafe_allow_html=True)
