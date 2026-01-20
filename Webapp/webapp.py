import streamlit as st
import streamlit.components.v1 as components
import requests
import time

# ==========================================
# ၁။ Setting & Configuration
# ==========================================
API_KEY = "b005ad2097b843d59d9c44ddfd3f9038"  # ⚠️ Paid Key ထည့်ရန်

# Weight: 16.329 Grams per Tical
CONVERSION_FACTOR = 16.329 / 31.1034768
GOLD_SPREAD = 5000
SILVER_SPREAD = 1000

# Sidebar ကို အမြဲတမ်း ဖွင့်ထားရန်
st.set_page_config(page_title="Gold Exchange System", layout="wide", initial_sidebar_state="expanded")

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

# Default Rate: 4000
if 'usd_rate' not in st.session_state:
    st.session_state.usd_rate = 4000.0 

if 'user_balance' not in st.session_state:
    st.session_state.user_balance = 0.0
if 'user_assets' not in st.session_state:
    st.session_state.user_assets = {"Gold": 0.0, "Silver": 0.0}
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
# ၄။ SIDEBAR (System Control)
# ==========================================
with st.sidebar:
    st.header("⚙️ System Control")
    
    # API Status
    status_color = "green" if "Live" in st.session_state.price_status else "red"
    st.markdown(f"API Status: :{status_color}[{st.session_state.price_status}]")
    
    if st.button("Refresh System"):
        st.rerun()

    st.divider()
    
    # Rate Control
    st.subheader("Currency Setting")
    new_rate = st.number_input("USD Exchange Rate", value=st.session_state.usd_rate)
    if st.button("Update Rate"):
        st.session_state.usd_rate = new_rate
        st.cache_data.clear()
        st.rerun()
        
    st.divider()
    
    # Simulated Deposit Requests (Test Area)
    st.subheader("💰 Deposit Requests (Test)")
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
st.title("🏗️ Gold & Silver Exchange (Builder Mode)")
st.write(f"**Current Rate:** 1 USD = {st.session_state.usd_rate:,.0f} MMK")

@st.fragment(run_every=3)
def show_market_section():
    fetch_realtime_prices()
    gold_usd = st.session_state.last_gold_price
    silver_usd = st.session_state.last_silver_price
    gold_mmk = calculate_mmk(gold_usd)
    silver_mmk = calculate_mmk(silver_usd)
    
    # Tabs ကို ဖျောက်ပြီး Header တပ်လိုက်သည်
    st.header("📊 Spot Market")
    
    col1, col2 = st.columns(2)
    # GOLD SECTION
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

    # SILVER SECTION
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

show_market_section()

st.divider()
st.subheader("👤 Wallet (Test View)")
w1, w2, w3 = st.columns(3)
w1.metric("Cash Balance", f"{st.session_state.user_balance:,.0f} Ks")
w2.metric("Gold Assets", f"{st.session_state.user_assets['Gold']:.2f} Tical")
w3.metric("Silver Assets", f"{st.session_state.user_assets['Silver']:.2f} Tical")

# Button Styling
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
