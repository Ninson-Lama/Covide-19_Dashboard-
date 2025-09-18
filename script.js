// COVID-19 Dashboard JavaScript with Mock Data Fallback
class CovidDashboard {
    constructor() {
        this.apiBaseUrl = 'https://disease.sh/v3/covid-19';
        this.mockData = this.getMockData();
        this.init();
    }

    getMockData() {
        return {
            global: {
                cases: 704189651,
                deaths: 6977893,
                recovered: 675434109,
                active: 21777649,
                todayCases: 24567,
                todayDeaths: 445,
                todayRecovered: 18923
            },
            countries: [
                {
                    country: "USA",
                    cases: 103436829,
                    deaths: 1127152,
                    recovered: 100717827,
                    active: 1591850
                },
                {
                    country: "China",
                    cases: 99362755,
                    deaths: 121668,
                    recovered: 98800326,
                    active: 440761
                },
                {
                    country: "India",
                    cases: 44997809,
                    deaths: 533623,
                    recovered: 44441115,
                    active: 23071
                },
                {
                    country: "France",
                    cases: 38997490,
                    deaths: 174632,
                    recovered: 38494899,
                    active: 327959
                },
                {
                    country: "Germany",
                    cases: 38437756,
                    deaths: 174979,
                    recovered: 37800800,
                    active: 461977
                },
                {
                    country: "Brazil",
                    cases: 37717529,
                    deaths: 704659,
                    recovered: 36415195,
                    active: 597675
                },
                {
                    country: "Japan",
                    cases: 33320438,
                    deaths: 74694,
                    recovered: 33053361,
                    active: 192383
                },
                {
                    country: "South Korea",
                    cases: 30627471,
                    deaths: 34152,
                    recovered: 29799135,
                    active: 794184
                },
                {
                    country: "Italy",
                    cases: 25870833,
                    deaths: 190893,
                    recovered: 24987199,
                    active: 692741
                },
                {
                    country: "Russia",
                    cases: 22075858,
                    deaths: 396266,
                    recovered: 21334543,
                    active: 345049
                }
            ]
        };
    }

    async init() {
        try {
            // Try to load real data first, fall back to mock data if failed
            const useRealData = await this.checkApiAvailability();
            
            if (useRealData) {
                await this.loadGlobalData();
                await this.loadCountriesData();
            } else {
                console.log('Using mock data due to API restrictions');
                this.loadMockData();
            }
            
            this.hideLoading();
            this.updateLastUpdated();
        } catch (error) {
            console.error('Error loading data, using mock data:', error);
            this.loadMockData();
            this.hideLoading();
            this.updateLastUpdated();
        }
    }

    async checkApiAvailability() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000);
            
            const response = await fetch(`${this.apiBaseUrl}/all`, {
                signal: controller.signal,
                mode: 'cors'
            });
            
            clearTimeout(timeoutId);
            return response.ok;
        } catch (error) {
            return false;
        }
    }

    loadMockData() {
        const data = this.mockData.global;
        this.updateStatCard('total-cases', data.cases, data.todayCases, '+');
        this.updateStatCard('total-deaths', data.deaths, data.todayDeaths, '+');
        this.updateStatCard('total-recovered', data.recovered, data.todayRecovered, '+');
        this.updateStatCard('active-cases', data.active, null, '');
        
        this.renderCountries(this.mockData.countries);
        
        // Show a notice that this is demo data
        this.showMockDataNotice();
    }

    showMockDataNotice() {
        const footer = document.querySelector('footer');
        if (footer) {
            const notice = document.createElement('div');
            notice.innerHTML = `
                <div style="
                    background: rgba(255, 255, 255, 0.1);
                    padding: 10px;
                    border-radius: 5px;
                    margin-bottom: 15px;
                    text-align: center;
                ">
                    📊 <strong>Demo Mode:</strong> Showing sample data for demonstration purposes
                </div>
            `;
            footer.insertBefore(notice, footer.firstChild);
        }
    }

    async loadGlobalData() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/all`);
            const data = await response.json();
            
            this.updateStatCard('total-cases', data.cases, data.todayCases, '+');
            this.updateStatCard('total-deaths', data.deaths, data.todayDeaths, '+');
            this.updateStatCard('total-recovered', data.recovered, data.todayRecovered, '+');
            this.updateStatCard('active-cases', data.active, null, '');
        } catch (error) {
            console.error('Error loading global data:', error);
            throw error;
        }
    }

    async loadCountriesData() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/countries?sort=cases`);
            const countries = await response.json();
            
            // Get top 10 countries
            const topCountries = countries.slice(0, 10);
            this.renderCountries(topCountries);
        } catch (error) {
            console.error('Error loading countries data:', error);
            throw error;
        }
    }

    updateStatCard(elementId, total, todayChange, prefix) {
        const totalElement = document.getElementById(elementId);
        const changeElement = document.getElementById(elementId.replace('total-', 'new-').replace('active-cases', 'active-change'));
        
        if (totalElement) {
            totalElement.textContent = this.formatNumber(total);
        }
        
        if (changeElement && todayChange !== null && todayChange !== undefined) {
            changeElement.textContent = `${prefix}${this.formatNumber(todayChange)} today`;
        } else if (changeElement) {
            changeElement.textContent = 'Active cases';
        }
    }

    renderCountries(countries) {
        const container = document.getElementById('countries-grid');
        if (!container) return;

        container.innerHTML = '';
        
        countries.forEach(country => {
            const countryCard = this.createCountryCard(country);
            container.appendChild(countryCard);
        });
    }

    createCountryCard(country) {
        const card = document.createElement('div');
        card.className = 'country-card';
        
        card.innerHTML = `
            <div class="country-name">${country.country}</div>
            <div class="country-stats">
                <div class="country-stat">
                    <span>Total Cases:</span>
                    <span>${this.formatNumber(country.cases)}</span>
                </div>
                <div class="country-stat">
                    <span>Deaths:</span>
                    <span>${this.formatNumber(country.deaths)}</span>
                </div>
                <div class="country-stat">
                    <span>Recovered:</span>
                    <span>${this.formatNumber(country.recovered)}</span>
                </div>
                <div class="country-stat">
                    <span>Active:</span>
                    <span>${this.formatNumber(country.active)}</span>
                </div>
            </div>
        `;
        
        return card;
    }

    formatNumber(num) {
        if (num === null || num === undefined) return 'N/A';
        return new Intl.NumberFormat().format(num);
    }

    hideLoading() {
        const loading = document.getElementById('loading');
        const mainContent = document.getElementById('main-content');
        
        if (loading) loading.classList.add('hidden');
        if (mainContent) mainContent.classList.remove('hidden');
    }

    showError() {
        const loading = document.getElementById('loading');
        if (loading) {
            loading.innerHTML = `
                <div style="color: white; text-align: center;">
                    <h3>⚠️ Error Loading Data</h3>
                    <p>Unable to fetch COVID-19 data. Please check your internet connection and try again.</p>
                    <button onclick="location.reload()" style="
                        margin-top: 20px;
                        padding: 10px 20px;
                        background: white;
                        color: #333;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        font-weight: 600;
                    ">Retry</button>
                </div>
            `;
        }
    }

    updateLastUpdated() {
        const lastUpdatedElement = document.getElementById('last-updated');
        if (lastUpdatedElement) {
            const now = new Date();
            lastUpdatedElement.textContent = now.toLocaleString();
        }
    }
}

// Auto-refresh functionality
class AutoRefresh {
    constructor(dashboard) {
        this.dashboard = dashboard;
        this.refreshInterval = 5 * 60 * 1000; // 5 minutes
        this.start();
    }

    start() {
        setInterval(() => {
            console.log('Auto-refreshing data...');
            this.dashboard.init();
        }, this.refreshInterval);
    }
}

// Initialize the dashboard when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new CovidDashboard();
    
    // Start auto-refresh after initial load
    setTimeout(() => {
        new AutoRefresh(dashboard);
    }, 1000);
});

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === 'F5' || (e.ctrlKey && e.key === 'r')) {
        e.preventDefault();
        location.reload();
    }
});

// Service Worker for offline functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then((registration) => {
                console.log('SW registered: ', registration);
            })
            .catch((registrationError) => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}