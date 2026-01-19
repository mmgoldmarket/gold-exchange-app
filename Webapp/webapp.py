import streamlit as st
import streamlit.components.v1 as components
import requests
import time

# ==========================================
# ၁။ Setting (Configuration)
# ==========================================
# ⚠️ သတိပြုရန်: Plan ဝယ်ထားသော အကောင့်မှ API Key အစစ်ကို ဒီနေရာမှာ ထည့်ပေးပါ
API_KEY = "b005ad2097b843d59d9c44ddfd3f9038"  

CONVERSION_FACTOR = 16.329 / 31.1034768
GOLD_SPREAD = 5000
SILVER_SPREAD = 1000

st.set_page_config(page_title="Gold Exchange Admin", layout="wide")

# ==========================================
# ၂။ Session State Initialization (Memory)
# ==========================================
# ဈေးနှုန်းများကို Memory ထဲမှာ အရင်မှတ်ထားပါမယ် (Error တက်ရင် ဒါကိုပြန်သုံးမယ်)
if 'last_gold_price' not in st.session_state:
    st.session_state.last_gold_price = 2650.00
if 'last_silver_price' not in st.session_state:
    st.session_state.last_silver_price = 31.50
if 'price_status' not in st.session_state:
    st.session_state.price_status = "Init"

# Database Variables
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
# ၃။ Price Fetching Logic (Pro Version)
# ==========================================
def fetch_realtime_prices():
    # Paid Plan ဖြစ်လို့ Batch Request နဲ့ ၅ စက္ကန့်တစ်ခါ ခေါ်မယ်
    url = f"https://api.twelvedata.com/price?symbol=XAU/USD,XAG/USD&apikey={API_KEY}"
    
    try:
        response = requests.get(url, timeout=5) # 5 seconds timeout
        data = response.json()
        
        # Error Checking
        if "code" in data and data["code"] != 200:
             # API Error တက်ရင် ဘာမှမလုပ်ဘဲ Pass (Memory ထဲကဈေးကိုပဲ ဆက်သုံးမယ်)
             st.session_state.price_status = "Offline (API Error)"
        else:
            # Success - Update Memory
            if "XAU/USD" in data:
                st.session_state.last_gold_price = float(data["XAU/USD"]["price"])
            if "XAG/USD" in data:
                st.session_state.last_silver_price = float(data["XAG/USD"]["price"])
            
            st.session_state.price_status = "Live 🟢"
                
    except Exception as e:
        # Internet Error တက်ရင်လည်း Pass (Memory ထဲကဈေးကိုပဲ ဆက်သုံးမယ်)
        st.session_state.price_status = "Offline (Net Error)"
        pass

def calculate_mmk(usd_price):
    return int((usd_price * CONVERSION_FACTOR) * st.session_state.usd_rate)

def fmt_price(mmk_value):
    return f"{mmk_value/100000:,.2f}"

# ==========================================
# ၄။ Website UI
# ==========================================

# --- Fetch Data (Run this every refresh) ---
fetch_realtime_prices()

# Get Prices from Session State (Safe Mode)
gold_usd = st.session_state.last_gold_price
silver_usd = st.session_state.last_silver_price

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔧 Admin Control")
    
    # Status Indicator
    status_color = "green" if "Live" in st.session_state.price_status else "red"
    st.markdown(f"Status: :{status_color}[{st.session_state.price_status}]")
    
    if st.button("Manual Refresh"):
        st.rerun()

    # 5 Seconds Refresh Logic Checkbox
    auto_refresh = st.checkbox("⚡ Real-time (5s)", value=True)

    st.divider()
    st.write("Exchange Rate Setting")
    new_rate = st.number_input("Western Union Rate (MMK)", value=st.session_state.usd_rate)
    if st.button("Update Rate"):
        st.session_state.usd_rate = new_rate
        st.success("Rate Updated!")

    # Deposit Requests Section...
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

# --- MAIN PAGE ---
st.title("🏆 Myanmar Gold & Silver Exchange")

if st.session_state.user_messages:
    with st.expander("📬 Messages from Admin", expanded=True):
        for msg in reversed(st.session_state.user_messages):
            st.info(f"**Admin ({msg['time']}):** {msg['text']}")

st.write(f"**Exchange Rate:** 1 USD = {st.session_state.usd_rate:,.0f} MMK")

gold_mmk = calculate_mmk(gold_usd)
silver_mmk = calculate_mmk(silver_usd)

col1, col2 = st.columns(2)

# --- GOLD SECTION ---
with col1:
    st.subheader("🟡 Gold (ရွှေ)")
    st.metric(label="World Price", value=f"${gold_usd:,.2f}")
    st.info(f"**Base Price:** {fmt_price(gold_mmk)} (Spread မပါ)")
    
    buy_price = gold_mmk + GOLD_SPREAD
    sell_price = gold_mmk - GOLD_SPREAD
    
    b_col, s_col = st.columns(2)
    with b_col:
        if st.button(f"Buy Gold\n{fmt_price(buy_price)}", key="buy_gold", use_container_width=True):
            if st.session_state.user_balance >= buy_price:
                st.session_state.user_balance -= buy_price
                st.session_state.user_assets["Gold"] += 1.0
                st.session_state.transaction_history.append(f"Bought Gold @ {fmt_price(buy_price)}")
                st.success("Success!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Insufficient Funds!")
    with s_col:
        if st.button(f"Sell Gold\n{fmt_price(sell_price)}", key="sell_gold", use_container_width=True):
            if st.session_state.user_assets["Gold"] >= 1.0:
                st.session_state.user_balance += sell_price
                st.session_state.user_assets["Gold"] -= 1.0
                st.session_state.transaction_history.append(f"Sold Gold @ {fmt_price(sell_price)}")
                st.success("Sold!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("No Gold to Sell!")

# --- SILVER SECTION ---
with col2:
    st.subheader("⚪ Silver (ငွေ)")
    st.metric(label="World Price", value=f"${silver_usd:,.3f}")
    st.info(f"**Base Price:** {fmt_price(silver_mmk)} (Spread မပါ)")
    
    buy_price_s = silver_mmk + SILVER_SPREAD
    sell_price_s = silver_mmk - SILVER_SPREAD
    
    b_col_s, s_col_s = st.columns(2)
    with b_col_s:
        if st.button(f"Buy Silver\n{fmt_price(buy_price_s)}", key="buy_silver", use_container_width=True):
            if st.session_state.user_balance >= buy_price_s:
                st.session_state.user_balance -= buy_price_s
                st.session_state.user_assets["Silver"] += 1.0
                st.session_state.transaction_history.append(f"Bought Silver @ {fmt_price(buy_price_s)}")
                st.success("Success!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Insufficient Funds!")
    with s_col_s:
        if st.button(f"Sell Silver\n{fmt_price(sell_price_s)}", key="sell_silver", use_container_width=True):
            if st.session_state.user_assets["Silver"] >= 1.0:
                st.session_state.user_balance += sell_price_s
                st.session_state.user_assets["Silver"] -= 1.0
                st.session_state.transaction_history.append(f"Sold Silver @ {fmt_price(sell_price_s)}")
                st.success("Sold!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("No Silver to Sell!")

st.divider()

# --- USER WALLET DISPLAY ---
st.subheader("👤 My Wallet")
w_col1, w_col2, w_col3 = st.columns(3)
w_col1.metric("Cash Balance", f"{st.session_state.user_balance:,.0f} Ks")
w_col2.metric("Gold Assets", f"{st.session_state.user_assets['Gold']:.2f} Tical")
w_col3.metric("Silver Assets", f"{st.session_state.user_assets['Silver']:.2f} Tical")

# --- JAVASCRIPT AUTO REFRESH (5 SECONDS) ---
if auto_refresh:
    components.html(
        f"""
            <script>
                var timeLeft = 5;
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
