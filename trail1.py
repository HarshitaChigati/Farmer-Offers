import streamlit as st
import pandas as pd
import math

# ------------------ CONFIG ------------------
st.set_page_config(page_title="CultivaTec Farmer Offer App", layout="wide")

# ------------------ RAW URLs ------------------
logo_url = "https://raw.githubusercontent.com/HarshitaChigati/Farmer-Offers/e556477ff605f501a2c044f675978bf29375060d/cultivatec%202-Photoroom%20(3).png"
excel_url = "https://raw.githubusercontent.com/HarshitaChigati/Farmer-Offers/e556477ff605f501a2c044f675978bf29375060d/Farmer%20offer%20data.xlsx"

# ------------------ LOAD DATA ------------------
@st.cache_data
def load_data(url):
    return pd.read_excel(url)

df = load_data(excel_url)

# ------------------ PREMIUM STYLING ------------------
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f4fff8, #fffdf5);
        font-family: 'Segoe UI', sans-serif;
    }
    .header { text-align: center; margin-bottom: 20px; }
    .header h1 { color: #1a2b49; font-size: 34px; font-weight: 700; margin-bottom: 5px; }
    .header p { color: #444; font-size: 16px; margin-top: 0; }

    .card {
        background: white;
        padding: 20px;
        margin-bottom: 20px;
        border-radius: 14px;
        border-top: 6px solid #27ae60;
        box-shadow: 0 6px 14px rgba(0,0,0,0.08);
    }
    .card h3 { margin-top: 0; color: #1a2b49; font-weight: 600; }

    .eligible {
        background-color: #eafaf1;
        color: #0b6b2d;
        padding: 16px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 22px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .not-eligible {
        background-color: #fdecea;
        color: #a80000;
        padding: 16px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 22px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .summary-box {
        background: #fff9e6;
        border: 2px solid #f1c40f;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        font-weight: 600;
        margin: 5px 0;
        color: #1a2b49;
        font-size: 18px;
    }

    .suggestion-box {
        background: #eaf3fc;
        border-left: 6px solid #3498db;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
        color: #1a2b49;
        font-weight: 500;
    }

    div.stButton > button:first-child {
        background: #27ae60;
        color: white;
        border-radius: 8px;
        padding: 10px 28px;
        font-size: 16px;
        font-weight: 600;
        border: none;
        transition: 0.3s;
    }
    div.stButton > button:first-child:hover {
        background: #219150;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.markdown(f"""
<div class="header">
    <img src="{logo_url}" width="130">
    <h1>CultivaTec Farmer Offer App</h1>
    <p>Check eligibility, see farmer prices, and suggested free offers</p>
</div>
""", unsafe_allow_html=True)

# ------------------ HELPER ------------------
def _parse_pct(val):
    if pd.isna(val): return 0.0
    if isinstance(val, str):
        s = val.strip().replace('%','').strip()
        try: f = float(s)
        except: return 0.0
        return f/100 if f > 1 else f
    try: f = float(val)
    except: return 0.0
    return f/100 if f > 1 else f

def calculate_eligibility(purchased_list, free_list, df):
    total_purchased_profit = 0.0
    total_required_min_profit = 0.0
    total_free_cost = 0.0

    for p in purchased_list:
        row = df[(df["Product"]==p["Product"]) & (df["SKU"]==p["SKU"])]
        if row.empty: continue
        ct_profit = row["CT SKU Profit"].iloc[0]
        pct = _parse_pct(row["Min. Profit"].iloc[0])
        qty = p["Qty"]
        total_purchased_profit += ct_profit * qty
        total_required_min_profit += ct_profit * qty * pct

    for f in free_list:
        row = df[(df["Product"]==f["Product"]) & (df["SKU"]==f["SKU"])]
        if row.empty: continue
        ct_price = row["CT Purchase Price(with GST)"].iloc[0]
        total_free_cost += ct_price * f["Qty"]

    leftover_profit = total_purchased_profit - total_free_cost
    eligible = leftover_profit >= total_required_min_profit

    return eligible, leftover_profit, total_purchased_profit, total_required_min_profit

# ------------------ PURCHASED PRODUCTS ------------------
st.markdown("<div class='card'><h3>Purchased Products</h3>", unsafe_allow_html=True)
purchased_products = []
purchased_total_value = 0
for i in range(3):
    cols = st.columns([3,2,2,2])
    with cols[0]:
        prod = st.selectbox(f"Product {i+1}", [""]+df["Product"].unique().tolist(), key=f"p_prod_{i}")
    with cols[1]:
        sku = st.selectbox(f"SKU {i+1}", [""]+df[df["Product"]==prod]["SKU"].unique().tolist(), key=f"p_sku_{i}") if prod else ""
    with cols[2]:
        qty = st.number_input(f"Qty {i+1}", min_value=0, step=1, key=f"p_qty_{i}")
    price_val = 0
    if prod and sku and qty>0:
        row = df[(df["Product"]==prod) & (df["SKU"]==sku)].iloc[0]
        price_val = row["Farmer Price(with GST)"] * qty
        purchased_products.append({"Product": prod, "SKU": sku, "Qty": qty})
        purchased_total_value += price_val
    with cols[3]:
        st.write(f"₹{price_val:,.0f}")
st.markdown(f"<div class='summary-box'>Total Purchase Value: ₹{purchased_total_value:,.0f}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ------------------ FREE PRODUCTS ------------------
st.markdown("<div class='card'><h3>Free Products</h3>", unsafe_allow_html=True)
free_products = []
free_total_value = 0
for i in range(3):
    cols = st.columns([3,2,2,2])
    with cols[0]:
        prod = st.selectbox(f"Free Product {i+1}", [""]+df["Product"].unique().tolist(), key=f"f_prod_{i}")
    with cols[1]:
        sku = st.selectbox(f"Free SKU {i+1}", [""]+df[df["Product"]==prod]["SKU"].unique().tolist(), key=f"f_sku_{i}") if prod else ""
    with cols[2]:
        qty = st.number_input(f"Free Qty {i+1}", min_value=0, step=1, key=f"f_qty_{i}")
    price_val = 0
    if prod and sku and qty>0:
        row = df[(df["Product"]==prod) & (df["SKU"]==sku)].iloc[0]
        price_val = row["Farmer Price(with GST)"] * qty
        free_products.append({"Product": prod, "SKU": sku, "Qty": qty})
        free_total_value += price_val
    with cols[3]:
        st.write(f"₹{price_val:,.0f}")
st.markdown(f"<div class='summary-box'>Total Free Value: ₹{free_total_value:,.0f}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ------------------ BUTTON ------------------
cols = st.columns([1,1,1])
with cols[1]:
    submit = st.button("Check Eligibility")

# ------------------ RESULTS ------------------
if submit:
    eligible, leftover, tp, tr = calculate_eligibility(purchased_products, free_products, df)

    if eligible:
        st.markdown("<div class='eligible'>✅ Eligible for Free Products!</div>", unsafe_allow_html=True)
        st.balloons()
    else:
        st.markdown("<div class='not-eligible'>❌ Not Eligible</div>", unsafe_allow_html=True)

    # Suggestions
    st.markdown("<div class='card'><h3>Suggested Free Products</h3>", unsafe_allow_html=True)
    available_for_free = tp - tr
    if available_for_free > 0:
        for _, row in df.iterrows():
            if pd.isna(row["CT Purchase Price(with GST)"]): continue
            price = row["CT Purchase Price(with GST)"]
            max_qty = math.floor(available_for_free / price) if price>0 else 0
            if max_qty > 0:
                st.markdown(f"<div class='suggestion-box'>{row['Product']} ({row['SKU']}): {max_qty} units</div>", unsafe_allow_html=True)
    else:
        st.info("No free products suggested. Increase purchase quantity to unlock offers.")
    st.markdown("</div>", unsafe_allow_html=True)
