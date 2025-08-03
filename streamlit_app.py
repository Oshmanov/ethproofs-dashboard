import os, requests, pandas as pd, streamlit as st

API = "https://ethproofs.org/api/v0"
HEAD = {"Authorization": f"Bearer {os.getenv('ETHPROOFS_KEY')}"}

st.title("L1-Proving Profit Simulator")

# ── пользовательские ползунки ───────────────────────────────
price  = st.slider("Цена пруфа, $", 0.01, 1.00, 0.05, 0.01)
time_s = st.slider("Время пруфа, сек", 0.1, 30.0, 2.5, 0.1)
cost_h = st.slider("Цена инстанса, $/ч", 0.5, 5.0, 1.2, 0.1)
util   = st.slider("Загрузка, %", 10, 100, 70, 5)

# ── подтянуть реальные средние (опция) ─────────────────────
if st.checkbox("Использовать свежие данные Ethproofs"):
    try:
        proofs = requests.get(f"{API}/proofs?status=proved&limit=500",
                              headers=HEAD, timeout=10).json()
        df = pd.DataFrame(proofs)
        price  = round(df["cost_usd"].mean(), 4)
        time_s = round(df["proving_time"].mean() / 1000, 2)
        st.info(f"Средняя цена: ${price} | Среднее время: {time_s}s")
    except Exception as e:
        st.error(f"API error: {e}")

# ── расчёты ─────────────────────────────────────────────────
proofs_day = (86400 / time_s) * (util / 100)
income  = proofs_day * price
expense = cost_h * 24
profit  = income - expense

st.metric("Прибыль за сутки", f"${profit:,.2f}")

# ── прогноз на 12 месяцев ──────────────────────────────────
growth = st.slider("Рост цены пруфа в месяц, %", -20, 20, 0)
data = []
p = price
for m in range(12):
    d = proofs_day * p * 30
    e = expense * 30
    data.append({"Месяц": m+1, "Прибыль": d-e})
    p *= 1 + growth/100
st.bar_chart(pd.DataFrame(data).set_index("Месяц"))
