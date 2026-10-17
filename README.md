# 🌍 Gapminder Dashboard

An interactive Streamlit dashboard exploring life expectancy, population and GDP per person for 142 countries from 1952 to 2007.

## Features
- **Filters:** pick a year and one or more continents in the sidebar, and every card and chart updates together
- **KPI cards:** average life expectancy, total population, average GDP per person and country count, with change vs. 5 years earlier
- **Richest vs. longest-living:** top 10 countries by GDP and by life expectancy side by side, with countries in both lists highlighted
- **Does more money mean a longer life?** scatter plot of GDP per person vs. life expectancy on a log scale, with the correlation coefficient
- **Trend:** average life expectancy by continent over time, with the selected year marked
- **World map:** countries shaded by life expectancy, with a marker showing each country's income group; the map zooms to the selected continents

The scatter plot and the world map use the same visual language:

| Visual | Meaning |
|---|---|
| ▼ ● ▲ | Income group by GDP per person: Low (under \$3k), Middle (\$3k–15k), High (\$15k+) |
| Light → dark blue | Shorter → longer life expectancy, on the same scale for every year |

## Data
The [Gapminder](https://www.gapminder.org/) dataset bundled with Plotly (`plotly.express.data.gapminder()`): 142 countries, measured every 5 years from 1952 to 2007. GDP per person is in inflation-adjusted dollars.

## Built with
Python · Streamlit · pandas · Plotly

## Run it locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
