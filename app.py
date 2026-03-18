import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulateur P/E Réel", layout="wide")

st.title("📊 Simulateur P/E avec données réelles (yfinance)")

# ======================
# INPUT TICKER
# ======================

ticker = st.text_input("Entrer un ticker (ex: NOW, MSFT, NVDA)", value="NOW")

# ======================
# FETCH DATA
# ======================

@st.cache_data
def get_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info

    price = info.get("currentPrice", None)
    eps = info.get("trailingEps", None)
    pe = info.get("trailingPE", None)

    return price, eps, pe

price, eps, pe = get_data(ticker)

# ======================
# DISPLAY REAL DATA
# ======================

st.subheader("📌 Données actuelles")

col1, col2, col3 = st.columns(3)

col1.metric("Prix", f"{price:.2f}" if price else "N/A")
col2.metric("EPS", f"{eps:.2f}" if eps else "N/A")
col3.metric("P/E", f"{pe:.2f}" if pe else "N/A")

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

if price and eps:

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
    # TABLE
    # ======================

    st.subheader("📋 Projection")

    st.dataframe(df.style.format({
        "Prix": "{:.2f}",
        "EPS": "{:.2f}",
        "P/E": "{:.2f}"
    }))

    # ======================
    # GRAPH
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
    # INTERPRETATION
    # ======================

    st.subheader("🧠 Lecture")

    if growth_eps > growth_price:
        st.success("➡️ Le P/E diminue (croissance saine)")
    elif growth_eps == growth_price:
        st.warning("➡️ P/E stable")
    else:
        st.error("➡️ P/E augmente (danger)")

else:
    st.error("Impossible de récupérer les données du ticker.")
