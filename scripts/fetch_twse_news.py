import requests
import pandas as pd
from pathlib import Path

URL = "https://openapi.twse.com.tw/v1/news/newsList"

def main():
    r = requests.get(URL, headers={"Accept": "application/json"}, timeout=30)
    print("status:", r.status_code)
    r.raise_for_status()

    data = r.json()
    df = pd.DataFrame(data)

    print("df.shape:", df.shape)
    print("df.columns:", df.columns.tolist())
    print(df.head(5))

    Path("data/raw").mkdir(parents=True, exist_ok=True)
    df.to_csv("data/raw/twse_news_list.csv", index=False, encoding="utf-8-sig")
    print("\nSaved -> data/raw/twse_news_list.csv")

if __name__ == "__main__":
    main()