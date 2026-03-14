#!/usr/bin/env python3
"""
Algorithmic Trader Simulation for DvP Protocol
Simulates orders being sent to smart contract for atomic settlement
"""

import asyncio
import json
import os
import time
import random
from datetime import datetime
from typing import List, Dict, Any
from web3 import Web3
from eth_account import Account

# Configuration - Using Ganache default addresses
RPC_URL = "http://127.0.0.1:8545"
TRADER_PRIVATE_KEY = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"
TRADER_ADDRESS = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"

# Settlement tracking
settlements: List[Dict[str, Any]] = []

# Simulated asset price (geometric random walk)
_asset_price = 150.0

TRADITIONAL_FAIL_REASONS = [
    "Counterparty bank rejected transfer",
    "Clearing house reconciliation mismatch",
    "Custodian authentication timeout",
    "Insufficient margin at intermediary",
    "Regulatory hold placed on transfer",
    "Settlement agent system outage",
]


def _next_asset_price() -> float:
    """Advance the simulated asset price by one tick (geometric random walk)."""
    global _asset_price
    drift = 0.0001
    vol = 0.002
    shock = random.gauss(0, 1)
    _asset_price *= (1 + drift + vol * shock)
    return round(_asset_price, 2)


def write_settlements():
    """Atomically write the global settlements list to settlements.json."""
    tmp_path = "settlements.json.tmp"
    with open(tmp_path, "w") as f:
        json.dump(settlements, f, indent=2)
    os.replace(tmp_path, "settlements.json")


class AlgorithmicTrader:
    def __init__(self, w3: Web3, contract_address: str, private_key: str):
        self.w3 = w3
        self.account = Account.from_key(private_key)
        self.contract = self._load_contract(contract_address)
        self.is_running = False

    def _load_contract(self, address: str):
        """Load the DvP contract ABI and create contract instance"""
        abi = [{
            "inputs": [{
                "internalType": "address", "name": "trader", "type": "address"
            }, {"internalType": "address", "name": "cashToken", "type": "address"},
            {"internalType": "address", "name": "securitiesToken", "type": "address"},
            {"internalType": "uint256", "name": "cashAmount", "type": "uint256"},
            {"internalType": "uint256", "name": "securitiesAmount", "type": "uint256"},
            {"internalType": "address", "name": "cashRecipient", "type": "address"},
            {"internalType": "address", "name": "securitiesRecipient", "type": "address"}
            ],
            "name": "settleTrade",
            "outputs": [{"internalType": "bool", "name": "success", "type": "bool"}],
            "stateMutability": "nonpayable", "type": "function"
        }, {
            "anonymous": False,
            "inputs": [{
                "indexed": True, "internalType": "address", "name": "trader", "type": "address"
            }, {"indexed": False, "internalType": "uint256", "name": "cashTokenId", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "securitiesTokenId", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "cashAmount", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "securitiesAmount", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "gasUsed", "type": "uint256"}
            ],
            "name": "Settlement", "type": "event"
        }, {
            "inputs": [
                {"internalType": "address", "name": "token", "type": "address"},
                {"internalType": "address", "name": "account", "type": "address"}
            ],
            "name": "getBalance",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view", "type": "function"
        }]
        return self.w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)

    def generate_order(self, order_id: int) -> Dict[str, Any]:
        """Generate a random trade order"""
        return {
            "orderId": order_id,
            "cashAmount": random.randint(100, 10000),  # ETH cents
            "securitiesAmount": random.randint(10, 1000),  # Shares
            "cashRecipient": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
            "securitiesRecipient": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
            "assetPrice": _next_asset_price(),
        }

    async def submit_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Submit order to smart contract for atomic settlement"""
        submission_time = time.time()

        # Build transaction
        tx = self.contract.functions.settleTrade(
            self.account.address,
            Web3.to_checksum_address("0x0000000000000000000000000000000000000001"),
            Web3.to_checksum_address("0x0000000000000000000000000000000000000002"),
            order["cashAmount"],
            order["securitiesAmount"],
            Web3.to_checksum_address(order["cashRecipient"]),
            Web3.to_checksum_address(order["securitiesRecipient"])
        ).build_transaction({
            'from': self.account.address,
            'gas': 300000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address)
        })

        # Sign and send transaction
        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        # Wait for confirmation
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

        settlement_time = time.time()
        latency = settlement_time - submission_time

        return {
            "orderId": order["orderId"],
            "status": "settled" if receipt.status == 1 else "failed",
            "type": "dvp",
            "assetSymbol": "ACME",
            "assetPrice": order.get("assetPrice", 150.0),
            "cashAmount": order["cashAmount"],
            "securitiesAmount": order["securitiesAmount"],
            "submissionTime": submission_time,
            "settlementTime": settlement_time,
            "latencyMs": latency * 1000,
            "txHash": tx_hash.hex(),
            "blockNumber": receipt.blockNumber,
            "atomic": True,
        }

    async def _resolve_traditional(self, record: Dict[str, Any]):
        """Simulate the delayed resolution of a traditional settlement."""
        await asyncio.sleep(random.uniform(1.5, 2.5))
        if random.random() < 0.01:
            record["status"] = "failed"
            record["traditionalFailReason"] = random.choice(TRADITIONAL_FAIL_REASONS)
        else:
            record["status"] = "settled"
            record["settlementTime"] = time.time()
            record["latencyMs"] = (record["settlementTime"] - record["submissionTime"]) * 1000
        write_settlements()

    async def run_simulation(self, num_orders: int = 20, interval: float = 2.0):
        """Run the trader simulation"""
        self.is_running = True
        order_id = 0

        # Start with an empty settlements file
        write_settlements()

        print(f"\n{'='*60}")
        print(f"DvP Protocol Trader Simulation")
        print(f"{'='*60}")
        print(f"Trading as: {self.account.address}")
        print(f"Contract: {CONTRACT_ADDRESS}")
        print(f"Starting simulation with {num_orders} orders...\n")

        while self.is_running and order_id < num_orders:
            order = self.generate_order(order_id)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Order #{order_id}: "
                  f"Cash={order['cashAmount']} | Securities={order['securitiesAmount']} | "
                  f"ACME @ ${order['assetPrice']:.2f}")

            try:
                result = await self.submit_order(order)
                settlements.append(result)
                write_settlements()
                print(f"  -> DvP Settled in {result['latencyMs']:.2f}ms | "
                      f"Block #{result['blockNumber']}")

                # Create a companion traditional settlement (pending)
                trad_record = {
                    "orderId": order_id,
                    "status": "pending",
                    "type": "traditional",
                    "assetSymbol": "ACME",
                    "assetPrice": order["assetPrice"],
                    "cashAmount": order["cashAmount"],
                    "securitiesAmount": order["securitiesAmount"],
                    "submissionTime": result["submissionTime"],
                    "settlementTime": None,
                    "latencyMs": None,
                    "atomic": False,
                }
                settlements.append(trad_record)
                write_settlements()
                print(f"  -> Traditional settlement pending...")

                asyncio.create_task(self._resolve_traditional(trad_record))

            except Exception as e:
                print(f"  -> Error: {e}")

            order_id += 1
            if order_id < num_orders:
                await asyncio.sleep(interval)

        # Wait for remaining traditional settlements to resolve
        await asyncio.sleep(3)

        print(f"\n{'='*60}")
        print(f"Simulation Complete: {len(settlements)} records")
        print(f"{'='*60}\n")

        return settlements

async def main():
    """Main entry point"""
    w3 = Web3(Web3.HTTPProvider(RPC_URL))

    if not w3.is_connected():
        print("Error: Could not connect to Ethereum node")
        print("Please start a local node first (e.g., ganache-cli or hardhat node)")
        return

    trader = AlgorithmicTrader(w3, CONTRACT_ADDRESS, TRADER_PRIVATE_KEY)

    # Run simulation
    results = await trader.run_simulation(num_orders=20, interval=2.0)

    # Save final results
    write_settlements()
    print("Results saved to settlements.json")

if __name__ == "__main__":
    asyncio.run(main())
