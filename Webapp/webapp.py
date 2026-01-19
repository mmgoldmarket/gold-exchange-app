import streamlit as st
import streamlit.components.v1 as components
import requests
import time

# ==========================================
# ၁။ Setting (အရေးကြီးဆုံးအပိုင်း)
# ==========================================
# 👉 အစ်ကို့ Dashboard က "Reveal" နှိပ်ပြီးရလာတဲ့ Key ကို ဒီမှာထည့်ပါ
API_KEY = "b005ad2097b843d59d9c44ddfd3f9038" 

CONVERSION_FACTOR = 16.329 / 31.1034768
GOLD_SPREAD = 5000
SILVER_SPREAD = 1000

st.set_page_config(page_title="Gold Exchange Admin", layout="wide")

# ==========================================
# ၂။ Session State
# ==========================================
if 'usd_rate' not in st.session_state:
    st.session_state.usd_rate = 3959.1 

if 'user_balance' not in st.session_state:
    st.session_state.user_balance = 0.0

if 'user_assets' not in st.session_state:
    st.session_state.user_assets = {"Gold": 0.0, "Silver": 0.0}

if 'transaction_history' not in st.session_state:
    st.session_state.transaction_history = []

if 'deposit_requests' not in st.session_state:
    st.session_state.deposit_requests = [
        {"id": 1, "user": "Mg Mg", "amount": 1000000, "status": "Pending"},
    ]

if 'user_messages' not in st.session_state:
    st.session_state.user_messages = []

# ==========================================
# ၃။ Price Fetching (Batch Request for Limit Saving)
# ==========================================
@st.cache_data(ttl=20) # 20 စက္ကန့် Cache (Limit မကျော်အောင် ထိန်းထားသည်)
def get_all_prices():
    # Gold နှင့် Silver ကို ကော်မာခံပြီး တစ်ခါတည်း လှမ်းယူသည် (1 Credit ပဲကုန်မယ်)
    url = f"https://api.twelvedata.com/price?symbol=XAU/USD,XAG/USD&apikey={API_KEY}"
    
    prices = {"XAU": 2650.00, "XAG": 31.50, "error": None}
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # Error Checking
        if "code" in data and data["code"] != 200:
             prices["error"] = data.get("message", "API Limit Reached")
        else:
            # Success Parsing (Batch Response ပုံစံ)
            if "XAU/USD" in data:
                prices["XAU"] = float(data["XAU/USD"]["price"])
            
            if "XAG/USD" in data:
                prices["XAG"] = float(data["XAG/USD"]["price"])
                
    except Exception as e:
        prices["error"] = str(e)
        
    return prices

def calculate_mmk(usd_price):
    return int((usd_price * CONVERSION_FACTOR) * st.session_state.usd_rate)

def fmt_price(mmk_value):
    return f"{mmk_value/100000:,.2f}"

# ==========================================
# ၄။ Website UI
# ==========================================

with st.sidebar:
    st.header("🔧 Admin Control")
    
    # Refresh ခလုတ်
    if st.button("🔄 Force Refresh"):
        st.cache_data.clear()
        st.rerun()
        
    auto_refresh = st.checkbox("Running Auto Refresh (20s)", value=True)

    st.divider()
    with st.expander("🛠 API Debugger"):
        # ဒီနေရာမှာ API က ဘာပို့လိုက်လဲ အတိအကျပြပါမယ်
        st.write(f"Using Key: ...{API_KEY[-4:] if len(API_KEY)>4 else 'None'}")
        data = get_all_prices()
        if data['error']:
            st.error(f"Error: {data['error']}")
        else:
            st.success("API Connected Successfully!")
            st.json(data)

    st.write("---")
    st.write("Exchange Rate Setting")
    new_rate = st.number_input("Western Union Rate", value=st.session_state.usd_rate)
    if st.button("Update Rate"):
        st.session_state.usd_rate = new_rate
        st.success("Updated!")

# --- MAIN PAGE ---
st.title("🏆 Myanmar Gold & Silver Exchange")

# Data ဆွဲယူခြင်း
data = get_all_prices()
gold_usd = data['XAU']
silver_usd = data['XAG']

if data['error']:
    st.warning(f"⚠️ API Error: {data['error']} (Showing Backup Prices)")

gold_mmk = calculate_mmk(gold_usd)
silver_mmk = calculate_mmk(silver_usd)

col1, col2 = st.columns(2)

# GOLD
with col1:
    st.subheader("🟡 Gold (ရွှေ)")
    st.metric("World Price", f"${gold_usd:,.2f}")
    st.info(f"Base: {fmt_price(gold_mmk)}")
    
    buy = gold_mmk + GOLD_SPREAD
    sell = gold_mmk - GOLD_SPREAD
    
    b, s = st.columns(2)
    if b.button(f"Buy Gold\n{fmt_price(buy)}", key="bg", use_container_width=True):
        st.session_state.user_balance -= buy
        st.session_state.user_assets["Gold"] += 1
        st.success("Bought!")
    if s.button(f"Sell Gold\n{fmt_price(sell)}", key="sg", use_container_width=True):
        st.session_state.user_assets["Gold"] -= 1
        st.session_state.user_balance += sell
        st.success("Sold!")

# SILVER
with col2:
    st.subheader("⚪ Silver (ငွေ)")
    st.metric("World Price", f"${silver_usd:,.3f}")
    st.info(f"Base: {fmt_price(silver_mmk)}")
    
    buy_s = silver_mmk + SILVER_SPREAD
    sell_s = silver_mmk - SILVER_SPREAD
    
    b, s = st.columns(2)
    if b.button(f"Buy Silver\n{fmt_price(buy_s)}", key="bs", use_container_width=True):
        st.session_state.user_balance -= buy_s
        st.session_state.user_assets["Silver"] += 1
        st.success("Bought!")
    if s.button(f"Sell Silver\n{fmt_price(sell_s)}", key="ss", use_container_width=True):
        st.session_state.user_assets["Silver"] -= 1
        st.session_state.user_balance += sell_s
        st.success("Sold!")

st.divider()
st.subheader("👤 My Wallet")
c1, c2, c3 = st.columns(3)
c1.metric("Balance", f"{st.session_state.user_balance:,.0f} Ks")
c2.metric("Gold", f"{st.session_state.user_assets['Gold']} Tical")
c3.metric("Silver", f"{st.session_state.user_assets['Silver']} Tical")

# Javascript Refresh Logic (20 Seconds)
if auto_refresh:
    components.html(
        f"""
            <script>
                var timeLeft = 20;
                var timer = setInterval(function() {{
                    timeLeft--;
                    if (timeLeft <= 0) {{
                        window.parent.location.reload();
                    }}
                }}, 1000);
            </script>
        """,
        height=0
    )
