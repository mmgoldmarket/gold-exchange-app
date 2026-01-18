import streamlit as st
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
# ၂။ Javascript Injection (ခလုတ်အရောင်)
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

# Admin ပို့လိုက်သော စာများကို သိမ်းမည့်နေရာ (Chat Box အတွက်)
if 'user_messages' not in st.session_state:
    st.session_state.user_messages = []

# ==========================================
# ၄။ တွက်ချက်ရေး Function များ
# ==========================================
def get_market_price(symbol):
    td = TDClient(apikey=API_KEY)
    try:
        res = td.price(symbol=symbol).as_json()
        if 'price' in res:
            return float(res['price'])
        else:
            return 2650.50 if "XAU" in symbol else 90.119
    except:
        return 2650.50 if "XAU" in symbol else 90.119

def calculate_mmk(usd_price):
    base_mmk = (usd_price * CONVERSION_FACTOR) * st.session_state.usd_rate
    return int(base_mmk)

def fmt_price(mmk_value):
    return f"{mmk_value/100000:,.2f}"

# ==========================================
# ၅။ Website UI
# ==========================================

# --- SIDEBAR (Admin Panel) ---
with st.sidebar:
    st.header("🔧 Admin Control")
    if st.button("🔄 Refresh Market Data"):
        st.rerun()

    st.write("---")
    st.write("Exchange Rate Setting")
    new_rate = st.number_input("Western Union Rate (MMK)", value=st.session_state.usd_rate)
    if st.button("Update Rate"):
        st.session_state.usd_rate = new_rate
        st.success("Rate Updated!")

    st.divider()
    st.subheader("💰 Deposit Requests")
    
    # Pending List ကို ဆွဲထုတ်ခြင်း
    pending_list = [d for d in st.session_state.deposit_requests if d['status'] == "Pending"]
    
    if not pending_list:
        st.info("No pending requests.")
    else:
        for req in pending_list:
            # Request တစ်ခုချင်းစီကို Expander (အကွက်) လေးနဲ့ပြမယ်
            with st.expander(f"{req['user']} : {req['amount']:,} Ks"):
                
                # ၁. Admin စာပြန်ရန်အကွက် (Chat Reply)
                admin_msg = st.text_input("Send Bank Account Info:", key=f"msg_{req['id']}", placeholder="e.g. KBZPay 09xxxxxx")
                
                if st.button("Send Message", key=f"send_{req['id']}"):
                    if admin_msg:
                        # User Chat Box ထဲသို့ စာထည့်ပေးလိုက်ခြင်း
                        st.session_state.user_messages.append({
                            "user": req['user'],
                            "text": admin_msg,
                            "time": time.strftime("%I:%M %p")
                        })
                        st.success(f"Message sent to {req['user']}!")
                
                st.write("---")
                
                # ၂. ငွေဝင်တာသေချာမှ Approve နှိပ်ရန်
                if st.button("✅ Approve Deposit", key=f"app_{req['id']}"):
                    req['status'] = "Approved"
                    st.session_state.user_balance += req['amount']
                    st.success(f"Approved {req['amount']:,} Ks")
                    time.sleep(1)
                    st.rerun()

# --- MAIN PAGE (User View) ---
st.title("🏆 Myanmar Gold & Silver Exchange")

# --- USER CHAT / NOTIFICATION BOX ---
# Admin ဆီက စာရောက်နေရင် ဒီမှာပြမယ်
if st.session_state.user_messages:
    with st.expander("📬 Messages from Admin", expanded=True):
        for msg in reversed(st.session_state.user_messages):
            st.info(f"**Admin ({msg['time']}):** {msg['text']}")

# --- Market Data ---
st.write(f"**Exchange Rate:** 1 USD = {st.session_state.usd_rate:,.0f} MMK")

gold_usd = get_market_price("XAU/USD")
silver_usd = get_market_price("XAG/USD")

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