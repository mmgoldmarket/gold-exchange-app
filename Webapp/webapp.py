import streamlit as st
import streamlit.components.v1 as components
import time
from twelvedata import TDClient

# ==========================================
# ၁။ Setting
# ==========================================
API_KEY = "b005ad2097b843d59d9c44ddfd3f9038" # Free Key (Rate Limit 8 calls/min)
CONVERSION_FACTOR = 16.329 / 31.1034768
GOLD_SPREAD = 5000
SILVER_SPREAD = 1000

st.set_page_config(page_title="Gold Exchange Admin", layout="wide")

# ==========================================
# ၂။ Session State & Database
# ==========================================import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import time
from twelvedata import TDClient

# ==========================================
# ၁။ Setting (Configuration)
# ==========================================
API_KEY = "b005ad2097b843d59d9c44ddfd3f9038"
CONVERSION_FACTOR = 16.329 / 31.1034768
GOLD_SPREAD = 5000
SILVER_SPREAD = 1000

st.set_page_config(page_title="Gold Exchange Admin", layout="wide")

# ==========================================
# ၂။ Javascript Injection (Button Colors)
# ==========================================
components.html("""
<script>
var interval = setInterval(function() {
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

# ==========================================
# ၃။ Database & Session State
# ==========================================
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
# ၄။ တွက်ချက်ရေး Function များ (API Fix)
# ==========================================

# NOTE: ၁၅ စက္ကန့် Cache ထားတဲ့အတွက် API Limit မကျော်ပါ
@st.cache_data(ttl=15)
def get_cached_prices():
    td = TDClient(apikey=API_KEY)
    # Default တန်ဖိုးများကို လက်ရှိဈေးအမှန်နှင့် နီးစပ်အောင် ပြင်ထားသည် (Error တက်လျှင် ဒီဈေးပြမည်)
    prices = {"XAU": 2650.00, "XAG": 31.50} 
    
    try:
        # Time Series မဟုတ်ဘဲ Price (Real-time) ကို တိုက်ရိုက်ခေါ်ပါမည်
        # Batch Request: Gold ရော Silver ပါ တစ်ခါတည်းခေါ်သည်
        res = td.price(symbol="XAU/USD,XAG/USD").as_json()
        
        # Result စစ်ဆေးခြင်း
        # Gold Parsing
        if 'XAU/USD' in res:
            prices["XAU"] = float(res['XAU/USD']['price'])
        
        # Silver Parsing
        if 'XAG/USD' in res:
            prices["XAG"] = float(res['XAG/USD']['price'])
            
    except Exception as e:
        print(f"API Error: {e}") # Console မှာ Error ပြခိုင်းသည်
        pass
        
    return prices

def calculate_mmk(usd_price):
    base_mmk = (usd_price * CONVERSION_FACTOR) * st.session_state.usd_rate
    return int(base_mmk)

def fmt_price(mmk_value):
    return f"{mmk_value/100000:,.2f}"

# ==========================================
# ၅။ Website UI
# ==========================================

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔧 Admin Control")
    
    # Auto Refresh Checkbox
    auto_refresh = st.checkbox("🔄 Auto Refresh Market (Every 15s)", value=True)

    if st.button("Manual Refresh"):
        st.cache_data.clear() 
        st.rerun()

    st.write("---")
    st.write("Exchange Rate Setting")
    new_rate = st.number_input("Western Union Rate (MMK)", value=st.session_state.usd_rate)
    if st.button("Update Rate"):
        st.session_state.usd_rate = new_rate
        st.success("Rate Updated!")

    st.divider()
    st.subheader("💰 Deposit Requests")
    
    pending_list = [d for d in st.session_state.deposit_requests if d['status'] == "Pending"]
    if not pending_list:
        st.info("No pending requests.")
    else:
        for req in pending_list:
            with st.expander(f"{req['user']} : {req['amount']:,} Ks"):
                admin_msg = st.text_input("Send Bank Account Info:", key=f"msg_{req['id']}", placeholder="e.g. KBZPay 09xxxxxx")
                if st.button("Send Message", key=f"send_{req['id']}"):
                    if admin_msg:
                        st.session_state.user_messages.append({
                            "user": req['user'],
                            "text": admin_msg,
                            "time": time.strftime("%I:%M %p")
                        })
                        st.success(f"Message sent!")
                
                st.write("---")
                if st.button("✅ Approve Deposit", key=f"app_{req['id']}"):
                    req['status'] = "Approved"
                    st.session_state.user_balance += req['amount']
                    st.success(f"Approved!")
                    time.sleep(1)
                    st.rerun()

# --- MAIN PAGE ---
st.title("🏆 Myanmar Gold & Silver Exchange")

if st.session_state.user_messages:
    with st.expander("📬 Messages from Admin", expanded=True):
        for msg in reversed(st.session_state.user_messages):
            st.info(f"**Admin ({msg['time']}):** {msg['text']}")

# --- FETCH PRICES ---
market_data = get_cached_prices()
gold_usd = market_data["XAU"]
silver_usd = market_data["XAG"]

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
        if st.button(f"Buy Gold\n{fmt_price(buy_price)}", key="buy_gold"):
            if st.session_state.user_balance >= buy_price:
                st.session_state.user_balance -= buy_price
                st.session_state.user_assets["Gold"] += 1.0
                st.session_state.transaction_history.append(f"Bought Gold @ {fmt_price(buy_price)}")
                st.success("Success!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Insufficient Funds!")
    with s_col:
        if st.button(f"Sell Gold\n{fmt_price(sell_price)}", key="sell_gold"):
            if st.session_state.user_assets["Gold"] >= 1.0:
                st.session_state.user_balance += sell_price
                st.session_state.user_assets["Gold"] -= 1.0
                st.session_state.transaction_history.append(f"Sold Gold @ {fmt_price(sell_price)}")
                st.success("Sold!")
                time.sleep(1)
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
        if st.button(f"Buy Silver\n{fmt_price(buy_price_s)}", key="buy_silver"):
            if st.session_state.user_balance >= buy_price_s:
                st.session_state.user_balance -= buy_price_s
                st.session_state.user_assets["Silver"] += 1.0
                st.session_state.transaction_history.append(f"Bought Silver @ {fmt_price(buy_price_s)}")
                st.success("Success!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Insufficient Funds!")
    with s_col_s:
        if st.button(f"Sell Silver\n{fmt_price(sell_price_s)}", key="sell_silver"):
            if st.session_state.user_assets["Silver"] >= 1.0:
                st.session_state.user_balance += sell_price_s
                st.session_state.user_assets["Silver"] -= 1.0
                st.session_state.transaction_history.append(f"Sold Silver @ {fmt_price(sell_price_s)}")
                st.success("Sold!")
                time.sleep(1)
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

with st.expander("View Recent Transactions"):
    if st.session_state.transaction_history:
        for txn in reversed(st.session_state.transaction_history):
            st.write(f"- {txn}")
    else:
        st.write("No transactions yet.")

# --- AUTO REFRESH LOGIC ---
if auto_refresh:
    time.sleep(15) 
    st.rerun()
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

# ==========================================
# ၃။ Price Fetching Function (Error ရှာရန် ပြင်ဆင်ထားသည်)
# ==========================================
@st.cache_data(ttl=20) # 20 စက္ကန့် Cache ထားမယ် (API Limit မကျော်အောင်)
def get_real_prices():
    td = TDClient(apikey=API_KEY)
    prices = {"XAU": None, "XAG": None, "error": None}
    
    try:
        # API ကို လှမ်းခေါ်မည် (Real-time Price)
        res = td.price(symbol="XAU/USD,XAG/USD").as_json()
        
        # ရွှေဈေး ယူမည်
        if 'XAU/USD' in res and 'price' in res['XAU/USD']:
            prices["XAU"] = float(res['XAU/USD']['price'])
        elif 'price' in res and 'XAU' in str(res): # တစ်ခါတလေ Structure ပြောင်းတတ်လို့
             prices["XAU"] = float(res['price'])

        # ငွေဈေး ယူမည်
        if 'XAG/USD' in res and 'price' in res['XAG/USD']:
            prices["XAG"] = float(res['XAG/USD']['price'])
            
        # API က Error Message ပြန်ပို့လာရင် မှတ်ထားမည်
        if 'code' in res and res['code'] != 200:
            prices['error'] = res.get('message', 'Unknown API Error')
            
    except Exception as e:
        prices['error'] = str(e)
        
    return prices

def calculate_mmk(usd_price):
    if usd_price is None: return 0
    return int((usd_price * CONVERSION_FACTOR) * st.session_state.usd_rate)

def fmt_price(mmk_value):
    return f"{mmk_value/100000:,.2f}"

# ==========================================
# ၄။ Website UI
# ==========================================

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔧 Admin Control")
    
    # Refresh ခလုတ် (အလုပ်လုပ်နေကြောင်းသိသာအောင် Spinner ထည့်သည်)
    if st.button("🔄 Force Refresh Data"):
        st.cache_data.clear()
        st.rerun()
        
    # Auto Refresh Checkbox
    auto_refresh = st.checkbox("Running Auto Refresh (20s)", value=True)

    st.divider()
    
    # DEBUG SECTION (ဒါက အရေးကြီးပါတယ် - API ဘာဖြစ်နေလဲ ကြည့်ဖို့)
    with st.expander("🛠 API Debugger (Check Here)"):
        st.write("API Key Status Checking...")
        # ဒီနေရာမှာ API Response အစစ်ကို ပြပေးပါမယ်

    st.write("---")
    st.write("Exchange Rate Setting")
    new_rate = st.number_input("Western Union Rate", value=st.session_state.usd_rate)
    if st.button("Update Rate"):
        st.session_state.usd_rate = new_rate
        st.success("Updated!")

# --- MAIN PAGE ---
st.title("🏆 Myanmar Gold & Silver Exchange")

# ဈေးနှုန်းများ ဆွဲယူခြင်း
data = get_real_prices()

# Error ရှိရင် အနီရောင်နဲ့ စာတန်းထိုးပြမယ် (ဒါမှ သိရမှာပါ)
if data['error']:
    st.error(f"⚠️ API Error: {data['error']}")
    st.warning("API Limit ပြည့်သွားတာ ဖြစ်နိုင်ပါတယ်။ 1 မိနစ်လောက်စောင့်ပြီး Refresh ပြန်နှိပ်ကြည့်ပါ။")
    # ယာယီ Fallback ဈေးပြထားမယ် (ဒါပေမဲ့ Error တက်မှန်းသိအောင်)
    gold_usd = 2650.00
    silver_usd = 31.50
else:
    gold_usd = data['XAU'] if data['XAU'] else 2650.00
    silver_usd = data['XAG'] if data['XAG'] else 31.50

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
    st.metric("World Price", f"${silver_usd:,.3f}") # Real price or 31.50 fallback
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

# ==========================================
# ၅။ Javascript Auto Refresh (More Stable)
# ==========================================
# Python sleep အစား Javascript နဲ့ Refresh လုပ်ခိုင်းမယ့် ကုဒ်
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

