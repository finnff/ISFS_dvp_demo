#!/bin/bash
# DvP Protocol - Run Script
# Orchestrates the entire DvP prototype

# Track all child PIDs for cleanup
CHILD_PIDS=()

cleanup() {
    echo ""
    echo "Shutting down all processes..."
    for pid in "${CHILD_PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null
            echo "  Stopped PID $pid"
        fi
    done
    # Kill any remaining children of this script
    pkill -P $$ 2>/dev/null
    echo "Done. Goodbye."
    exit 0
}
trap cleanup INT TERM EXIT

set -e

echo "=============================================="
echo "  Delivery-versus-Payment (DvP) Prototype"
echo "=============================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q -r requirements.txt

USE_MOCK=false

# Check if ganache is running by testing the actual RPC endpoint
echo "Checking for local Ethereum node..."
if curl -s -X POST --connect-timeout 2 -H "Content-Type: application/json" \
    --data '{"jsonrpc":"2.0","method":"net_version","params":[],"id":1}' \
    http://127.0.0.1:8545 > /dev/null 2>&1; then
    echo "Local Ethereum node already running"
elif command -v ganache-cli > /dev/null 2>&1; then
    echo "Starting local Ethereum blockchain (ganache-cli)..."
    ganache-cli -d --port 8545 &
    CHILD_PIDS+=($!)
    echo "Ganache started with PID: $!"
    sleep 3
else
    echo "ganache-cli not found and no Ethereum node running."
    echo "Falling back to MOCK mode."
    USE_MOCK=true
fi

echo ""
echo "=============================================="
echo "  Starting Dashboard & Simulation"
echo "=============================================="
echo ""

# Start the HTTP server BEFORE the trader so the dashboard is live during simulation
echo "Starting dashboard server on http://localhost:8555 ..."
python3 -m http.server 8555 --directory "$(pwd)" &
CHILD_PIDS+=($!)
echo ""
echo "Dashboard is live at: http://localhost:8555/dashboard.html"
echo ""

# Run the trader simulation
if [ "$USE_MOCK" = true ]; then
    echo "Running mock trader..."
    python trader_mock.py &
else
    echo "Running on-chain trader..."
    python trader.py &
fi
CHILD_PIDS+=($!)

# Wait for the trader to finish
wait ${CHILD_PIDS[-1]}

echo ""
echo "=============================================="
echo "  Simulation Complete!"
echo "=============================================="
echo ""
echo "Results saved to: settlements.json"
echo "Dashboard still running at: http://localhost:8555/dashboard.html"
echo ""
echo "Press Ctrl+C to stop all services and exit"

# Wait for remaining background processes (HTTP server)
wait
