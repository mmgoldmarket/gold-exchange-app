import streamlit as st
import streamlit.components.v1 as components
import requests
import time

# ==========================================
# ၁။ Setting & Configuration
# ==========================================
API_KEY = "b005ad2097b843d59d9c44ddfd3f9038"  # ⚠️ Paid Key

# Conversion Factors
CONVERSION_FACTOR = 16.329 / 31.1034768
GOLD_SPREAD = 5000
SILVER_SPREAD = 1000

# Sidebar Config
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

# Default Rate
if 'usd_rate' not in st.session_state:
    st.session_state.usd_rate = 4000.0 

# Wallet & Positions
if 'user_balance' not in st.session_state:
    st.session_state.user_balance = 0.0
if 'spot_assets' not in st.session_state:
    st.session_state.spot_assets = {"Gold": 0.0, "Silver": 0.0}
if 'future_positions' not in st.session_state:
    st.session_state.future_positions = []  # Future အရောင်းအဝယ် စာရင်း

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
    new_rate = st.number_input("USD Rate", value=st.session_state.usd_rate)
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
st.title("🏗️ Gold & Silver Exchange")
st.write(f"**Current Rate:** 1 USD = {st.session_state.usd_rate:,.0f} MMK")

fetch_realtime_prices()
gold_usd = st.session_state.last_gold_price
silver_usd = st.session_state.last_silver_price
gold_mmk = calculate_mmk(gold_usd)
silver_mmk = calculate_mmk(silver_usd)

# 🟢 MAIN TABS (Spot vs Future)
main_tab1, main_tab2 = st.tabs(["Store (Spot Market)", "Trading (Future Market)"])

# ------------------------------------------
# TAB 1: SPOT MARKET (Physical Logic)
# ------------------------------------------
with main_tab1:
    st.subheader("📦 Spot Market (Physical Asset)")
    c1, c2 = st.columns(2)
    
    # Gold Spot
    with c1:
        st.info(f"**Gold Base:** {fmt_price(gold_mmk)} Lakhs")
        buy = gold_mmk + GOLD_SPREAD
        sell = gold_mmk - GOLD_SPREAD
        if st.button(f"Buy Gold\n{fmt_price(buy)}", key="s_bg", use_container_width=True):
            if st.session_state.user_balance >= buy:
                st.session_state.user_balance -= buy
                st.session_state.spot_assets["Gold"] += 1.0
                st.session_state.transaction_history.append(f"Spot: Bought Gold @ {fmt_price(buy)}")
                st.success("Bought!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Low Balance!")
        if st.button(f"Sell Gold\n{fmt_price(sell)}", key="s_sg", use_container_width=True):
            if st.session_state.spot_assets["Gold"] >= 1.0:
                st.session_state.user_balance += sell
                st.session_state.spot_assets["Gold"] -= 1.0
                st.session_state.transaction_history.append(f"Spot: Sold Gold @ {fmt_price(sell)}")
                st.success("Sold!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("No Gold!")

    # Silver Spot
    with c2:
        st.info(f"**Silver Base:** {fmt_price(silver_mmk)} Lakhs")
        buy_s = silver_mmk + SILVER_SPREAD
        sell_s = silver_mmk - SILVER_SPREAD
        if st.button(f"Buy Silver\n{fmt_price(buy_s)}", key="s_bs", use_container_width=True):
            if st.session_state.user_balance >= buy_s:
                st.session_state.user_balance -= buy_s
                st.session_state.spot_assets["Silver"] += 1.0
                st.session_state.transaction_history.append(f"Spot: Bought Silver @ {fmt_price(buy_s)}")
                st.success("Bought!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Low Balance!")
        if st.button(f"Sell Silver\n{fmt_price(sell_s)}", key="s_ss", use_container_width=True):
            if st.session_state.spot_assets["Silver"] >= 1.0:
                st.session_state.user_balance += sell_s
                st.session_state.spot_assets["Silver"] -= 1.0
                st.session_state.transaction_history.append(f"Spot: Sold Silver @ {fmt_price(sell_s)}")
                st.success("Sold!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("No Silver!")

# ------------------------------------------
# TAB 2: FUTURE MARKET (Trading Logic)
# ------------------------------------------
with main_tab2:
    st.subheader("📈 Future Market (Paper Trading)")
    st.caption("Trading on Price Difference (CFD Style) - No Physical Delivery")
    
    fc1, fc2 = st.columns(2)
    with fc1:
        st.markdown(f"### 🟡 Gold Future")
        st.metric("Market Price", f"{fmt_price(gold_mmk)}")
        # Future Logic: Buy/Sell creates a "Position"
        if st.button("Open LONG (Buy)", key="f_buy_g", use_container_width=True):
             st.session_state.future_positions.append({"type": "Long", "symbol": "Gold", "entry": gold_mmk, "size": 1})
             st.success("Opened Long Position")
             
        if st.button("Open SHORT (Sell)", key="f_sell_g", use_container_width=True):
             st.session_state.future_positions.append({"type": "Short", "symbol": "Gold", "entry": gold_mmk, "size": 1})
             st.success("Opened Short Position")

    with fc2:
        st.markdown(f"### ⚪ Silver Future")
        st.metric("Market Price", f"{fmt_price(silver_mmk)}")
        if st.button("Open LONG (Buy)", key="f_buy_s", use_container_width=True):
             st.session_state.future_positions.append({"type": "Long", "symbol": "Silver", "entry": silver_mmk, "size": 1})
             st.success("Opened Long Position")
             
        if st.button("Open SHORT (Sell)", key="f_sell_s", use_container_width=True):
             st.session_state.future_positions.append({"type": "Short", "symbol": "Silver", "entry": silver_mmk, "size": 1})
             st.success("Opened Short Position")
    
    st.divider()
    st.write("🔴 **Open Positions**")
    if st.session_state.future_positions:
        for i, pos in enumerate(st.session_state.future_positions):
            current_price = gold_mmk if pos['symbol'] == "Gold" else silver_mmk
            # P/L Logic
            if pos['type'] == "Long":
                pnl = current_price - pos['entry']
            else:
                pnl = pos['entry'] - current_price
            
            c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
            c1.write(f"{pos['symbol']} ({pos['type']})")
            c2.write(f"Entry: {fmt_price(pos['entry'])}")
            c3.write(f"P/L: {pnl:,.0f} Ks")
            if c4.button("Close", key=f"close_{i}"):
                st.session_state.user_balance += pnl
                st.session_state.future_positions.pop(i)
                st.rerun()
    else:
        st.info("No Open Positions")

# ==========================================
# ၆။ WALLET SUMMARY
# ==========================================
st.divider()
st.subheader("👤 My Wallet")
w1, w2, w3 = st.columns(3)
w1.metric("Cash Balance", f"{st.session_state.user_balance:,.0f} Ks")
w2.metric("Spot Gold", f"{st.session_state.spot_assets['Gold']:.2f} Tical")
w3.metric("Spot Silver", f"{st.session_state.spot_assets['Silver']:.2f} Tical")

# Button Coloring
components.html("""
<script>
    setInterval(function() {
        var buttons = window.parent.document.querySelectorAll('button');
        for (var i = 0; i < buttons.length; i++) {
            var text = buttons[i].innerText;
            if (text.includes("Buy") || text.includes("LONG")) {
                buttons[i].style.backgroundColor = "#28a745"; 
                buttons[i].style.color = "white";
                buttons[i].style.borderColor = "#28a745";
            }
            else if (text.includes("Sell") || text.includes("SHORT")) {
                buttons[i].style.backgroundColor = "#dc3545"; 
                buttons[i].style.color = "white";
                buttons[i].style.borderColor = "#dc3545";
            }
        }
    }, 500); 
</script>
""", height=0)
