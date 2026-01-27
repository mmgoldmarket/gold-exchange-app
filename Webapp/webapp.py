import streamlit as st
import streamlit.components.v1 as components
import requests
import time

# ==========================================
# 👑 VIP LOGO DATA (Base64 Encoded Image)
# ==========================================
VIP_LOGO_DATA = """
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAMAAAD04JH5AAAAh1BMVEUAAAD////6+vr4+Pj29vbz8/Px8fHv7+/t7e3r6+vq6urn5+fk5OTi4uLg4ODe3t7c3Nza2trX19fV1dXT09PR0dHPz8/Nzc3Lysetra2mpqaZmZmVlZWRkZGJiYmDg4N/f396enp3d3d0dHRxcXFtbW1ra2tmZmZkZGRcXFxaWlpYWFg8m912AAAKGElEQVR4nO1bWW/jNhg2Eh8Sc7ct0t4HjY9x0mY6tE3T7c0C7X/FdyS4kETZkjO20/k+BE4A6fCRryhKov71L7zhDfZB6f3/8E8Q6v32eX3+9tD76x/+CIH+/uf99v35UeG397fXz18f/gAB/f36/v1R2d1//7x+ev7+h1/eR19v39/e9+T8+/3Xn78/Yj99ff/2qOzX50c8P490fL39+vVd1d3/fN7fP3/Efn79/qj4132E8/m8/yT+5/P99y/f46v99+77m5q7/3nfF3v8r66eX6Xk/Gf97jT99U/385r81+frP2L/fL29v/9QhP/z9RHPb99vP2k/V1d/fT4/+l/t83X///7t9fn66P3v356e/4z/UfL9e6zXn3/E0/P3f8S+v359/+uXv96/qfPrL7Hvz98eOf71r/dYv/8aTf3z898/+8/3X5+3j1b6eH3Efn7+U2yXn56/P6r583X/F4n1lXyU8uv19l9+UfPz+pP2f/8V1/T5+vv7o+L7T1pff9I+v6n87fvrV/8W/l9/v9/eH31Vfr7ff33982+g//z3H/91P7n//Pv9j399vj/+9fv9t6enP6/j1/d/1H5++6v6+2+v6tf//tN3P+v1z3/+UeHf3571/b/f/xH/X0X5/k3j39c/n5+fn3/+rVqvv1T9338f4f71l5/W316ft9/7x32E+3H/+b/3b6/7z5/5/fN+q0a/P/+s2v8aTf/+EefvP//X5yfv/nZ/e3Tf99tP4+tW9X//Ecvz89/fnp//Efv5+Y/P5+fnp+fnPz8fnS3//mftxP/5/9f/y4V+hO+nZ+2s6vP7b1X87/2394fvftbf3p6/f0/7eH97299fH/H8/Pz1d/j7t2+v22+Vf/42uubnt/e3b69q/P8r4Nvn2+cfP6l9f/tJ+3xU+Hn/pum3z/f3X4V/fv2X3//1T+Pz7fX99dGf163Kz0dPv7+8P/q7sT9ff6v2j1r9t56en5+q7f5Z0++3Z20/z/o++n7/qPb921/fP9K7V/X/F9rP99tHjX96evr66Pm7//74/i+i/6v414+Q/lHt67t++5E5P3J/fv/7s6Lff/787/f9v30fP7973b//I8r3n3++vr5+a/2I/u9f9f2j6re/qn4V9bfa5//c+ffbT9r3Z9Ue2d1fP+v8j/j79V/P+9+q/lHtW3X//P63z5+ft8+f375U/f+J/Z8XyZ+v//r+/r+w0UftP4//b/X78+/P2t+2+9uvPz8ftd7+/Pv/4/3911/q/5H380e0bz/L/Pbt6f/v34/8HjE/39/f//X5/ffH91/q/2r1M+/3j9/q+K/f9P42+vbr79vX2l9u/9v77fvP/L/I/D/7+9//6jw26O3Hyn8/u8P0c//ef/2P8q/32k+6vj7b71eH53vj//+8eP++Hl6fHq+f3x+/v74+fnHl+/Xp6fnH58/frx+fn5+vP8Y37/xI7bfXj89Pz8/P9+P2n98vP74+Pj5+fl5v9/3+4/7jx9Pz88/n7/Pz8+P3H7k/j0//uT/+Pzz8/Hz45X5UfGP+y/vnz+fX9+fn58/79c/nx+df9b8rOnr8+c37+fL397vd/d9+e35/u9f8fb6s/yv15+f/nK/e91/xN96/fjx8fH6/Pz8/Pz48fHj9frj4+P19eP1+fn56/X56/nx4+PH89PTj9ffH6/X89eXj9fPr49v//jx/Hx/f//L9fM3l5fXX19+/fXX19fvL28v315erh9fv/34+H65f/m+fH+5f//2+uv7y8u359dv3/d/+XG9/+fH649/v7//9v3ly8v7H/+///2fD8e13Ww0E0Th7uH60ZpYIq6o55L//2d6A02R4l5nQ/S8k+XkLKe78691gHnQW7/G68N633t/sA7Q3v5vG/A2rI/eH6x1eX+01vneX92v7tfeD2v92h9Y19u9dZDWB72/934/aN/f652Dtd5bB87/v6631gG897f11jow6177/Wv9H4/8l8f/+Vd3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3d3f394L7l35/9L4/WAfo/Qc/H563T539AgAAAABJRU5ErkJggg=="""

# ==========================================
# ၁။ Setting & Configuration
# ==========================================
API_KEY = "b005ad2097b843d59d9c44ddfd3f9038"  # ✅ API Key ထည့်ထားပြီးပါပြီ

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
if 'future_positions' not in st.session_state:
    st.session_state.future_positions = []  

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
    # ⚠️ (1) API Call per Refresh only
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
    # ပုံဖိုင်မလိုဘဲ ကုဒ်ထဲက Data ကို တိုက်ရိုက်ပြပါမည်
    st.image(VIP_LOGO_DATA, width=85)

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

    main_tab1, main_tab2 = st.tabs(["Store (Spot Market)", "Trading (Future Market)"])

    # TAB 1: SPOT MARKET
    with main_tab1:
        st.subheader("📦 Spot Market")
        c1, c2 = st.columns(2)
        
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

    # TAB 2: FUTURE MARKET
    with main_tab2:
        st.subheader("📈 Future Market")
        fc1, fc2 = st.columns(2)
        
        with fc1:
            st.markdown(f"### 🟡 Gold Future")
            future_buy_g = gold_mmk + GOLD_SPREAD  
            future_sell_g = gold_mmk - GOLD_SPREAD 
            st.metric(label="World Price", value=f"${gold_usd:,.2f}") 
            st.caption(f"Base Price: {fmt_price(gold_mmk)} Lakhs")
            
            if st.button(f"LONG (Buy)\n{fmt_price(future_buy_g)}", key="f_long_g", use_container_width=True):
                st.session_state.future_positions.append({
                    "type": "Long", "symbol": "Gold", "entry": future_buy_g, "size": 1
                })
                st.success("Opened Long Position")
            if st.button(f"SHORT (Sell)\n{fmt_price(future_sell_g)}", key="f_short_g", use_container_width=True):
                st.session_state.future_positions.append({
                    "type": "Short", "symbol": "Gold", "entry": future_sell_g, "size": 1
                })
                st.success("Opened Short Position")

        with fc2:
            st.markdown(f"### ⚪ Silver Future")
            future_buy_s = silver_mmk + SILVER_SPREAD
            future_sell_s = silver_mmk - SILVER_SPREAD
            st.metric(label="World Price", value=f"${silver_usd:,.2f}") 
            st.caption(f"Base Price: {fmt_price(silver_mmk)} Lakhs")
            
            if st.button(f"LONG (Buy)\n{fmt_price(future_buy_s)}", key="f_long_s", use_container_width=True):
                st.session_state.future_positions.append({
                    "type": "Long", "symbol": "Silver", "entry": future_buy_s, "size": 1
                })
                st.success("Opened Long Position")
            if st.button(f"SHORT (Sell)\n{fmt_price(future_sell_s)}", key="f_short_s", use_container_width=True):
                st.session_state.future_positions.append({
                    "type": "Short", "symbol": "Silver", "entry": future_sell_s, "size": 1
                })
                st.success("Opened Short Position")
        
        st.divider()
        st.write("🔴 **Open Positions**")
        if st.session_state.future_positions:
            for i, pos in enumerate(st.session_state.future_positions):
                if pos['symbol'] == "Gold":
                    current_base = gold_mmk
                    market_spread = GOLD_SPREAD
                else:
                    current_base = silver_mmk
                    market_spread = SILVER_SPREAD
                
                exit_price_long = current_base - market_spread
                exit_price_short = current_base + market_spread
                
                if pos['type'] == "Long":
                    pnl = exit_price_long - pos['entry']
                else:
                    pnl = pos['entry'] - exit_price_short
                
                c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
                c1.write(f"**{pos['symbol']} {pos['type']}**")
                c2.write(f"Entry: {fmt_price(pos['entry'])}")
                pnl_color = "green" if pnl >= 0 else "red"
                c3.markdown(f"P/L: :{pnl_color}[{pnl:,.0f} Ks]")
                if c4.button("Close", key=f"close_{i}"):
                    st.session_state.user_balance += pnl
                    st.session_state.future_positions.pop(i)
                    st.rerun()
        else:
            st.info("No Open Positions")

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
