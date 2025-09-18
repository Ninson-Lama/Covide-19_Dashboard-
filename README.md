# COVID-19 Dashboard

A real-time COVID-19 statistics dashboard that displays global and country-specific data.

## Features

- 🌍 **Global Statistics**: Total cases, deaths, recovered, and active cases
- 📊 **Country Rankings**: Top 10 most affected countries
- 🔄 **Auto-refresh**: Data updates every 5 minutes
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile
- ⚡ **Fast Loading**: Modern web technologies for optimal performance
- 🎨 **Clean UI**: Beautiful, intuitive interface

## Quick Start

1. Open `index.html` in your web browser
2. The dashboard will automatically load the latest COVID-19 data
3. Data refreshes automatically every 5 minutes

## Live Demo

Simply open the `index.html` file in any modern web browser. No installation or setup required!

## Data Source

This dashboard uses the [disease.sh](https://disease.sh) API, which provides:
- Real-time global COVID-19 statistics
- Country-specific data
- Historical data tracking
- Reliable, frequently updated information

## Browser Compatibility

- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 12+
- ✅ Edge 79+

## Features Overview

### Global Statistics
- Total confirmed cases worldwide
- Total deaths
- Total recovered patients
- Current active cases

### Country Data
- Top 10 countries by total cases
- Individual statistics for each country
- Cases, deaths, recovered, and active cases per country

### Technical Features
- Responsive CSS Grid layout
- Modern JavaScript (ES6+)
- Fetch API for data retrieval
- Error handling and loading states
- Auto-refresh functionality

## File Structure

```
├── index.html      # Main HTML file
├── style.css       # Styling and layout
├── script.js       # JavaScript functionality
└── README.md       # This file
```

## Customization

You can easily customize the dashboard by modifying:

- **Colors**: Edit the CSS variables in `style.css`
- **Refresh Rate**: Change the `refreshInterval` in `script.js`
- **Countries Shown**: Modify the slice parameter in `loadCountriesData()`
- **Data Source**: Update the `apiBaseUrl` to use a different API

## Contributing

1. Fork the repository
2. Create your feature branch
3. Make your changes
4. Test in multiple browsers
5. Submit a pull request

## License

This project is open source and available under the MIT License.