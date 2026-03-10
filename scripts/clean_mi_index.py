import requests
import pandas as pd
from pathlib import Path

URL = "https://openapi.twse.com.tw/v1/exchangeReport/MI_INDEX"

def roc_to_ad(roc_yyyymmdd: str) -> str:
    """
    1150306 -> 2026-03-06 (民國年轉西元)
    """
    s = str(roc_yyyymmdd).strip()
    roc_year = int(s[:3])
    month = int(s[3:5])
    day = int(s[5:7])
    ad_year = roc_year + 1911
    return f"{ad_year:04d}-{month:02d}-{day:02d}"

def fetch_weighted_index() -> pd.DataFrame:
    r = requests.get(URL, headers={"Accept": "application/json"}, timeout=30)
    r.raise_for_status()
    df = pd.DataFrame(r.json())

    w = df[df["指數"].astype(str).str.contains("發行量加權股價指數", na=False)].copy()
    if w.empty:
        raise ValueError("找不到『發行量加權股價指數』列")

    w = w[["日期", "收盤指數", "漲跌", "漲跌點數", "漲跌百分比", "特殊處理註記"]].copy()

    w["date"] = pd.to_datetime(w["日期"].apply(roc_to_ad), format="%Y-%m-%d")

    for col in ["收盤指數", "漲跌點數", "漲跌百分比"]:
        w[col] = pd.to_numeric(w[col], errors="coerce")

    w["market_dir"] = w["漲跌"].map({"+": 1, "-": -1}).fillna(0).astype(int)

    w = w.rename(
        columns={
            "收盤指數": "index_close",
            "漲跌點數": "index_change",
            "漲跌百分比": "index_change_pct",
            "特殊處理註記": "note",
        }
    )

    w = w[["date", "index_close", "index_change", "index_change_pct", "market_dir", "note"]].sort_values("date")
    return w

def main():
    w = fetch_weighted_index()
    print(w.tail(5))

    # ✅ 確保資料夾存在
    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / "mi_index_weighted.csv"
    w.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\nSaved -> {out_path}")

if __name__ == "__main__":
    main()