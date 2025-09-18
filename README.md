# COVID-19 Dashboard

An interactive Streamlit dashboard for visualizing COVID-19 data from Our World in Data (OWID).

## Features

- **Interactive Filters**: Country selection and date range filtering via sidebar
- **Key Metrics**: Real-time display of total cases, deaths, vaccinations, and daily averages
- **Multiple Visualizations**:
  - Time-series line chart showing new cases over time
  - Global choropleth map displaying cases per million population
  - Bar chart ranking top countries by total deaths

## Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

## Data Source

The dashboard automatically loads the latest COVID-19 data from:
- [Our World in Data COVID-19 Dataset](https://ourworldindata.org/coronavirus)

## Usage

1. Use the sidebar to select countries and date ranges for filtering
2. View key metrics in the main dashboard
3. Select different visualization types from the dropdown menu
4. Interact with charts for detailed information

## Requirements

- streamlit
- pandas
- plotly
- requests