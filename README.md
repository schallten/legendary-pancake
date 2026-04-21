# 🥞 Legendary Pancake - Binance Futures Trading Bot

A clean, production-ready trading bot for Binance Futures Testnet with market/limit orders, rich CLI UI, and comprehensive logging.

## ✨ Features

- ✅ **Market & Limit Orders** - Both order types fully supported
- ✅ **BUY/SELL** - Trade both sides of the market
- ✅ **Rich CLI** - Beautiful tables, colors, and progress bars
- ✅ **Input Validation** - Smart validation with clear error messages
- ✅ **Comprehensive Logging** - All API calls logged to `logs/` directory
- ✅ **Error Handling** - Network errors, API failures, invalid inputs

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- [Binance Futures Testnet account](https://testnet.binancefuture.com/) (get free test funds)

### Installation

```bash
# Clone the repository
git clone https://github.com/schallten/legendary-pancake.git
cd legendary-pancake

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies with uv
uv sync
```

### Configuration

Create a `.env` file with your testnet API credentials:

```bash
# Copy example file
cp .env.example .env

# Edit with your keys (get from https://testnet.binancefuture.com/)
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_secret_here
```

## 📖 Usage

### Interactive Mode (Recommended)
```bash
python cli.py --interactive
```

### Command Line Examples

**Market Order:**
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

**Limit Order:**
```bash
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 2100
```

## 📊 Sample Output

```
╔══════════════════════════════════════════════╗
║     🚀 Binance Futures Trading Bot v1.0     ║
║         [Testnet Environment]               ║
╚══════════════════════════════════════════════╝

┌──────────────────────────────────────────────┐
│           📋 Order Summary                   │
├────────────┬─────────────────────────────────┤
│ Symbol     │ BTCUSDT                         │
│ Side       │ BUY                             │
│ Type       │ MARKET                          │
│ Quantity   │ 0.001                           │
└────────────┴─────────────────────────────────┘

✅ Order Successful
┌─────────────────┬─────────────────┐
│ Order ID        │ 876543210       │
│ Status          │ FILLED          │
│ Executed        │ 0.001           │
│ Avg Price       │ $45123.45       │
└─────────────────┴─────────────────┘
```

## 📁 Project Structure

```
legendary-pancake/
├── bot/
│   ├── client.py          # Binance API wrapper
│   ├── orders.py          # Order placement logic
│   ├── validators.py      # Input validation
│   └── logging_config.py  # Logging setup
├── cli.py                 # Main entry point
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
└── logs/                 # Auto-generated logs
```

## 📝 Logging

All API requests, responses, and errors are logged to `logs/trading_bot_*.log` with timestamps and full details.

## 🛠️ Dependencies

- `httpx` - Async HTTP client
- `rich` - Beautiful terminal UI
- `python-dotenv` - Environment management
- `click` - CLI argument parsing

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "API credentials not found" | Create `.env` file with valid keys |
| "Invalid symbol" | Use format like `BTCUSDT`, `ETHUSDT` |
| "Insufficient balance" | Get test funds from [testnet faucet](https://testnet.binancefuture.com/) |
| Module errors | Run `uv pip install -r requirements.txt` |
