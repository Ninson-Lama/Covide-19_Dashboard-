import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="COVID-19 Interactive Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌍 COVID-19 Interactive Dashboard")
st.markdown("Built with **Streamlit**, **Pandas**, and **Plotly** using OWID data.")

# -------------------------------
# Load Data
# -------------------------------
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
    df = pd.read_csv(url)
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# -------------------------------
# Filter Setup
# -------------------------------
non_countries = [
    "World", "Asia", "Europe", "Africa", "North America", "South America", "Oceania",
    "European Union", "International", "High income", "Upper middle income", "Lower middle income", "Low income"
]

country_df = df[~df["location"].isin(non_countries)]
all_countries = sorted(country_df["location"].unique())

# Sidebar
st.sidebar.header("⚙️ Filters")
selected_countries = st.sidebar.multiselect(
    "Select Countries",
    all_countries,
    default=["United Kingdom"]  # ✅ UK pre-selected
)

start_date = st.sidebar.date_input("Start Date", df["date"].min())
end_date = st.sidebar.date_input("End Date", df["date"].max())

mask = (df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))
filtered_df = df[mask & df["location"].isin(selected_countries)]

# -------------------------------
# Key Metrics
# -------------------------------
st.header("📊 Key Metrics for Selected Countries")
if not filtered_df.empty:
    total_cases = filtered_df["new_cases"].sum()
    total_deaths = filtered_df["new_deaths"].sum()

    vacc_col = "people_fully_vaccinated_per_hundred"
    latest_vaccination_rate = filtered_df.groupby("location")[vacc_col].last().mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cases", f"{total_cases:,.0f}")
    col2.metric("Total Deaths", f"{total_deaths:,.0f}")
    col3.metric("Avg. Full Vaccination Rate (%)",
                f"{latest_vaccination_rate:,.2f}%" if pd.notna(latest_vaccination_rate) else "N/A")
else:
    st.warning("No data available for the selected countries and date range.")

st.divider()

# -------------------------------
# Interactive Chart Selection
# -------------------------------
st.header("📈 Visualizations")
chart_selection = st.selectbox(
    "Choose a chart to display:",
    [
        "Daily New Cases",
        "Global Vaccination Coverage",
        "Vaccination Rates vs. Mortality Rates",
        "Top 10 Countries by Total Deaths"
    ]
)

# -------------------------------
# Charts
# -------------------------------
if chart_selection == "Daily New Cases":
    st.subheader("📉 Daily New Cases")
    if not filtered_df.empty:
        fig = px.line(
            filtered_df,
            x="date", y="new_cases", color="location",
            title="Daily New Cases Over Time",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for the selected countries and date range.")

elif chart_selection == "Global Vaccination Coverage":
    st.subheader("🌐 Global Vaccination Coverage")

    # ✅ Forward fill vaccination data
    vacc_df = country_df.sort_values(["location", "date"])
    vacc_df = vacc_df.groupby("location", as_index=False).apply(lambda g: g.ffill()).reset_index(drop=True)

    # Get latest available row for each country
    latest_data = vacc_df.loc[vacc_df.groupby("location")["date"].idxmax()]
    latest_data = latest_data.dropna(subset=["people_fully_vaccinated_per_hundred", "iso_code"])

    fig = px.choropleth(
        latest_data,
        locations="iso_code",
        color="people_fully_vaccinated_per_hundred",
        hover_name="location",
        color_continuous_scale="Viridis",
        title="Global Vaccination Coverage (Latest Available Data)"
    )

    # Highlight selected countries
    if selected_countries:
        highlight_points = latest_data[latest_data["location"].isin(selected_countries)]
        fig.add_scattergeo(
            locations=highlight_points["iso_code"],
            text=highlight_points["location"],
            mode="markers+text",
            marker=dict(size=10, color="red", symbol="circle"),
            textposition="top center",
            name="Selected Countries"
        )

    st.plotly_chart(fig, use_container_width=True)


elif chart_selection == "Vaccination Rates vs. Mortality Rates":
    st.subheader("💉 Vaccination Rates vs. Mortality Rates")

    # Prepare time-series data
    scatter_df = df[df["location"].isin(selected_countries)].copy()
    scatter_df = scatter_df.sort_values(["location", "date"])
    scatter_df = scatter_df.groupby("location", as_index=False).apply(lambda g: g.ffill()).reset_index(drop=True)

    # Latest snapshot for scatter plot
    latest_data_scatter = scatter_df.loc[scatter_df.groupby("location")["date"].idxmax()]
    latest_data_scatter = latest_data_scatter.dropna(
        subset=["people_fully_vaccinated_per_hundred", "total_deaths_per_million"]
    )

    # Chart type toggle
    view_option = st.radio(
        "Select view:",
        ["📍 Scatter Snapshot (Latest Available Data)", "📈 Trend Over Time"],
        horizontal=True
    )

    if view_option == "📍 Scatter Snapshot (Latest Available Data)":
        if not latest_data_scatter.empty:
            fig = px.scatter(
                latest_data_scatter,
                x="people_fully_vaccinated_per_hundred",
                y="total_deaths_per_million",
                hover_name="location",
                color="location",
                size="population",
                template="plotly_white",
                title="Vaccination Rates vs. Mortality Rates (Latest Available Data)"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No vaccination/mortality data available for the selected countries.")

    elif view_option == "📈 Trend Over Time":
        if not scatter_df.empty:
            fig = px.line(
                scatter_df,
                x="date",
                y="total_deaths_per_million",
                color="location",
                line_dash="location",
                title="Mortality Rate Over Time",
                template="plotly_white"
            )

            # Add vaccination % as secondary axis
            for country in selected_countries:
                country_data = scatter_df[scatter_df["location"] == country]
                fig.add_scatter(
                    x=country_data["date"],
                    y=country_data["people_fully_vaccinated_per_hundred"],
                    mode="lines",
                    name=f"{country} Vaccination (%)",
                    yaxis="y2"
                )

            # Configure secondary y-axis
            fig.update_layout(
                yaxis=dict(title="Deaths per Million"),
                yaxis2=dict(title="Vaccination Rate (%)", overlaying="y", side="right"),
                legend_title="Country"
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No trend data available for the selected countries.")


elif chart_selection == "Top 10 Countries by Total Deaths":
    st.subheader("⚰️ Top 10 Countries by Total Deaths")
    latest_country_data = country_df.loc[country_df.groupby("location")["date"].idxmax()]
    top_10_deaths = latest_country_data.nlargest(10, "total_deaths").sort_values("total_deaths", ascending=False)

    fig = px.bar(
        top_10_deaths,
        x="location", y="total_deaths",
        title="Top 10 Countries by Total Deaths",
        labels={"location": "Country", "total_deaths": "Total Deaths"},
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown("Data Source: [Our World in Data (OWID)](https://covid.ourworldindata.org/data/owid-covid-data.csv)")
st.markdown("Dashboard created by: Ninson Lama")
