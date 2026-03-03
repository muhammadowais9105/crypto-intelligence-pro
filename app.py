"""
app.py
Crypto Intelligence Pro
"""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
// Get Monaco editor instance and replace content
const editor = monaco.editor.getEditors()[0];
const newContent = `"""
app.py
Crypto Intelligence Pro - Main Streamlit Dashboard
Google Antigravity | A next-generation crypto decision support system
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime

from trading_logic import (
    COINS, PERIODS, fetch_price_data, calculate_rsi, calculate_ma,
    generate_signal, get_volatility, get_stop_loss_guidance
)
from news_sentiment import fetch_crypto_news, get_sentiment_summary
from political_tracker import fetch_political_news, get_political_summary
from email_alerts import send_alert, build_signal_alert, build_political_alert, EMAIL_CONFIGURED

st.set_page_config(
        page_title="Crypto Intelligence Pro",
        page_icon="Rocket",
        layout="wide",
        initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0d1117 0%, #0f1923 50%, #0d1117 100%); color: #e6edf3; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #111827 0%, #0d1117 100%); border-right: 1px solid #1f2937; }
            .metric-card { background: linear-gradient(135deg, #161b22 0%, #1c2333 100%); border: 1px solid #30363d; border-radius: 12px; padding: 18px 20px; text-align: center; transition: all 0.3s ease; }
                .metric-card:hover { border-color: #58a6ff; box-shadow: 0 0 20px rgba(88,166,255,0.15); transform: translateY(-2px); }
                    .metric-label { font-size: 11px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; color: #8b949e; margin-bottom: 6px; }
                        .metric-value { font-size: 26px; font-weight: 800; color: #e6edf3; }
                            .signal-buy { background: linear-gradient(135deg,#1a4731,#0d6638); color: #3fb950; border: 1px solid #3fb950; border-radius: 10px; padding: 14px 28px; font-size: 22px; font-weight: 800; text-align: center; }
                                .signal-sell { background: linear-gradient(135deg,#4a1616,#7a1e1e); color: #f85149; border: 1px solid #f85149; border-radius: 10px; padding: 14px 28px; font-size: 22px; font-weight: 800; text-align: center; }
                                    .signal-hold { background: linear-gradient(135deg,#3a2d0d,#5a4a1a); color: #f0c040; border: 1px solid #f0c040; border-radius: 10px; padding: 14px 28px; font-size: 22px; font-weight: 800; text-align: center; }
                                        .section-header { font-size: 15px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #58a6ff; border-bottom: 1px solid #21262d; padding-bottom: 8px; margin: 20px 0 14px 0; }
                                            .news-positive { border-left: 3px solid #3fb950; padding-left: 10px; margin: 6px 0; }
                                                .news-negative { border-left: 3px solid #f85149; padding-left: 10px; margin: 6px 0; }
                                                    .news-neutral { border-left: 3px solid #8b949e; padding-left: 10px; margin: 6px 0; }
                                                        .stTabs [data-baseweb="tab-list"] { background: #161b22; border-radius: 10px; padding: 4px; border: 1px solid #30363d; }
                                                            .stTabs [data-baseweb="tab"] { border-radius: 8px; color: #8b949e; font-weight: 600; font-size: 13px; padding: 8px 18px; }
                                                                .stTabs [aria-selected="true"] { background: #21262d; color: #e6edf3; }
                                                                    hr { border-color: #21262d; margin: 16px 0; }
                                                                        .risk-block { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 16px; margin: 8px 0; }
                                                                          
