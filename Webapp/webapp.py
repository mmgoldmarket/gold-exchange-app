import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import plotly.graph_objects as go
import time

# ==========================================
# ၁။ Setting & Configuration
# ==========================================
API_KEY = "b005ad2097b843d59d9c44ddfd3f9038"  # ⚠️ Paid Key ကို ထည့်ပါ

# ⚠️ New Formula: 16.606 Grams per Tical (Standard)
CONVERSION_FACTOR = 16.606 / 31.1034768
GOLD_SPREAD = 5000
SILVER_SPREAD = 1000

st.set_page_config(page_title="Gold Exchange Admin", layout="wide")

# ==========================================
# ၂။ Session State Initialization
# ==========================================
if 'last_gold_price' not in st.session_state:
    st.session_state.last_gold_price = 2650.00
if 'last_silver_price' not in st.session_state:
    st.session_state.last_silver_price = 31.50
if 'price_status' not in st.session_state:
    st.session_state.price_status = "Init"
if 'usd_rate' not in st.session_state:
    st.session_state.usd_rate = 3959.1 
if 'user_balance' not in st.session_state:
    st.session_state.user_balance = 0.0
if 'user_assets' not in st.session_state:
    st.session_state.user_assets = {"Gold": 0.0, "Silver": 0.0}
if 'deposit_requests' not in st.session_state:
    st.session_state.deposit_requests = [
        {"id": 1, "user": "Mg Mg", "amount": 1000000, "status": "Pending"},
    ]
if 'transaction_history' not in st.session_state:
    st.session_state.transaction_history = []
if 'user_messages' not in st.session_state:
    st.session_state.user_messages = []

# ==========================================
# ၃။ Helper Functions
# ==========================================

def fetch_realtime_prices():
    url = f"https://api.twelvedata.com/price?symbol=XAU/USD,XAG/USD&apikey={API_KEY}"
    try:
        response = requests.get(url, timeout=2) 
        data = response.json()
        if "code" in data and data["code"] != 200:
             st.session_state.price_status = "Offline"
        else:
            if "XAU/USD" in data:
                st.session_state.last_gold_price = float(data["XAU/USD"]["price"])
            if "XAG/USD" in data:
                st.session_state.last_silver_price = float(data["XAG/USD"]["price"])
            st.session_state.price_status = "Live 🟢"     
    except:
        pass

# Chart Data ဆွဲယူခြင်း (USD)
@st.cache_data(ttl=60) 
def get_chart_data_usd(symbol):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&outputsize=30&apikey={API_KEY}"
    try:
        res = requests.get(url).json()
        if 'values' in res:
            df = pd.DataFrame(res['values'])
            df['datetime'] = pd.to_datetime(df['datetime'])
            
            cols = ['open', 'high', 'low', 'close']
            df[cols] = df[cols].astype(float)
            return df
    except:
        return None
    return None

# Chart ပုံဖော်ခြင်း (MMK Base Price အတိုင်းတွက်မည်)
def plot_mmk_chart(df_usd, title, rate):
    if df_usd is None:
        return None
    
    # ⚠️ Updated Formula Logic
    df_mmk = df_usd.copy()
    
    # သိန်းဂဏန်း (Lakhs) အဖြစ်ပြောင်းလဲခြင်း Factor
    # (Weight Factor * Exchange Rate) / 100000
    factor = (CONVERSION_FACTOR * rate) / 100000
    
    df_mmk['open'] = df_mmk['open'] * factor
    df_mmk['high'] = df_mmk['high'] * factor
    df_mmk['low'] = df_mmk['low'] * factor
    df_mmk['close'] = df_mmk['close'] * factor
    
    fig = go.Figure(data=[go.Candlestick(
        x=df_mmk['datetime'],
        open=df_mmk['open'], high=df_mmk['high'],
        low=df_mmk['low'], close=df_mmk['close'],
        increasing_line_color="#28a745", 
        decreasing_line_color="#dc3545"
    )])
    
    fig.update_layout(
        title=f"{title} (Base Price - Lakhs)",
        height=350,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        yaxis_tickformat=".2f"
    )
    return fig

def calculate_mmk(usd_price):
    return int((usd_price * CONVERSION_FACTOR) * st.session_state.usd_rate)

def fmt_price(mmk_value):
    return f"{mmk_value/100000:,.2f}"

# ==========================================
# ၄။ MAIN UI
# ==========================================

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔧 Admin Control")
    status_color = "green" if "Live" in st.session_state.price_status else "red"
    st.markdown(f"Status: :{status_color}[{st.session_state.price_status}]")
    
    if st.button("Manual Page Reload"):
        st.rerun()

    st.divider()
    st.write("Rate Setting")
    new_rate = st.number_input("Exchange Rate (MMK)", value=st.session_state.usd_rate)
    if st.button("Update Rate"):
        st.session_state.usd_rate = new_rate
        st.cache_data.clear()
        st.rerun()

# --- HEADER ---
st.title("🏆 Myanmar Gold & Silver Exchange")
st.write(f"**Exchange Rate:** 1 USD = {st.session_state.usd_rate:,.0f} MMK")

# ==========================================
# ၅။ Market Display Fragment (3s Refresh)
# ==========================================
@st.fragment(run_every=3)
def show_market_section():
    fetch_realtime_prices()
    
    gold_usd = st.session_state.last_gold_price
    silver_usd = st.session_state.last_silver_price
    
    gold_mmk = calculate_mmk(gold_usd)
    silver_mmk = calculate_mmk(silver_usd)
    
    # --- TABS ---
    tab1, tab2 = st.tabs(["📊 Market Overview", "📈 Live Charts (Base Price)"])
    
    # TAB 1: Trading Buttons
    with tab1:
        col1, col2 = st.columns(2)

        # GOLD
        with col1:
            st.subheader("🟡 Gold (ရွှေ)")
            st.metric(label="World Price", value=f"${gold_usd:,.2f}")
            st.info(f"**Base:** {fmt_price(gold_mmk)} (Lakhs)")
            
            buy = gold_mmk + GOLD_SPREAD
            sell = gold_mmk - GOLD_SPREAD
            
            b, s = st.columns(2)
            if b.button(f"Buy Gold\n{fmt_price(buy)}", key="bg", use_container_width=True):
                if st.session_state.user_balance >= buy:
                    st.session_state.user_balance -= buy
                    st.session_state.user_assets["Gold"] += 1.0
                    st.session_state.transaction_history.append(f"Bought Gold @ {fmt_price(buy)}")
                    st.success("Bought!")
                else:
                    st.error("Low Balance!")

            if s.button(f"Sell Gold\n{fmt_price(sell)}", key="sg", use_container_width=True):
                if st.session_state.user_assets["Gold"] >= 1.0:
                    st.session_state.user_balance += sell
                    st.session_state.user_assets["Gold"] -= 1.0
                    st.session_state.transaction_history.append(f"Sold Gold @ {fmt_price(sell)}")
                    st.success("Sold!")
                else:
                    st.error("No Gold!")

        # SILVER
        with col2:
            st.subheader("⚪ Silver (ငွေ)")
            st.metric(label="World Price", value=f"${silver_usd:,.3f}")
            st.info(f"**Base:** {fmt_price(silver_mmk)} (Lakhs)")
            
            buy_s = silver_mmk + SILVER_SPREAD
            sell_s = silver_mmk - SILVER_SPREAD
            
            b, s = st.columns(2)
            if b.button(f"Buy Silver\n{fmt_price(buy_s)}", key="bs", use_container_width=True):
                if st.session_state.user_balance >= buy_s:
                    st.session_state.user_balance -= buy_s
                    st.session_state.user_assets["Silver"] += 1.0
                    st.session_state.transaction_history.append(f"Bought Silver @ {fmt_price(buy_s)}")
                    st.success("Bought!")
                else:
                    st.error("Low Balance!")

            if s.button(f"Sell Silver\n{fmt_price(sell_s)}", key="ss", use_container_width=True):
                if st.session_state.user_assets["Silver"] >= 1.0:
                    st.session_state.user_balance += sell_s
                    st.session_state.user_assets["Silver"] -= 1.0
                    st.session_state.transaction_history.append(f"Sold Silver @ {fmt_price(sell_s)}")
                    st.success("Sold!")
                else:
                    st.error("No Silver!")

    # TAB 2: MMK Charts
    with tab2:
        st.caption(f"Charts showing Base Price in MMK (Lakhs) @ Rate: {st.session_state.usd_rate}")
        c1, c2 = st.columns(2)
        current_rate = st.session_state.usd_rate
        
        # Gold Chart
        with c1:
            df_gold = get_chart_data_usd("XAU/USD")
            if df_gold is not None:
                fig_g = plot_mmk_chart(df_gold, "Gold Base Price", current_rate)
                st.plotly_chart(fig_g, use_container_width=True, key="chart_gold")
            else:
                st.warning("Loading Gold Chart...")

        # Silver Chart
        with c2:
            df_silver = get_chart_data_usd("XAG/USD")
            if df_silver is not None:
                fig_s = plot_mmk_chart(df_silver, "Silver Base Price", current_rate)
                st.plotly_chart(fig_s, use_container_width=True, key="chart_silver")
            else:
                st.warning("Loading Silver Chart...")

show_market_section()

# ==========================================
# ၆။ Wallet & Styles
# ==========================================
st.divider()
st.subheader("👤 My Wallet")
w1, w2, w3 = st.columns(3)
w1.metric("Cash Balance", f"{st.session_state.user_balance:,.0f} Ks")
w2.metric("Gold Assets", f"{st.session_state.user_assets['Gold']:.2f} Tical")
w3.metric("Silver Assets", f"{st.session_state.user_assets['Silver']:.2f} Tical")

components.html("""
<script>
    setInterval(function() {
        var buttons = window.parent.document.querySelectorAll('button');
        for (var i = 0; i < buttons.length; i++) {
            var text = buttons[i].innerText;
            if (text.includes("Buy")) {
                buttons[i].style.backgroundColor = "#28a745"; 
                buttons[i].style.color = "white";
                buttons[i].style.borderColor = "#28a745";
            }
            else if (text.includes("Sell")) {
                buttons[i].style.backgroundColor = "#dc3545"; 
                buttons[i].style.color = "white";
                buttons[i].style.borderColor = "#dc3545";
            }
        }
    }, 500); 
</script>
""", height=0)
