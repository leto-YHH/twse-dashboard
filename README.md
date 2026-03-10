# TWSE Market News Dashboard

使用 Python 擷取台灣證券交易所（TWSE）新聞與加權指數資料，
加上一點變化再上傳到github以及測試git
進行基本整理與分析，並透過 Streamlit 製作簡易 dashboard。

## 使用技術
- Python
- pandas
- requests
- Streamlit

## 執行方式
```bash
pip install -r requirements.txt
python scripts/fetch_twse_news.py
python scripts/fetch_mi_index.py
python scripts/clean_mi_index.py
python scripts/build_market_news_daily.py
python scripts/generate_daily_report.py
streamlit run app/app.py
```