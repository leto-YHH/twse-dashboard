import requests
import pandas as pd

URL = "https://openapi.twse.com.tw/v1/exchangeReport/MI_INDEX"

def fetch_mi_index() -> pd.DataFrame:
    r = requests.get(
        URL,
        headers={"Accept": "application/json"},
        timeout=30,
    )
    print("status:", r.status_code)
    r.raise_for_status()

    data = r.json()  # 通常是 list[dict]
    if not isinstance(data, list) or len(data) == 0:
        raise ValueError(f"Unexpected JSON shape: {type(data)}")

    df = pd.DataFrame(data)
    return df

def pick_weighted_index_row(df: pd.DataFrame) -> pd.DataFrame:
    # 常見欄位名是「指數」或類似名稱；先找包含「指數」的欄位
    idx_col_candidates = [c for c in df.columns if "指數" in c]
    if not idx_col_candidates:
        print("df.columns:", df.columns.tolist())
        raise KeyError("找不到包含「指數」字樣的欄位，請貼 df.columns 給我。")

    idx_col = idx_col_candidates[0]
    # 抓「發行量加權股價指數」那一列（加權指數）
    target = df[df[idx_col].astype(str).str.contains("發行量加權股價指數", na=False)]

    # 有些資料可能寫「發行量加權股價指數」或略有差異，fallback
    if target.empty:
        target = df[df[idx_col].astype(str).str.contains("加權", na=False)]

    return target

def main():
    df = fetch_mi_index()
    print("df.shape:", df.shape)
    print("df.columns:", df.columns.tolist())
    print(df.head(3))

    w = pick_weighted_index_row(df)
    print("\n=== weighted index row(s) ===")
    if w.empty:
        print("找不到加權指數列，請把 df.head(20) 貼給我。")
    else:
        print(w)

if __name__ == "__main__":
    main()