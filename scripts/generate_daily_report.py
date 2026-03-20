from pathlib import Path
import pandas as pd

def div_label(x: int) -> str:
    if x == 1:
        return "一致"
    if x == -1:
        return "背離"
    return "不判斷"

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate markdown daily market reports")
    parser.add_argument("--start", type=str, default=None, help="起始日期（YYYY-MM-DD），預設為最早日期")
    parser.add_argument("--end", type=str, default=None, help="結束日期（YYYY-MM-DD），預設為最新日期")
    parser.add_argument("--top", type=int, default=5, help="每日顯示新聞標題上限，預設5")
    args = parser.parse_args()

    df = pd.read_csv("data/processed/market_news_daily.csv", encoding="utf-8-sig", parse_dates=["date"])
    df = df.sort_values("date")

    if args.start:
        start_date = pd.to_datetime(args.start)
    else:
        start_date = df["date"].min()

    if args.end:
        end_date = pd.to_datetime(args.end)
    else:
        end_date = df["date"].max()

    selected = df[(df["date"] >= start_date) & (df["date"] <= end_date)].copy()

    out_dir = Path("reports")
    out_dir.mkdir(parents=True, exist_ok=True)

    for _, row in selected.iterrows():
        date_str = row["date"].strftime("%Y-%m-%d")
        idx_pct = float(row["index_change_pct"])
        idx_close = float(row["index_close"])
        news_count = int(row["news_count"])
        sent = float(row["news_sent_score"])
        div = int(row.get("div_dir", 0))

        titles = str(row.get("news_titles", "")).split("；")
        titles = [t.strip() for t in titles if t.strip()]
        titles = titles[: args.top]

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
            if len(titles) < news_count:
                lines.append(f"-（已顯示 {len(titles)} 則，實際新聞數 {news_count}）")
        else:
            lines.append("- （無）")

        out_path = out_dir / f"{date_str}.md"
        out_path.write_text("\n".join(lines), encoding="utf-8")
        print("Saved ->", out_path)

if __name__ == "__main__":
    main()