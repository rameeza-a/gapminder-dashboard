import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# Page settings — must be the first Streamlit command
st.set_page_config(page_title="Gapminder Dashboard", page_icon="🌍", layout="wide")

# One fixed color per continent, so a continent looks the same in every chart
CONTINENT_COLORS = {
    "Africa": "#2a78d6",
    "Americas": "#eb6834",
    "Asia": "#1baf7a",
    "Europe": "#eda100",
    "Oceania": "#e87ba4",
}
HIGHLIGHT = "#2a78d6"  # blue for the thing we want you to notice
MUTED = "#a3a29b"  # gray for everything else


# @st.cache_data loads the data once and reuses it,
# instead of reloading every time you click something
@st.cache_data
def load_data():
    df = px.data.gapminder()
    return df.drop(columns=["iso_num"])


df = load_data()

st.title("🌍 Gapminder Dashboard")
st.caption("Life expectancy, population and GDP per person for 142 countries, 1952–2007")

# ---------- Sidebar filters ----------
# Anything inside "with st.sidebar:" goes in the panel on the left
with st.sidebar:
    st.header("Filters")
    year = st.slider(
        "Year",
        min_value=int(df["year"].min()),
        max_value=int(df["year"].max()),
        value=int(df["year"].max()),
        step=5,  # data is every 5 years
    )
    all_continents = sorted(df["continent"].unique())
    continents = st.multiselect("Continents", all_continents, default=all_continents)

# Stop early if nothing is selected, instead of drawing empty charts
if not continents:
    st.warning("Pick at least one continent in the sidebar.")
    st.stop()

# Every card and chart below uses these filtered tables
filtered = df[df["continent"].isin(continents)]
now = filtered[filtered["year"] == year]
before = filtered[filtered["year"] == year - 5]
has_before = not before.empty  # the first year (1952) has nothing to compare with

# ---------- KPI cards ----------
st.subheader(f"Key numbers for {year}")
k1, k2, k3, k4 = st.columns(4)
k1.metric(
    "Avg life expectancy",
    f"{now['lifeExp'].mean():.1f} yrs",
    f"{now['lifeExp'].mean() - before['lifeExp'].mean():+.1f} yrs vs {year - 5}" if has_before else None,
    help="Simple average across countries",
)
pop = now["pop"].sum()
k2.metric(
    "Total population",
    f"{pop / 1e9:.2f} billion" if pop >= 1e9 else f"{pop / 1e6:.1f} million",
    f"{(now['pop'].sum() - before['pop'].sum()) / 1e6:+,.0f} million vs {year - 5}" if has_before else None,
)
k3.metric(
    "Avg GDP per person",
    f"${now['gdpPercap'].mean():,.0f}",
    f"{now['gdpPercap'].mean() / before['gdpPercap'].mean() - 1:+.1%} vs {year - 5}" if has_before else None,
    help="Simple average across countries, in inflation-adjusted US$",
)
k4.metric("Countries", now["country"].nunique())

st.divider()

# ---------- Top 10 comparison ----------
top_gdp = now.nlargest(10, "gdpPercap")
top_life = now.nlargest(10, "lifeExp")
in_both = set(top_gdp["country"]) & set(top_life["country"])

st.subheader(f"Richest vs. longest-living countries, {year}")
st.caption(f"Blue = in both top 10 lists ({len(in_both)} of {len(top_gdp)} countries). Hover a bar to see the other measure.")

LABELS = {"gdpPercap": "GDP per person (US$)", "lifeExp": "Life expectancy (years)", "country": "", "group": ""}


# We draw the same kind of chart twice, so we put it in a function
def top10_chart(data, column):
    data = data.copy()
    data["group"] = np.where(data["country"].isin(in_both), "In both lists", "Only in this list")
    fig = px.bar(
        data,
        x=column,
        y="country",
        orientation="h",
        color="group",
        color_discrete_map={"In both lists": HIGHLIGHT, "Only in this list": MUTED},
        hover_data={"gdpPercap": ":,.0f", "lifeExp": ":.1f", "group": False},
        labels=LABELS,
    )
    fig.update_yaxes(categoryorder="total ascending")  # biggest bar on top
    return fig


left, right = st.columns(2)
with left:
    st.markdown("**Top 10 by GDP per person**")
    st.plotly_chart(top10_chart(top_gdp, "gdpPercap"))
with right:
    st.markdown("**Top 10 by life expectancy**")
    st.plotly_chart(top10_chart(top_life, "lifeExp"))

st.divider()

# ---------- Correlation + trend ----------
left, right = st.columns(2)

with left:
    st.subheader(f"Does more money mean a longer life? ({year})")
    # A correlation from just a handful of countries is meaningless, so we need at least 10
    if len(now) >= 10:
        r = np.log10(now["gdpPercap"]).corr(now["lifeExp"])
        st.caption(
            f"Each dot is a country. Correlation r = {r:.2f} (1 = perfect link, 0 = no link). "
            "The GDP axis is logarithmic: each step is 10× richer."
        )
    else:
        st.caption(f"Only {len(now)} countries selected — too few to measure a correlation.")
    fig = px.scatter(
        now,
        x="gdpPercap",
        y="lifeExp",
        log_x=True,
        hover_name="country",
        hover_data={"continent": True, "gdpPercap": ":,.0f", "lifeExp": ":.1f"},
        labels=LABELS,
    )
    fig.update_traces(marker=dict(size=9, color=HIGHLIGHT, opacity=0.7))
    st.plotly_chart(fig)

with right:
    st.subheader("Life expectancy over time")
    trend = filtered.groupby(["year", "continent"], as_index=False)["lifeExp"].mean()
    fig = px.line(
        trend,
        x="year",
        y="lifeExp",
        color="continent",
        color_discrete_map=CONTINENT_COLORS,
        markers=True,
        labels={"year": "Year", "lifeExp": "Avg life expectancy (years)", "continent": "Continent"},
    )
    fig.update_layout(hovermode="x unified")
    fig.add_vline(x=year, line_width=1, line_color=MUTED)  # marks the year picked in the sidebar
    st.plotly_chart(fig)

st.divider()

# ---------- World map ----------
st.subheader(f"World map, {year}")
st.caption(
    "Shape and shade = income group (GDP per person: Low under \\$3k · Middle \\$3k–15k · High \\$15k+). "
    "Bigger marker = longer life expectancy."
)

# pd.cut sorts each country into a group based on which range its GDP falls in
GDP_GROUPS = ["Low", "Middle", "High"]
map_data = now.copy()
map_data["gdp_group"] = pd.cut(
    map_data["gdpPercap"], bins=[0, 3000, 15000, np.inf], labels=GDP_GROUPS, right=False
).astype(str)

fig = px.scatter_geo(
    map_data,
    locations="iso_alpha",  # 3-letter country codes tell Plotly where each country is
    symbol="gdp_group",
    color="gdp_group",
    size="lifeExp",
    symbol_map={"Low": "triangle-down", "Middle": "circle", "High": "triangle-up"},
    color_discrete_map={"Low": "#86b6ef", "Middle": "#2a78d6", "High": "#104281"},
    category_orders={"gdp_group": GDP_GROUPS},
    hover_name="country",
    hover_data={"gdpPercap": ":,.0f", "lifeExp": ":.1f", "iso_alpha": False},
    labels={**LABELS, "gdp_group": "Income group"},
    projection="natural earth",
    size_max=14,
)
fig.update_layout(height=550, margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(fig)

# ---------- Raw data ----------
with st.expander("Show raw data"):
    st.dataframe(filtered, hide_index=True)
