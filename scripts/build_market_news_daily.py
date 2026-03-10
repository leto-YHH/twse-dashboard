import re
from pathlib import Path

import pandas as pd

def roc_to_ad(roc_yyyymmdd: str) -> str:
    s = str(roc_yyyymmdd).strip()
    roc_year = int(s[:3])
    month = int(s[3:5])
    day = int(s[5:7])
    ad_year = roc_year + 1911
    return f"{ad_year:04d}-{month:02d}-{day:02d}"

# 很簡單的規則式情緒（第一版先能跑）
POS_WORDS = ["中大獎", "獲獎", "創新高", "大大上漲", "成長", "增加", "優於", "突破", "擴大", "利多"]
NEG_WORDS = ["大下跌", "跌幅", "衰退", "虧損", "下滑", "減少", "風險", "警示", "違約", "裁員", "利空"]

def rule_sentiment(text: str, n_items: int = 1) -> float:
    if not isinstance(text, str) or not text.strip():
        return 0.0
    score = 0
    for w in POS_WORDS:
        score += text.count(w)
    for w in NEG_WORDS:
        score -= text.count(w)

    # 用新聞篇數做縮放，避免太極端
    denom = max(2, n_items)  # 至少 2，避免一篇就爆表
    val = score / denom

    # 壓到 -1~+1
    return float(max(-1.0, min(1.0, val)))

def sign(x: float, eps: float = 1e-9) -> int:
    if x is None or pd.isna(x):
        return 0
    if x > eps:
        return 1
    if x < -eps:
        return -1
    return 0

def main():
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    Path("data/raw").mkdir(parents=True, exist_ok=True)

    # 讀新聞（你已經有 raw 檔就用 raw 檔；沒有就請你先存成 data/raw/twse_news_list.csv）
    news_path = Path("data/raw/twse_news_list.csv")
    if not news_path.exists():
        raise FileNotFoundError("找不到 data/raw/twse_news_list.csv，請先執行 scripts/fetch_twse_news.py")
    
    news = pd.read_csv(news_path, encoding="utf-8-sig")
    # 欄位：Title, Url, Date
    news["date"] = news["Date"].apply(roc_to_ad)
    news["date"] = pd.to_datetime(news["date"], format="%Y-%m-%d")

    # 每日彙總：篇數 + 串接標題（給情緒）
    daily = (
        news.groupby("date", as_index=False)
            .agg(
                news_count=("Title", "count"),
                news_titles=("Title", lambda s: "；".join(map(str, s))),
            )
    )
    #分數計算
    daily["news_sent_score"] = daily.apply(lambda row: rule_sentiment(row["news_titles"], row["news_count"]), axis=1)

    daily.to_csv("data/processed/twse_news_daily.csv", index=False, encoding="utf-8-sig")
    print("Saved -> data/processed/twse_news_daily.csv")

    # 讀大盤加權指數
    mi = pd.read_csv("data/processed/mi_index_weighted.csv", encoding="utf-8-sig", parse_dates=["date"])

    # 合併
    merged = pd.merge(mi, daily, on="date", how="left")
    merged["news_count"] = merged["news_count"].fillna(0).astype(int)
    merged["news_sent_score"] = merged["news_sent_score"].fillna(0.0)

    # 背離：市場方向 vs 新聞情緒方向
    merged["news_dir"] = merged["news_sent_score"].apply(sign)
    merged["div_dir"] = merged["market_dir"] * merged["news_dir"]  # +1一致 / -1背離 / 0不判斷

    merged.to_csv("data/processed/market_news_daily.csv", index=False, encoding="utf-8-sig")
    print("Saved -> data/processed/market_news_daily.csv")

    print("\nPreview:")
    print(merged.tail(5)[["date","index_change_pct","market_dir","news_count","news_sent_score","news_dir","div_dir"]])

if __name__ == "__main__":
    main()