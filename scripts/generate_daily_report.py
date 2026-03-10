from pathlib import Path
import pandas as pd

def div_label(x: int) -> str:
    if x == 1:
        return "一致"
    if x == -1:
        return "背離"
    return "不判斷"

def main():
    df = pd.read_csv("data/processed/market_news_daily.csv", encoding="utf-8-sig", parse_dates=["date"])
    df = df.sort_values("date")
    latest = df.iloc[-1]

    date_str = latest["date"].strftime("%Y-%m-%d")
    idx_pct = float(latest["index_change_pct"])
    idx_close = float(latest["index_close"])
    news_count = int(latest["news_count"])
    sent = float(latest["news_sent_score"])
    div = int(latest.get("div_dir", 0))

    titles = str(latest.get("news_titles", "")).split("；")
    titles = [t.strip() for t in titles if t.strip()]

    lines = []
    lines.append(f"# 每日市場摘要（{date_str}）\n")
    lines.append("## 1) 大盤概況")
    lines.append(f"- 加權指數收盤：{idx_close:,.2f}")
    lines.append(f"- 漲跌幅：{idx_pct:.2f}%")
    lines.append("")
    lines.append("## 2) 證交所新聞概況")
    lines.append(f"- 新聞則數：{news_count}")
    lines.append(f"- 新聞情緒分數（規則法）：{sent:.2f}（-1~+1）")
    lines.append("")
    lines.append("## 3) 背離判斷")
    lines.append(f"- 市場行為 vs 新聞敘事：**{div_label(div)}**（div_dir={div}）")
    lines.append("")
    lines.append("## 4) 今日新聞標題")

    if titles:
        for i, t in enumerate(titles, 1):
            lines.append(f"{i}. {t}")
    else:
        lines.append("- （無）")

    out_dir = Path("reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{date_str}.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")

    print("Saved ->", out_path)

if __name__ == "__main__":
    main()