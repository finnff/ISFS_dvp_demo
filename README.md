# Delivery-versus-Payment (DvP) Protocol Demo

A live interactive demonstration comparing **blockchain-based atomic settlement (DvP)** against **traditional clearing** in securities trading. Built for non-technical audiences to visually grasp the difference.

## Live Dashboard

The dashboard runs entirely in the browser with a self-contained simulation engine. No backend required.

- Real-time price chart with settlement event markers
- Latency histogram bars showing DvP (~70ms) vs traditional (~5s) settlement times
- Configurable sliders for traditional market latency and success rate
- Live stats grid comparing both settlement methods
- Settlement feed with pending/settled/failed states

![Dashboard Preview](https://img.shields.io/badge/status-demo-blue)

## Quick Start

### Docker (Recommended)

```bash
docker build -t dvp-dashboard .
docker run -d -p 8555:8555 dvp-dashboard
```

Open [http://localhost:8555](http://localhost:8555)

### Without Docker

```bash
python3 -m http.server 8555
```

Open [http://localhost:8555/dashboard.html](http://localhost:8555/dashboard.html)

### Full Simulation (with backend trader)

```bash
chmod +x run_dvp.sh
./run_dvp.sh
```

This starts the HTTP server and runs `trader_mock.py` (or `trader.py` if a local Ethereum node is available). Falls back to mock mode automatically.

## Components

| File | Description |
|------|-------------|
| `dashboard.html` | Interactive dashboard with price chart, stats, and settlement feed |
| `trader_mock.py` | Mock trader simulation (no blockchain needed) |
| `trader.py` | Real blockchain trader (requires Ganache/Hardhat) |
| `DvPContract.sol` | Solidity smart contract for atomic DvP settlement |
| `deploy.py` | Smart contract deployment script |
| `run_dvp.sh` | Orchestration script with auto-fallback to mock mode |
| `Dockerfile` | Nginx-based container serving the dashboard |
| `index.html` | Redirect to dashboard |

## Dashboard Controls

- **Traditional Settlement Latency** slider (1s - 10s): Controls how long traditional settlements take
- **Traditional Success Rate** slider (50% - 100%): Controls traditional settlement failure probability
- **Pause/Resume**: Freeze the simulation
- **Reset**: Clear all data and restart with current slider values

## How It Works

The dashboard simulates both settlement methods side-by-side for each trade:

1. **Trade executed** (gold arrow on chart)
2. **DvP settlement** completes in ~70ms (cyan marker appears instantly)
3. **Traditional settlement** sits pending for seconds (red marker appears later)
4. The visual gap between cyan and red markers is the core insight

Traditional settlements may also **fail** (~5% default) with reasons like "Counterparty bank rejected transfer" — demonstrating a risk that atomic DvP eliminates entirely.

## Settlement Comparison

| Metric | Blockchain DvP | Traditional |
|--------|---------------|-------------|
| Settlement Time | ~70ms | Configurable (default 5s, real-world T+1 = 24h) |
| Atomicity | Guaranteed | Not guaranteed |
| Failure Risk | 0% | Configurable (default 5%) |
| Intermediaries | 1 smart contract | 5-7 (banks, clearinghouses) |

## Tech Stack

- **Frontend**: Vanilla HTML/JS + [TradingView Lightweight Charts](https://github.com/nickovchinnikov/lightweight-charts)
- **Backend** (optional): Python 3, asyncio, web3.py
- **Blockchain** (optional): Solidity, Ganache/Hardhat
- **Container**: Nginx Alpine

## Dependencies

- Python 3.8+ (only for backend trader)
- Docker (for containerized deployment)
- web3.py, eth-account (see `requirements.txt`, only for `trader.py`)

## Project Context

Built as part of the Information Systems for Financial Services (ISFS) course to demonstrate how blockchain-based Delivery-versus-Payment protocols can improve securities settlement.
