# 📈 NADEX — Real-Time 5-Minute Binary Options Market Data CLI

`NADEX` is a powerful Python CLI tool that fetches **live 5-minute binary options forex data** directly from the Nadex exchange. With a single command, you can access comprehensive market data including all available forex pairs, trading levels (strikes), bid/ask prices, and order book quantities — transforming your terminal into a real-time trading dashboard.

Perfect for traders, developers, and financial analysts who need instant access to Nadex's binary options market structure and live pricing data.

---

## 🚀 Key Features

- ⏱ **Real-time 5-minute binary options data** for all major forex pairs
- 💵 **Complete strike levels** with bid/ask prices and available quantities
- 📊 **Full order book visualization** in your terminal
- 🔐 **Built-in test credentials** (easily replaceable with your own)
- 🎯 **Clean, parsable CLI output** for both human reading and automation
- 🐍 **One-command installation** via PyPI (`pip install nadex-cli`)
- 🌐 **WebSocket streaming** for real-time updates
- 📈 **Professional-grade market data** from Nadex exchange

---

## 📦 Quick Installation

Install the package globally using pip:

```bash
pip install nadex-cli
```

That's it! No additional setup required.

---

## ⚡ Quick Start

After installation, simply run:

```bash
nadex_dashboard
```

The CLI will immediately:
1. Connect to Nadex using built-in test credentials
2. Subscribe to the live 5-minute binary options feed
3. Display real-time market data in a clean, organized format

## 🎯 What You Get

### Complete Market Overview
- **All Active Forex Pairs**: EUR/USD, GBP/USD, USD/JPY, AUD/USD, USD/CAD, EUR/GBP, 
- **Strike Levels**: Every available trading level for 5-minute binary options
- **Bid/Ask Prices**: Real-time pricing from the Nadex order book
- **Contract Quantities**: Available volume at each price level

### Real-Time Updates
The dashboard refreshes automatically as new market data arrives via WebSocket connection, ensuring you always see the latest:
- Price movements
- Quantity changes
- New strike levels
- Market status updates

---

## 🔑 Authentication & Credentials

### Default Test Mode
The package comes with **built-in test credentials** that connect to Nadex's demo environment. This means:
- ✅ No real money involved
- ✅ Full access to live market data structure
- ✅ Perfect for learning and development
- ✅ No registration required

### Using Your Own Credentials

If you have a Nadex account and want to use your own credentials:

#### Method 1: Environment Variables
```bash
export NADEX_USERNAME=your-username
export NADEX_PASSWORD=your-password
nadex_dashboard
```

#### Method 2: .env File
Create a `.env` file in your working directory:
```env
NADEX_USERNAME=your-username
NADEX_PASSWORD=your-password
```

Then run the command as usual:
```bash
nadex_dashboard
```

#### Method 3: Direct Configuration
```python
# Custom script using the package
from nadex_dashboard import NadexClient

client = NadexClient(
    username="your-username",
    password="your-password"
)
client.start_dashboard()
```

---

## 🏗️ Architecture & Project Structure

```
nadex/
├── nadex_dashboard/
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration and environment handling
│   ├── helpers.py               # Utility functions and data processing
│   ├── messages.py              # WebSocket message formats and protocols
│   ├── parsing.py               # Market data parsing and validation
│   ├── dashboard.py             # CLI formatting and display logic
│   ├── websocket_manager.py     # WebSocket connection management
│   └── __main__.py              # CLI entry point
├── setup.py                     # Package configuration
├── requirements.txt             # Dependencies
├── README.md                    # This file
└── LICENSE                      # MIT License
```

---

## 📊 Market Data Specifications

### Supported Instruments
- **EUR/USD** - Euro vs US Dollar
- **GBP/USD** - British Pound vs US Dollar  
- **USD/JPY** - US Dollar vs Japanese Yen
- **AUD/USD** - Australian Dollar vs US Dollar
- **USD/CAD** - US Dollar vs Canadian Dollar
- **EUR/JPY** - Euro vs Japanese Yen
- **GBP/JPY** - British Pound vs Japanese Yen

---

### Local Development Setup
```bash
# Clone the repository
git clone https://github.com/shivamgarg-dev/nadex-dashboard.git
cd nadex-dashboard

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/

# Run the CLI
nadex_dashboard
```

---

## ❓ Frequently Asked Questions

### General Questions

**Q: Is this connected to real money?**
A: By default, no. The package uses Nadex's test environment with demo credentials. No real funds are involved unless you explicitly provide your own production credentials.

**Q: Do I need a Nadex account?**
A: No, the package works out-of-the-box with built-in test credentials. However, you can use your own Nadex account if you prefer.

**Q: Is the data real-time?**
A: Yes, the data is streamed live via WebSocket from Nadex's servers with minimal latency.

### Technical Questions

**Q: Can I use this in trading bots?**
A: Absolutely. The package is designed with automation in mind. You can import modules and build custom applications on top of it.

**Q: How often does the data update?**
A: Updates are pushed in real-time as market conditions change, typically 1-5 times per second during active trading hours.

---

## 🗺️ Roadmap

### Upcoming Features
- [ ] **Historical data export** for backtesting
- [ ] **Alert system** for price/volume thresholds
- [ ] **Multiple timeframes** (1-minute, 15-minute options)
- [ ] **Advanced filtering** by instrument, strike range, etc.
- [ ] **REST API mode** for web applications
- [ ] **Docker container** for easy deployment
- [ ] **Grafana dashboard** integration
- [ ] **Telegram/Discord bot** notifications

### Long-term Vision
- Support for other Nadex instrument types (indices, commodities)
- Machine learning integration for pattern recognition
- Advanced analytics and visualization tools
- Mobile app companion

---

## 👨‍💻 Author & Maintainer

**Shivam Garg**  
- 🌐 **GitHub**: [@shivamgarg001](https://github.com/shivamgarg001)

---

## ⭐️ Show Your Support

If you find this tool helpful for your trading, development, or learning:

- ⭐ **Star the repository** on GitHub
- 🍴 **Fork it** to contribute
- 🐛 **Report issues** to help improve it
- 💡 **Suggest features** for future releases
- 📢 **Share it** with others who might benefit

**GitHub Repository**: [https://github.com/shivamgarg001/Nadex]

---

**Happy trading! 📈**