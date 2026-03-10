import pandas as pd
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="TWSE Market + News Dashboard", layout="wide")
st.title("TWSE 大盤 + 證交所新聞情緒（站內資料）")

DATA_PATH = "data/processed/market_news_daily.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig", parse_dates=["date"])
    df = df.sort_values("date")
    return df

df = load_data()

if df.empty:
    st.error("找不到資料或資料為空：data/processed/market_news_daily.csv")
    st.stop()

# ===== 日期下拉選單 =====
date_options = df["date"].dt.strftime("%Y-%m-%d").tolist()
default_idx = len(date_options) - 1  # 預設最新一天

selected_date_str = st.selectbox("選擇交易日", options=date_options, index=default_idx)

# 取出該日資料列
selected_date = pd.to_datetime(selected_date_str)
row = df.loc[df["date"] == selected_date]
if row.empty:
    st.error(f"找不到該日期資料：{selected_date_str}")
    st.stop()

latest = row.iloc[0]

# ===== 指標卡片 =====
col1, col2, col3, col4 = st.columns(4)
col1.metric("日期", latest["date"].strftime("%Y-%m-%d"))
col2.metric("大盤漲跌幅(%)", f"{float(latest['index_change_pct']):.2f}")
col3.metric("新聞則數", int(latest["news_count"]))
col4.metric("新聞情緒分數", f"{float(latest['news_sent_score']):.2f}")

def div_label(x: int) -> str:
    return {1: "一致 (+1)", -1: "背離 (-1)", 0: "不判斷 (0)"}.get(int(x), "不判斷 (0)")

st.write(f"**背離判斷：** {div_label(latest.get('div_dir', 0))}")

st.divider()

# ===== 今日新聞 =====
st.subheader("當日新聞標題（TWSE）")
titles = str(latest.get("news_titles", "")).split("；")
titles = [t.strip() for t in titles if t.strip()]

if titles:
    for i, t in enumerate(titles, 1):
        st.write(f"{i}. {t}")
else:
    st.write("（無）")
#++++
st.divider()

# ===== 當日報告 =====
st.subheader("當日分析報告（reports）")
report_path = Path("reports") / f"{latest['date'].strftime('%Y-%m-%d')}.md"
if report_path.exists():
    st.markdown(report_path.read_text(encoding="utf-8"))
else:
    st.info(f"找不到該日報告：{report_path}（可先執行 python generate_daily_report.py 產生）")

st.divider()

# ===== 趨勢圖（可選：以你選的日期為中心）=====
st.subheader("近 N 日走勢（到選定日期為止）")

if len(df) < 2:
    st.info("目前資料筆數不足（少於 2 天），暫時無法顯示趨勢圖。")
else:
    max_n = min(120, len(df))
    n = st.slider("顯示天數", min_value=2, max_value=max_n, value=min(30, max_n), step=1)

    # 只取到選定日期為止，再取最後 n 筆
    df_upto = df[df["date"] <= selected_date]
    view = df_upto.tail(n).set_index("date")

    st.line_chart(view[["index_change_pct"]])
    st.line_chart(view[["news_sent_score"]])

st.subheader("資料表（到選定日期為止，最近 30 筆）")
table_df = df[df["date"] <= selected_date].tail(min(30, len(df)))
st.dataframe(table_df, width="stretch")