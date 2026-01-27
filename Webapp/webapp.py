import streamlit as st
import streamlit.components.v1 as components
import requests
import time
import os

# ==========================================
# ၁။ Setting & Configuration
# ==========================================
API_KEY = "b005ad2097b843d59d9c44ddfd3f9038"

# Weight: 16.606 Grams per Tical
CONVERSION_FACTOR = 16.606 / 31.1034768
GOLD_SPREAD = 5000
SILVER_SPREAD = 1000

# Sidebar Config
st.set_page_config(page_title="VIP Group Exchange", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 🛑 UI CLEANER
# ==========================================
hide_streamlit_style = """
    <style>
    footer {display: none !important;}
    [data-testid="stFooter"] {display: none !important;}
    .stAppDeployButton {display: none !important;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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
if 'spot_assets' not in st.session_state:
    st.session_state.spot_assets = {"Gold": 0.0, "Silver": 0.0}

# Future Market နဲ့ဆိုင်တဲ့ State တွေကို ဖယ်လိုက်ပါပြီ

if 'deposit_requests' not in st.session_state:
    st.session_state.deposit_requests = [
        {"id": 1, "user": "Test User", "amount": 1000000, "status": "Pending"},
    ]
if 'transaction_history' not in st.session_state:
    st.session_state.transaction_history = []

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

def calculate_mmk(usd_price):
    return int((usd_price * CONVERSION_FACTOR) * st.session_state.usd_rate)

def fmt_price(mmk_value):
    return f"{mmk_value/100000:,.2f}"

# ==========================================
# ၄။ SIDEBAR
# ==========================================
with st.sidebar:
    st.header("⚙️ System Control")
    status_color = "green" if "Live" in st.session_state.price_status else "red"
    st.markdown(f"API Status: :{status_color}[{st.session_state.price_status}]")
    
    if st.button("Refresh System"):
        st.rerun()
    st.divider()
    
    st.subheader("Currency Setting")
    new_rate = st.number_input("USD Rate", value=st.session_state.usd_rate, format="%.2f")
    if st.button("Update Rate"):
        st.session_state.usd_rate = new_rate
        st.cache_data.clear()
        st.rerun()
    st.divider()
    
    st.subheader("💰 Deposit (Test)")
    pending_list = [d for d in st.session_state.deposit_requests if d['status'] == "Pending"]
    if not pending_list:
        st.info("No pending requests.")
    else:
        for req in pending_list:
            with st.expander(f"{req['user']} : {req['amount']:,} Ks"):
                if st.button("✅ Approve", key=f"app_{req['id']}"):
                    req['status'] = "Approved"
                    st.session_state.user_balance += req['amount']
                    st.rerun()

# ==========================================
# ၅။ MAIN DASHBOARD
# ==========================================
col_logo, col_title = st.columns([1, 7])

with col_logo:
    if os.path.exists("vip_logo.png"):
        st.image("vip_logo.png", width=100)
    elif os.path.exists("vip_logo.jpg"):
        st.image("vip_logo.jpg", width=85)
    else:
        st.write("## 🏆")

with col_title:
    st.title("VIP Group Gold & Silver Exchange")

st.write(f"**Western Union Rate:** 1 USD = {st.session_state.usd_rate:,.2f} MMK")

@st.fragment(run_every=5)
def show_market_section():
    fetch_realtime_prices()
    
    gold_usd = st.session_state.last_gold_price
    silver_usd = st.session_state.last_silver_price
    gold_mmk = calculate_mmk(gold_usd)
    silver_mmk = calculate_mmk(silver_usd)

    # 🛑 TAB များကို ဖယ်ရှားလိုက်ပြီး Spot Market ကို တိုက်ရိုက်ပြသခြင်း
    st.subheader("📦 Spot Market")
    c1, c2 = st.columns(2)
    
    # Gold Section
    with c1:
        st.metric(label="World Price", value=f"${gold_usd:,.2f}") 
        st.info(f"**Gold Base:** {fmt_price(gold_mmk)} Lakhs")
        spot_buy_g = gold_mmk + GOLD_SPREAD
        spot_sell_g = gold_mmk - GOLD_SPREAD
        if st.button(f"Buy Gold\n{fmt_price(spot_buy_g)}", key="s_bg", use_container_width=True):
            if st.session_state.user_balance >= spot_buy_g:
                st.session_state.user_balance -= spot_buy_g
                st.session_state.spot_assets["Gold"] += 1.0
                st.session_state.transaction_history.append(f"Spot: Bought Gold @ {fmt_price(spot_buy_g)}")
                st.success("Bought!")
            else:
                st.error("Low Balance!")
        if st.button(f"Sell Gold\n{fmt_price(spot_sell_g)}", key="s_sg", use_container_width=True):
            if st.session_state.spot_assets["Gold"] >= 1.0:
                st.session_state.user_balance += spot_sell_g
                st.session_state.spot_assets["Gold"] -= 1.0
                st.session_state.transaction_history.append(f"Spot: Sold Gold @ {fmt_price(spot_sell_g)}")
                st.success("Sold!")
            else:
                st.error("No Gold!")

    # Silver Section
    with c2:
        st.metric(label="World Price", value=f"${silver_usd:,.2f}") 
        st.info(f"**Silver Base:** {fmt_price(silver_mmk)} Lakhs")
        spot_buy_s = silver_mmk + SILVER_SPREAD
        spot_sell_s = silver_mmk - SILVER_SPREAD
        if st.button(f"Buy Silver\n{fmt_price(spot_buy_s)}", key="s_bs", use_container_width=True):
            if st.session_state.user_balance >= spot_buy_s:
                st.session_state.user_balance -= spot_buy_s
                st.session_state.spot_assets["Silver"] += 1.0
                st.session_state.transaction_history.append(f"Spot: Bought Silver @ {fmt_price(spot_buy_s)}")
                st.success("Bought!")
            else:
                st.error("Low Balance!")
        if st.button(f"Sell Silver\n{fmt_price(spot_sell_s)}", key="s_ss", use_container_width=True):
            if st.session_state.spot_assets["Silver"] >= 1.0:
                st.session_state.user_balance += spot_sell_s
                st.session_state.spot_assets["Silver"] -= 1.0
                st.session_state.transaction_history.append(f"Spot: Sold Silver @ {fmt_price(spot_sell_s)}")
                st.success("Sold!")
            else:
                st.error("No Silver!")

show_market_section()

# ==========================================
# ၆။ WALLET SUMMARY
# ==========================================
st.divider()
st.subheader("👤 My Wallet")
w1, w2, w3 = st.columns(3)
w1.metric("Cash Balance", f"{st.session_state.user_balance:,.0f} Ks")
w2.metric("Spot Gold", f"{st.session_state.spot_assets['Gold']:.2f} Tical")
w3.metric("Spot Silver", f"{st.session_state.spot_assets['Silver']:.2f} Tical")

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
