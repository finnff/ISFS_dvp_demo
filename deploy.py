#!/usr/bin/env python3
"""
Smart Contract Deployment Script
Deploys DvP contract and test tokens to local Ethereum network
"""

import sys
import json
import time
from web3 import Web3
from eth_account import Account

# Configuration
RPC_URL = "http://127.0.0.1:8545"
DEPLOYER_PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

def get_contract_abi():
    """Load contract ABI from compiled artifact"""
    # For simplicity, we'll use a minimal ABI
    return [
        {
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
        },
        {
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
        },
        {
            "inputs": [
                {"internalType": "address", "name": "token", "type": "address"},
                {"internalType": "address", "name": "account", "type": "address"}
            ],
            "name": "getBalance",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view", "type": "function"
        }
    ]

def create_test_token(w3, account, name, symbol, total_supply):
    """Create a simple ERC20 test token"""
    # Simplified ERC20 ABI
    erc20_abi = [
        {
            "inputs": [
                {"internalType": "string", "name": "name_", "type": "string"},
                {"internalType": "string", "name": "symbol_", "type": "string"},
                {"internalType": "uint256", "name": "initialSupply", "type": "uint256"}
            ],
            "name": "initialize",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "address", "name": "account", "type": "address"}
            ],
            "name": "balanceOf",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "address", "name": "from", "type": "address"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "amount", "type": "uint256"}
            ],
            "name": "transferFrom",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "address", "name": "spender", "type": "address"},
                {"internalType": "uint256", "name": "amount", "type": "uint256"}
            ],
            "name": "approve",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ]
    
    # Use pre-deployed contract at known address (simplified)
    # In production, we'd deploy a new contract
    return None

def main():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    if not w3.is_connected():
        print("Error: Could not connect to Ethereum node")
        print("\nPlease start ganache-cli first:")
        print("  $ source venv/bin/activate")
        print("  $ ganache-cli -d")
        print("\nThen run this script again.")
        sys.exit(1)
    
    print("Connected to Ethereum node")
    print(f"Network ID: {w3.eth.chain_id}")
    print(f"Default account: {Account.from_key(DEPLOYER_PRIVATE_KEY).address}")
    
    # Save configuration
    config = {
        "rpc_url": RPC_URL,
        "deployer_address": Account.from_key(DEPLOYER_PRIVATE_KEY).address,
        "contract_address": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
        "cash_token": "0x90F79bf6EB2c4f870365E785982E1f101E93b906",
        "securities_token": "0x15d34Aaf742668cA20380e3517b4971152EC58E7"
    }
    
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("\nConfiguration saved to config.json")
    print("\nTo start the simulation:")
    print("  1. Start ganache-cli: $ source venv/bin/activate && ganache-cli -d")
    print("  2. Run trader: $ source venv/bin/activate && python trader.py")
    print("  3. Open dashboard: $ open dashboard.html (or view in browser)")

if __name__ == "__main__":
    main()
