import streamlit as st
import requests
import time

# ==========================================
# ၁။ Setting & Configuration
# ==========================================
# ⚠️ Plan ဝယ်ထားသော Key ကိုသာ ထည့်ပါ (Free Key ဆိုရင် 5s refresh နဲ့ မခံပါ)
API_KEY = "b005ad2097b843d59d9c44ddfd3f9038"  

CONVERSION_FACTOR = 16.329 / 31.1034768
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
        {"id": 2, "user": "Ko Kyaw", "amount": 5000000, "status": "Pending"},
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
        response = requests.get(url, timeout=3)
        data = response.json()
        
        if "code" in data and data["code"] != 200:
             st.session_state.price_status = "Offline (API Error)"
        else:
            if "XAU/USD" in data:
                st.session_state.last_gold_price = float(data["XAU/USD"]["price"])
            if "XAG/USD" in data:
                st.session_state.last_silver_price = float(data["XAG/USD"]["price"])
            st.session_state.price_status = "Live 🟢"     
    except:
        st.session_state.price_status = "Offline (Net Error)"
        pass

def calculate_mmk(usd_price):
    return int((usd_price * CONVERSION_FACTOR) * st.session_state.usd_rate)

def fmt_price(mmk_value):
    return f"{mmk_value/100000:,.2f}"

# ==========================================
# ၄။ MAIN UI - Sidebar & Header
# ==========================================

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔧 Admin Control")
    
    # Status
    status_color = "green" if "Live" in st.session_state.price_status else "red"
    st.markdown(f"Status: :{status_color}[{st.session_state.price_status}]")
    
    if st.button("Manual Page Reload"):
        st.rerun()

    st.divider()
    st.write("Exchange Rate Setting")
    new_rate = st.number_input("Western Union Rate (MMK)", value=st.session_state.usd_rate)
    if st.button("Update Rate"):
        st.session_state.usd_rate = new_rate
        st.success("Updated!")
        time.sleep(0.5)
        st.rerun()

    # Requests
    st.subheader("💰 Deposit Requests")
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

# --- HEADER ---
st.title("🏆 Myanmar Gold & Silver Exchange")
st.write(f"**Exchange Rate:** 1 USD = {st.session_state.usd_rate:,.0f} MMK")

if st.session_state.user_messages:
    with st.expander("📬 Messages from Admin"):
        for msg in reversed(st.session_state.user_messages):
            st.info(f"**Admin ({msg['time']}):** {msg['text']}")

# ==========================================
# ၅။ Market Display Fragment (The Magic Part ✨)
# ==========================================
# ဒီ Function တစ်ခုတည်းသာ ၅ စက္ကန့်တစ်ခါ Run ပါမယ်။ Page တခုလုံး မ Run ပါ။
@st.fragment(run_every=5)
def show_market_section():
    # 1. Fetch New Data
    fetch_realtime_prices()
    
    # 2. Get Data
    gold_usd = st.session_state.last_gold_price
    silver_usd = st.session_state.last_silver_price
    
    gold_mmk = calculate_mmk(gold_usd)
    silver_mmk = calculate_mmk(silver_usd)
    
    col1, col2 = st.columns(2)

    # --- GOLD UI ---
    with col1:
        st.subheader("🟡 Gold (ရွှေ)")
        st.metric(label="World Price", value=f"${gold_usd:,.2f}")
        st.info(f"**Base Price:** {fmt_price(gold_mmk)}")
        
        buy_price = gold_mmk + GOLD_SPREAD
        sell_price = gold_mmk - GOLD_SPREAD
        
        b_col, s_col = st.columns(2)
        if b_col.button(f"Buy Gold\n{fmt_price(buy_price)}", key="bg", use_container_width=True):
            if st.session_state.user_balance >= buy_price:
                st.session_state.user_balance -= buy_price
                st.session_state.user_assets["Gold"] += 1.0
                st.session_state.transaction_history.append(f"Bought Gold @ {fmt_price(buy_price)}")
                st.success("Bought!")
            else:
                st.error("Insufficient Funds!")

        if s_col.button(f"Sell Gold\n{fmt_price(sell_price)}", key="sg", use_container_width=True):
            if st.session_state.user_assets["Gold"] >= 1.0:
                st.session_state.user_balance += sell_price
                st.session_state.user_assets["Gold"] -= 1.0
                st.session_state.transaction_history.append(f"Sold Gold @ {fmt_price(sell_price)}")
                st.success("Sold!")
            else:
                st.error("No Gold!")

    # --- SILVER UI ---
    with col2:
        st.subheader("⚪ Silver (ငွေ)")
        st.metric(label="World Price", value=f"${silver_usd:,.3f}")
        st.info(f"**Base Price:** {fmt_price(silver_mmk)}")
        
        buy_price_s = silver_mmk + SILVER_SPREAD
        sell_price_s = silver_mmk - SILVER_SPREAD
        
        b_col_s, s_col_s = st.columns(2)
        if b_col_s.button(f"Buy Silver\n{fmt_price(buy_price_s)}", key="bs", use_container_width=True):
            if st.session_state.user_balance >= buy_price_s:
                st.session_state.user_balance -= buy_price_s
                st.session_state.user_assets["Silver"] += 1.0
                st.session_state.transaction_history.append(f"Bought Silver @ {fmt_price(buy_price_s)}")
                st.success("Bought!")
            else:
                st.error("Insufficient Funds!")

        if s_col_s.button(f"Sell Silver\n{fmt_price(sell_price_s)}", key="ss", use_container_width=True):
            if st.session_state.user_assets["Silver"] >= 1.0:
                st.session_state.user_balance += sell_price_s
                st.session_state.user_assets["Silver"] -= 1.0
                st.session_state.transaction_history.append(f"Sold Silver @ {fmt_price(sell_price_s)}")
                st.success("Sold!")
            else:
                st.error("No Silver!")

# ဈေးကွက်ပြမယ့် Fragment ကို ခေါ်သုံးခြင်း
show_market_section()

# ==========================================
# ၆။ Wallet Display (Static - No Auto Refresh)
# ==========================================
st.divider()
st.subheader("👤 My Wallet")
# Wallet ကို Fragment အပြင်ထုတ်ထားတာမို့လို့ Page ငြိမ်နေပါမယ်
# Buy/Sell နှိပ်မှသာ ဂဏန်းပြောင်းပါမယ်
w_col1, w_col2, w_col3 = st.columns(3)
w_col1.metric("Cash Balance", f"{st.session_state.user_balance:,.0f} Ks")
w_col2.metric("Gold Assets", f"{st.session_state.user_assets['Gold']:.2f} Tical")
w_col3.metric("Silver Assets", f"{st.session_state.user_assets['Silver']:.2f} Tical")
