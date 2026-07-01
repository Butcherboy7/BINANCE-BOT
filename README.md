# Binance Futures Testnet Trading Bot (USDT-M)

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](#)
[![Binance Futures Testnet](https://img.shields.io/badge/Binance-Futures%20Testnet-orange.svg)](https://testnet.binancefuture.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#)

A production-quality Python command-line interface (CLI) client built using clean architecture principles to place orders on the **Binance Futures Testnet (USDT-M)**. 

Rather than relying on high-level wrappers, this codebase implements low-level HMAC-SHA256 signature generation and raw HTTP calls, demonstrating safe testing practices, input validation, robust logging, custom exception hierarchies, and network resilience.

---

## Architecture Overview

The project is structured to strictly separate concerns, enforcing a clean boundary between the terminal user interface, business rules, and external network resources:

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── binance_client.py   # Low-level REST API communicator with retry logic
│   ├── config.py           # Loads and validates environment variables
│   ├── exceptions.py       # Custom app-level exception hierarchy
│   ├── logging_config.py   # Handles structured file logging (logs/bot.log)
│   ├── models.py           # Dataclasses representing requests/responses
│   ├── orders.py           # Business orchestrator; handles dry-runs & validation dispatch
│   ├── utils.py            # HMAC signatures, timestamp calculations
│   └── validators.py       # Local input parameters validator
├── cli.py                  # CLI entry point (argparse parser & Rich formatting)
├── requirements.txt        # Production dependencies
├── .env                    # Secret environment credentials
└── README.md               # User documentation
```

### Flow of Execution

1. **CLI Layer (`cli.py`)**: Accepts CLI arguments, displays an initial visual summary, and triggers the orchestrator.
2. **Business Layer (`bot/orders.py`)**: Validates inputs locally before contacting the API. Checks if `--dry-run` is enabled; if so, returns a mock execution without placing an order. Otherwise, passes execution to the API client.
3. **API Client (`bot/binance_client.py`)**: Computes millisecond timestamps, generates request query strings, signs payloads cryptographically using HMAC-SHA256, sets headers, and handles raw HTTP requests.
4. **Network Layer**: Performs requests with **exponential backoff retry logic** (up to 3 attempts) for connection/network failures.
5. **Logging Handler (`bot/logging_config.py`)**: Records every step (requests, raw JSON payloads, API response statuses, errors) directly to `logs/bot.log` while keeping the terminal UI pristine.

---

## Cryptographic Request Signing

Binance endpoints under `/fapi/*` require authentication. This client executes manual request signing as follows:

1. **Timestamping**: Acquires the current Unix time in milliseconds.
2. **Query Normalization**: Serializes parameters (e.g. `symbol=BTCUSDT&side=BUY&type=MARKET&quantity=0.001&recvWindow=60000&timestamp=1719812400000`).
3. **HMAC-SHA256 Signing**: Signs the query string using the `SECRET_KEY` as the cryptographic key.
4. **Appended Signature**: Appends the hex digest of the signature as an additional URL query parameter (`&signature=...`).
5. **API Key Header**: Inserts the `API_KEY` into the custom header `X-MBX-APIKEY`.

---

## Installation & Setup

### Prerequisites

- Python 3.10 or newer.

### 1. Clone & Initialize Environment

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows (Command Prompt):
.venv\Scripts\activate
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On macOS / Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Credentials

Create a `.env` file in the project root:

```env
BINANCE_API_KEY=your_actual_futures_testnet_api_key
BINANCE_SECRET_KEY=your_actual_futures_testnet_secret_key
BINANCE_BASE_URL=https://testnet.binancefuture.com
```

---

## Usage Examples

Run the CLI using python:

### 1. Safe Dry Run (No Credentials Required)
Verify inputs and simulate order responses without hitting the API:
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --dry-run
```

### 2. Place a Market BUY Order (Live)
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### 3. Place a Limit SELL Order (Live)
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 95000.00
```

---

## Logging System

Every request, response payload, and API error is securely outputted to `logs/bot.log`. 

```text
2026-07-01 22:50:12,123 [INFO] (orders.py:41) - Order placement initiated - Symbol: BTCUSDT | Side: BUY | Type: MARKET | Qty: 0.001 | Price: None | Dry Run: False
2026-07-01 22:50:12,305 [INFO] (binance_client.py:45) - API Request - Method: POST | URL: https://testnet.binancefuture.com/fapi/v1/order | Params: symbol=BTCUSDT&side=BUY&type=MARKET&quantity=0.001&recvWindow=60000&timestamp=1719864012000&signature=4f46...
2026-07-01 22:50:12,680 [INFO] (binance_client.py:75) - API Response - Status: 200 | Payload: {'orderId': 123456789, 'symbol': 'BTCUSDT', 'status': 'FILLED', 'executedQty': '0.001', 'avgPrice': '95100.50', ...}
```
