# 🌍 Gapminder Dashboard

An interactive Streamlit dashboard exploring life expectancy, population and GDP per person for 142 countries from 1952 to 2007, using the Gapminder dataset bundled with Plotly.

## Features
- **Filters:** pick a year and one or more continents in the sidebar
- **KPI cards:** average life expectancy, total population, average GDP per person and country count, with change vs. 5 years earlier
- **Richest vs. longest-living:** top 10 countries by GDP and by life expectancy side by side, with countries in both lists highlighted
- **Correlation:** scatter plot of GDP per person vs. life expectancy, with the correlation coefficient
- **Trend:** average life expectancy by continent over time
- **World map:** income group shown by marker shape and shade, life expectancy by marker size

## Run it locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
