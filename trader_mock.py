#!/usr/bin/env python3
"""
Algorithmic Trader Simulation for DvP Protocol (Mock Mode)
Demonstrates atomic settlement with simulated blockchain behavior
"""

import asyncio
import json
import os
import time
import random
from datetime import datetime
from typing import List, Dict, Any

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


class MockBlockchain:
    """Simulates blockchain behavior for demonstration"""

    def __init__(self):
        self.block_time = 0.5  # 500ms per block
        self.gas_price = 20000000000  # 20 gwei

    async def simulate_settlement(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate atomic settlement on blockchain"""
        submission_time = time.time()

        # Simulate network latency and block time
        await asyncio.sleep(random.uniform(0.1, 0.3))  # Network propagation
        await asyncio.sleep(random.uniform(0.2, 0.4))  # Block confirmation

        settlement_time = time.time()
        latency = settlement_time - submission_time

        return {
            "orderId": order["orderId"],
            "status": "settled",
            "type": "dvp",
            "assetSymbol": "ACME",
            "assetPrice": order.get("assetPrice", 150.0),
            "cashAmount": order.get("cashAmount", 0),
            "securitiesAmount": order.get("securitiesAmount", 0),
            "securityType": order.get("securityType", "Stock"),
            "counterparty": order.get("counterparty", "Unknown"),
            "submissionTime": submission_time,
            "settlementTime": settlement_time,
            "latencyMs": latency * 1000,
            "blockNumber": int((submission_time - 1000000) / self.block_time),
            "atomic": True
        }


class AlgorithmicTrader:
    def __init__(self):
        self.trader_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
        self.contract_address = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
        self.blockchain = MockBlockchain()
        self.is_running = False

    def generate_order(self, order_id: int) -> Dict[str, Any]:
        """Generate a random trade order"""
        return {
            "orderId": order_id,
            "cashAmount": random.randint(1000, 100000),  # US cents
            "securitiesAmount": random.randint(10, 1000),  # Shares
            "securityType": random.choice(["Stock", "Bond", "ETF", "Commodity"]),
            "counterparty": f"Counterparty_{random.randint(1, 10)}",
            "assetPrice": _next_asset_price(),
        }

    async def submit_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Submit order for atomic settlement"""
        return await self.blockchain.simulate_settlement(order)

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

    async def run_simulation(self, num_orders: int = 0, interval: float = 1.5):
        """Run the trader simulation. num_orders=0 means run forever."""
        self.is_running = True
        order_id = 0

        # Start with an empty settlements file
        write_settlements()

        print(f"\n{'='*70}")
        print(f"  DvP Protocol - Atomic Settlement Demo (Mock Mode)")
        print(f"{'='*70}")
        print(f"  Trading Address: {self.trader_address}")
        print(f"  Smart Contract: {self.contract_address}")
        print(f"  Blockchain: Local Ethereum (Simulated)")
        mode = "continuous" if num_orders == 0 else f"{num_orders} orders"
        print(f"  Starting simulation ({mode})...\n")

        while self.is_running and (num_orders == 0 or order_id < num_orders):
            order = self.generate_order(order_id)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Order #{order_id}:")
            print(f"    {order['securityType']} | Cash: ${order['cashAmount']:.2f} | "
                  f"Securities: {order['securitiesAmount']} shares | "
                  f"ACME @ ${order['assetPrice']:.2f}")

            try:
                result = await self.submit_order(order)
                settlements.append(result)
                write_settlements()
                print(f"    DvP SETTLED in {result['latencyMs']:.2f}ms | "
                      f"Block #{result['blockNumber']} | Atomic: YES")

                # Create a companion traditional settlement (pending)
                trad_record = {
                    "orderId": order_id,
                    "status": "pending",
                    "type": "traditional",
                    "assetSymbol": "ACME",
                    "assetPrice": order["assetPrice"],
                    "cashAmount": order["cashAmount"],
                    "securitiesAmount": order["securitiesAmount"],
                    "securityType": order["securityType"],
                    "counterparty": order["counterparty"],
                    "submissionTime": result["submissionTime"],
                    "settlementTime": None,
                    "latencyMs": None,
                    "atomic": False,
                }
                settlements.append(trad_record)
                write_settlements()
                print(f"    Traditional settlement pending...")

                # Resolve the traditional settlement after a delay
                asyncio.create_task(self._resolve_traditional(trad_record))

            except Exception as e:
                print(f"    Error: {e}")

            order_id += 1
            if order_id < num_orders:
                await asyncio.sleep(interval)

        # Wait a bit for any remaining traditional settlements to resolve
        await asyncio.sleep(3)

        print(f"\n{'='*70}")
        print(f"  Simulation Complete: {len(settlements)} records")
        print(f"{'='*70}\n")

        return settlements


async def main():
    """Main entry point"""
    trader = AlgorithmicTrader()

    # Run simulation
    results = await trader.run_simulation(num_orders=0, interval=1.5)

    # Calculate statistics
    dvp = [s for s in results if s.get("type") == "dvp"]
    trad = [s for s in results if s.get("type") == "traditional"]

    if dvp:
        avg_latency = sum(s['latencyMs'] for s in dvp) / len(dvp)
        min_latency = min(s['latencyMs'] for s in dvp)
        max_latency = max(s['latencyMs'] for s in dvp)
    else:
        avg_latency = min_latency = max_latency = 0

    trad_settled = [s for s in trad if s["status"] == "settled" and s["latencyMs"] is not None]
    trad_failed = [s for s in trad if s["status"] == "failed"]

    print("Results saved to settlements.json")
    print("\n" + "="*70)
    print("  LATENCY COMPARISON: On-Chain DvP vs Traditional T+1")
    print("="*70)
    print(f"  {'Metric':<30} {'On-Chain DvP':<20} {'Traditional T+1':<20}")
    print("-"*70)
    print(f"  {'Settlement Time':<30} {'<1 second':<20} {'24+ hours':<20}")
    print(f"  {'Average Latency':<30} {avg_latency:.2f} ms{'':<14} {'~86,400,000 ms':<20}")
    print(f"  {'Atomicity':<30} {'Guaranteed':<20} {'Not guaranteed':<20}")
    print(f"  {'Intermediaries':<30} {'None (1 contract)':<20} {'5-7 (banks, clears)':<20}")
    if trad_failed:
        print(f"  {'Traditional Failures':<30} {'N/A':<20} {len(trad_failed):<20}")
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
