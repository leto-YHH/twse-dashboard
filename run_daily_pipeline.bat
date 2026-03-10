@echo off
cd /d %~dp0

call .venv\Scripts\activate.bat

python scripts\fetch_twse_news.py
python scripts\fetch_mi_index.py
python scripts\clean_mi_index.py
python scripts\build_market_news_daily.py
python scripts\generate_daily_report.py

echo Done.
pause