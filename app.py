import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import requests
from io import StringIO

# Page configuration
st.set_page_config(
    page_title="COVID-19 Dashboard",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_covid_data():
    """Load and merge COVID-19 data from OWID CSV files"""
    try:
        # Main COVID data
        main_data_url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
        locations_url = "https://covid.ourworldindata.org/data/owid-covid-codebook.csv"
        
        # Load main data
        response = requests.get(main_data_url)
        main_data = pd.read_csv(StringIO(response.text))
        
        # Convert date column
        main_data['date'] = pd.to_datetime(main_data['date'])
        
        # Filter out non-country entries (like 'World', continents)
        main_data = main_data[~main_data['iso_code'].isin(['OWID_WRL', 'OWID_AFR', 'OWID_ASI', 'OWID_EUR', 'OWID_NAM', 'OWID_OCE', 'OWID_SAM'])]
        main_data = main_data[main_data['iso_code'].notna()]
        
        return main_data
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def create_sidebar_filters(data):
    """Create sidebar filters for country and date range"""
    st.sidebar.header("🔍 Filters")
    
    # Country filter
    countries = sorted(data['location'].unique())
    selected_countries = st.sidebar.multiselect(
        "Select Countries",
        countries,
        default=['United States', 'United Kingdom', 'Germany', 'France', 'Italy'] if len(countries) > 0 else []
    )
    
    # Date range filter
    if len(data) > 0:
        min_date = data['date'].min().date()
        max_date = data['date'].max().date()
        
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Handle single date selection
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = end_date = date_range
    else:
        start_date = end_date = date.today()
        selected_countries = []
    
    return selected_countries, start_date, end_date

def filter_data(data, countries, start_date, end_date):
    """Filter data based on selected countries and date range"""
    if len(data) == 0:
        return data
    
    filtered_data = data.copy()
    
    # Filter by countries
    if countries:
        filtered_data = filtered_data[filtered_data['location'].isin(countries)]
    
    # Filter by date range
    filtered_data = filtered_data[
        (filtered_data['date'].dt.date >= start_date) & 
        (filtered_data['date'].dt.date <= end_date)
    ]
    
    return filtered_data

def display_key_metrics(data):
    """Display key metrics using st.metric"""
    if len(data) == 0:
        st.warning("No data available for the selected filters.")
        return
    
    # Get latest data for metrics
    latest_data = data.groupby('location').last().reset_index()
    
    # Calculate global totals
    total_cases = latest_data['total_cases'].sum()
    total_deaths = latest_data['total_deaths'].sum()
    total_vaccinations = latest_data['total_vaccinations'].sum()
    
    # Calculate daily changes (last 7 days average)
    recent_data = data[data['date'] >= data['date'].max() - pd.Timedelta(days=7)]
    daily_cases = recent_data.groupby('date')['new_cases'].sum().mean()
    daily_deaths = recent_data.groupby('date')['new_deaths'].sum().mean()
    
    # Display metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Cases",
            f"{total_cases:,.0f}" if pd.notna(total_cases) else "N/A"
        )
    
    with col2:
        st.metric(
            "Total Deaths",
            f"{total_deaths:,.0f}" if pd.notna(total_deaths) else "N/A"
        )
    
    with col3:
        st.metric(
            "Total Vaccinations",
            f"{total_vaccinations:,.0f}" if pd.notna(total_vaccinations) else "N/A"
        )
    
    with col4:
        st.metric(
            "Avg Daily Cases (7d)",
            f"{daily_cases:,.0f}" if pd.notna(daily_cases) else "N/A"
        )
    
    with col5:
        st.metric(
            "Avg Daily Deaths (7d)",
            f"{daily_deaths:,.0f}" if pd.notna(daily_deaths) else "N/A"
        )

def create_time_series_chart(data):
    """Create time-series line chart"""
    if len(data) == 0:
        st.warning("No data available for time series chart.")
        return
    
    # Create chart for new cases
    fig = px.line(
        data,
        x='date',
        y='new_cases_smoothed',
        color='location',
        title="COVID-19 New Cases Over Time (7-day smoothed)",
        labels={'new_cases_smoothed': 'New Cases (7-day average)', 'date': 'Date'}
    )
    
    fig.update_layout(
        height=500,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_choropleth_map(data):
    """Create global choropleth map"""
    if len(data) == 0:
        st.warning("No data available for choropleth map.")
        return
    
    # Get latest data for each country
    latest_data = data.groupby('iso_code').last().reset_index()
    
    fig = px.choropleth(
        latest_data,
        locations='iso_code',
        color='total_cases_per_million',
        hover_name='location',
        hover_data=['total_cases', 'total_deaths'],
        color_continuous_scale='Reds',
        title="COVID-19 Total Cases per Million Population"
    )
    
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

def create_bar_chart(data):
    """Create sorted bar chart showing top countries by total deaths"""
    if len(data) == 0:
        st.warning("No data available for bar chart.")
        return
    
    # Get latest data and sort by total deaths
    latest_data = data.groupby('location').last().reset_index()
    latest_data = latest_data.dropna(subset=['total_deaths'])
    latest_data = latest_data.sort_values('total_deaths', ascending=False).head(20)
    
    fig = px.bar(
        latest_data,
        x='total_deaths',
        y='location',
        orientation='h',
        title="Top 20 Countries by Total Deaths",
        labels={'total_deaths': 'Total Deaths', 'location': 'Country'}
    )
    
    fig.update_layout(
        height=600,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    st.plotly_chart(fig, use_container_width=True)

def main():
    """Main application function"""
    
    # Title and description
    st.title("🦠 COVID-19 Dashboard")
    st.markdown("Interactive dashboard showing COVID-19 data from Our World in Data")
    
    # Load data
    with st.spinner("Loading COVID-19 data..."):
        data = load_covid_data()
    
    if len(data) == 0:
        st.error("Failed to load data. Please check your internet connection.")
        return
    
    # Sidebar filters
    selected_countries, start_date, end_date = create_sidebar_filters(data)
    
    # Filter data
    filtered_data = filter_data(data, selected_countries, start_date, end_date)
    
    # Display key metrics
    st.header("📊 Key Metrics")
    display_key_metrics(filtered_data)
    
    # Visualization selector
    st.header("📈 Visualizations")
    chart_type = st.selectbox(
        "Select Visualization Type",
        ["Time-series Line Chart", "Global Choropleth Map", "Top Countries by Deaths (Bar Chart)"]
    )
    
    # Display selected chart
    if chart_type == "Time-series Line Chart":
        create_time_series_chart(filtered_data)
    elif chart_type == "Global Choropleth Map":
        create_choropleth_map(data)  # Use full data for global map
    elif chart_type == "Top Countries by Deaths (Bar Chart)":
        create_bar_chart(data)  # Use full data for ranking
    
    # Data info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ Data Info")
    st.sidebar.markdown(f"**Total Countries:** {data['location'].nunique()}")
    st.sidebar.markdown(f"**Date Range:** {data['date'].min().strftime('%Y-%m-%d')} to {data['date'].max().strftime('%Y-%m-%d')}")
    st.sidebar.markdown(f"**Last Updated:** {data['date'].max().strftime('%Y-%m-%d')}")
    
    # Footer
    st.markdown("---")
    st.markdown("**Data Source:** [Our World in Data](https://ourworldindata.org/coronavirus)")

if __name__ == "__main__":
    main()