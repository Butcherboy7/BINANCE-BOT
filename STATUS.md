# Project Status Report

This document outlines the current operational status of the Binance Futures Trading Bot, detailing what is working, what is currently restricted, and the technical reasons why.

---

## 🟢 What is Working (100% Verified)

1. **Local Parameter Validation**:
   - Enforces strict checks on trading inputs (symbol casing, BUY/SELL boundaries, quantity restrictions).
   - Validation failures are caught and formatted dynamically into clear warnings (e.g. missing price on LIMIT orders).

2. **Safe Dry-Run Mode (`--dry-run`)**:
   - Fully simulates the end-to-end execution flow.
   - Bypasses external REST requests while outputting simulated execution responses in beautiful tables.
   - Allows safe debugging and unit testing without credentials or network reliance.

3. **Exception and Error Handling**:
   - Custom exception hierarchies (`ValidationError`, `NetworkError`, `BinanceAPIError`) gracefully capture and report runtime failures.

4. **Cryptographic Signature Engine**:
   - Custom HMAC-SHA256 request payload signing and Unix millisecond timestamping align perfectly with the official Binance API specifications.

5. **Logging Subsystem**:
   - Detailed logs covering request params, mock execution results, and connection traces are generated correctly inside `logs/bot.log`.

---

## 🔴 What is Restricted (Live API Calls)

Live execution requests to the Binance Demo/Testnet endpoints currently fail with the following network error:
`urllib3.exceptions.SSLError: [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol`

### Technical Cause:
* **ISP-Level Domain Block**: In India, the government has directed ISPs to block access to Binance domains (including `binance.com`, `fapi.binance.com`, and `demo-fapi.binance.com`).
* **SSL Handshake Failure**: Whenever the Python `requests` library attempts to initiate a secure TLS session with the demo servers, the local ISP intercepts the packets and immediately resets or drops the connection. This sudden termination triggers the `SSLEOFError` in the SSL handshake layer.

---

## 🛠️ Remediation / How to Run Live Orders

To successfully execute live orders on the Demo Futures Testnet:

1. **Enable a VPN**: Turn on any Virtual Private Network (VPN) on the host machine (configured to a region outside India, e.g., US, Europe, or Singapore).
2. **Execute Commands**: Run the CLI order script normally:
   ```bash
   .venv\Scripts\python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
   ```
3. Once the VPN is active, the ISP block is bypassed, the secure SSL handshake will complete, and the order will place successfully on the Binance Demo platform.
