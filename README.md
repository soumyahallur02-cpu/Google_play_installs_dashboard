# PlayMetrics — Google Play Store Install Trend Dashboard

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Features
- Refined Streamlit layout with custom CSS, sidebar, hero header, KPI cards and tables.
- Requested filters: Reviews > 500; app name does not contain S; app name does not start X/Y/Z; category starts E/C/B.
- Beauty displayed in Hindi, Business in Tamil, Dating in German (Dating remains excluded by the E/C/B filter).
- Plotly category time-series chart with orange shaded high-growth observations (>20% MoM).
- Chart shown only between 18:00 and 21:00 Asia/Kolkata time. Refresh/rerun the app at the boundary to update visibility.
- Category summary and growth-highlight tables.

## Data limitation
The supplied dataset contains one current Installs value per app and Last Updated date, not actual monthly install history. Monthly totals are grouped by Last Updated month and should be interpreted as a proxy trend.
