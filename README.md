# Binance Futures Testnet Trading Bot (USDT-M)

A production-ready command-line interface (CLI) client built using clean architecture principles to place orders on the **Binance Futures Testnet (USDT-M)**.

Rather than relying on high-level wrappers, this codebase implements low-level HMAC-SHA256 signature generation and raw HTTP calls, demonstrating safe testing practices, input validation, robust logging, custom exception hierarchies, and network resilience.

---

## 🏛️ Architecture & Decisions

The project is structured to strictly separate concerns, enforcing a clean boundary between the user interface, business rules, and external network resources:

* **Presentation Layer (`cli.py`)**: Accepts CLI arguments, displays visual summaries via `rich`, and calls the orchestrator.
* **Business Layer (`bot/orders.py`)**: Handles dry-run routing and orchestrates validation.
* **Domain Layer (`bot/validators.py`)**: Sanitizes inputs (symbols, quantity, prices) locally before making network requests.
* **API Client Layer (`bot/binance_client.py`)**: Signs payloads using HMAC-SHA256 and communicates with the Binance Demo REST endpoints.

> [!NOTE]
> For a detailed walkthrough of design tradeoffs, clean architecture principles, and manual cryptographic signing implementation details, check out [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 🚀 Getting Started

### Prerequisites

* Python 3.10 or newer
* A Binance Demo Account (access via [demo.binance.com](https://demo.binance.com/))

### 1. Installation

Clone the repository and set up a virtual environment:

```bash
# Clone the repository
git clone https://github.com/Butcherboy7/BINANCE-BOT.git
cd BINANCE-BOT

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

Create a `.env` file in the root directory:

```env
BINANCE_API_KEY=your_copied_api_key_from_demo_portal
BINANCE_SECRET_KEY=your_copied_secret_key_from_demo_portal
BINANCE_BASE_URL=https://demo-fapi.binance.com
```

> [!IMPORTANT]
> Make sure to copy both the API Key and Secret Key from the **Binance Demo Trading** API Management page (`demo.binance.com`) and paste them exactly. The base URL for the Demo Futures environment is `https://demo-fapi.binance.com`.

---

## 💻 Usage Examples

### 1. Local Dry Run (No Credentials Required)
Verify inputs and simulate order responses without hitting the API:
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --dry-run
```

### 2. Place a Market BUY Order (Live API)
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### 3. Place a Limit BUY Order (Live API)
```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 90000.00
```

---

## 📝 Logging System

Every request parameter, raw JSON payload, API response, and connection warning is recorded inside `logs/bot.log`. 

```text
2026-07-02 10:53:25,092 [INFO] (orders.py:58) - Order placement initiated - Symbol: BTCUSDT | Side: BUY | Type: MARKET | Qty: 0.001 | Price: None | Dry Run: True
2026-07-02 10:53:25,092 [INFO] (orders.py:66) - Dry-run mode is enabled. Skipping actual API request.
```

---

## 🌐 Network Troubleshooting (ISP blocks)

If you are running live orders from India, the ISP-level blocks on Binance domains will cause network connection or SSL errors. 

**Remediation**: Enable a VPN on the host machine configured to a region outside India (e.g., US, Europe, or Singapore) before running live API calls.
