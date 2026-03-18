import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="Simulateur P/E Réel", layout="wide")

st.title("📊 Simulateur P/E avec données réelles (yfinance)")

# ======================
# INPUT TICKER
# ======================

ticker = st.text_input("Entrer un ticker (ex: NOW, MSFT, NVDA)", value="NOW")

# ======================
# DATA FETCH (ROBUSTE)
# ======================

@st.cache_data(ttl=3600)
def get_data(ticker):
    for attempt in range(3):
        try:
            stock = yf.Ticker(ticker)

            # ✅ Prix (rapide et fiable)
            price = stock.fast_info.get("lastPrice", None)

            # ⚠️ EPS (peut bug)
            eps = None
            try:
                eps = stock.info.get("trailingEps", None)
            except:
                eps = None

            # 🔁 Fallback EPS via financials
            if eps is None:
                try:
                    earnings = stock.financials
                    if not earnings.empty:
                        net_income = earnings.loc["Net Income"].iloc[0]
                        shares = stock.fast_info.get("shares", None)
                        if shares:
                            eps = net_income / shares
                except:
                    eps = None

            # ✅ Calcul P/E
            pe = None
            if price and eps and eps != 0:
                pe = price / eps

            return price, eps, pe

        except Exception:
            time.sleep(2)

    return None, None, None


price, eps, pe = get_data(ticker)

# ======================
# FALLBACK MANUEL
# ======================

st.subheader("📌 Données actuelles")

col1, col2, col3 = st.columns(3)

if price:
    col1.metric("Prix", f"{price:.2f}")
else:
    price = col1.number_input("Prix manuel", value=100.0)

if eps:
    col2.metric("EPS", f"{eps:.2f}")
else:
    eps = col2.number_input("EPS manuel", value=2.0)

if pe:
    col3.metric("P/E", f"{pe:.2f}")
else:
    pe = price / eps
    col3.metric("P/E (estimé)", f"{pe:.2f}")

# ======================
# SIMULATION INPUTS
# ======================

st.subheader("⚙️ Hypothèses de simulation")

col1, col2 = st.columns(2)

with col1:
    growth_price = st.slider("Croissance du prix (%)", 0, 30, 10) / 100
    years = st.slider("Nombre d'années", 1, 10, 5)

with col2:
    growth_eps = st.slider("Croissance EPS (%)", 0, 50, 25) / 100

# ======================
# SIMULATION
# ======================

prices = [price]
eps_list = [eps]
pe_list = [price / eps]

for i in range(1, years + 1):
    new_price = prices[-1] * (1 + growth_price)
    new_eps = eps_list[-1] * (1 + growth_eps)

    prices.append(new_price)
    eps_list.append(new_eps)
    pe_list.append(new_price / new_eps)

df = pd.DataFrame({
    "Année": list(range(years + 1)),
    "Prix": prices,
    "EPS": eps_list,
    "P/E": pe_list
})

# ======================
# TABLEAU
# ======================

st.subheader("📋 Projection")

st.dataframe(df.style.format({
    "Prix": "{:.2f}",
    "EPS": "{:.2f}",
    "P/E": "{:.2f}"
}))

# ======================
# GRAPHIQUE
# ======================

st.subheader("📈 Évolution")

fig, ax = plt.subplots()

ax.plot(df["Année"], df["Prix"], label="Prix")
ax.plot(df["Année"], df["EPS"], label="EPS")
ax.plot(df["Année"], df["P/E"], label="P/E")

ax.legend()
ax.set_xlabel("Années")

st.pyplot(fig)

# ======================
# INTERPRÉTATION
# ======================

st.subheader("🧠 Interprétation")

if growth_eps > growth_price:
    st.success("➡️ Le P/E diminue : croissance saine")
elif growth_eps == growth_price:
    st.warning("➡️ Le P/E reste stable")
else:
    st.error("➡️ Le P/E augmente : risque de surévaluation")

# ======================
# CONCLUSION AUTO
# ======================

final_pe = pe_list[-1]

st.subheader("🎯 Lecture finale")

if final_pe < 30:
    st.success("💡 Le stock devient raisonnable avec la croissance")
elif final_pe < 50:
    st.warning("⚖️ Le stock reste premium")
else:
    st.error("⚠️ Le stock reste cher même après croissance")
