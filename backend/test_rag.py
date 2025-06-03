import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Sample ERC-20 contract
SAMPLE_CONTRACT = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyToken is ERC20, Ownable {
    uint256 public maxSupply;
    uint256 public mintingFee;
    
    event TokensMinted(address indexed to, uint256 amount);
    event MintingFeeUpdated(uint256 newFee);
    
    constructor(
        string memory name,
        string memory symbol,
        uint256 _maxSupply,
        uint256 _mintingFee
    ) ERC20(name, symbol) Ownable(msg.sender) {
        maxSupply = _maxSupply;
        mintingFee = _mintingFee;
    }
    
    function mint(address to, uint256 amount) public payable {
        require(msg.value >= mintingFee, "Insufficient minting fee");
        require(totalSupply() + amount <= maxSupply, "Exceeds max supply");
        
        _mint(to, amount);
        emit TokensMinted(to, amount);
    }
    
    function setMintingFee(uint256 newFee) public onlyOwner {
        mintingFee = newFee;
        emit MintingFeeUpdated(newFee);
    }
    
    function withdraw() public onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }
}
"""

def test_rag_system():
    base_url = "http://localhost:8000"
    
    print("\n=== Testing RAG System ===\n")
    
    # Test 1: Add contract
    print("1. Adding contract to RAG system...")
    print("1")
    try:
        print("2")
        print("3")
        response = requests.post(
            f"{base_url}/rag/add-contract",
            json={
                "contract_text": SAMPLE_CONTRACT,
                "contract_name": "MyToken",
                "contract_address": "0x1234567890123456789012345678901234567890",
                "network": "ethereum"
            }
        )
        print("4")
        response.raise_for_status()
        print("✅ Contract added successfully")
        print(f"Stats: {json.dumps(response.json()['stats'], indent=2)}\n")
    except Exception as e:
        print("5")
        print(f"❌ Error adding contract: {e}")
        return
    
    # Test 2: Query about contract functions
    print("2. Querying about contract functions...")
    try:
        response = requests.post(
            f"{base_url}/rag/query",
            json={"question": "What are the main functions in this contract and what do they do?"}
        )
        response.raise_for_status()
        print("✅ Query successful")
        print("Answer:")
        print(response.json()["answer"])
        print()
    except Exception as e:
        print(f"❌ Error querying contract: {e}")
    
    # Test 3: Query about specific functionality
    print("3. Querying about minting functionality...")
    try:
        response = requests.post(
            f"{base_url}/rag/query",
            json={"question": "How does the minting process work in this contract? What are the requirements?"}
        )
        response.raise_for_status()
        print("✅ Query successful")
        print("Answer:")
        print(response.json()["answer"])
        print()
    except Exception as e:
        print(f"❌ Error querying contract: {e}")
    
    # Test 4: Get system stats
    print("4. Getting system stats...")
    try:
        response = requests.get(f"{base_url}/rag/stats")
        response.raise_for_status()
        print("✅ Stats retrieved successfully")
        print(f"Stats: {json.dumps(response.json()['stats'], indent=2)}\n")
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
    
    # Test 5: Reset collection (optional)
    print("5. Resetting collection...")
    try:
        response = requests.post(f"{base_url}/rag/reset")
        response.raise_for_status()
        print("✅ Collection reset successfully\n")
    except Exception as e:
        print(f"❌ Error resetting collection: {e}")

if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY environment variable not set!")
        print("Please set it using: export ANTHROPIC_API_KEY=your_api_key_here")
        exit(1)
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code != 200:
            print("❌ Backend server is not healthy!")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server!")
        print("Please ensure the FastAPI server is running on http://localhost:8000")
        exit(1)
    
    test_rag_system() 