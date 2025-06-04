import requests
import json
import os
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

# Sample knowledge base items
KNOWLEDGE_ITEMS = [
    {
        "content": """Reentrancy attacks are a critical vulnerability in smart contracts where an external contract can call back into the original contract before the first call completes. This can lead to multiple withdrawals or state changes.

Key points:
1. Always use the checks-effects-interactions pattern
2. Consider using ReentrancyGuard from OpenZeppelin
3. Be careful with external calls, especially those that transfer value
4. Update state before making external calls""",
        "category": "vulnerability",
        "pattern_type": "reentrancy",
        "severity": 5,
        "standard": "security",
        "version": "0.8.0",
        "references": [
            "https://swcregistry.io/docs/SWC-107",
            "https://docs.openzeppelin.com/contracts/4.x/api/security#ReentrancyGuard"
        ],
        "code_example": """// Vulnerable code
function withdraw() public {
    uint amount = balances[msg.sender];
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success, "Transfer failed");
    balances[msg.sender] = 0;  // State updated after external call
}

// Secure code
function withdraw() public nonReentrant {
    uint amount = balances[msg.sender];
    balances[msg.sender] = 0;  // State updated before external call
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success, "Transfer failed");
}""",
        "description": "Critical vulnerability that can lead to multiple withdrawals or state changes"
    },
    {
        "content": """Access control is a fundamental security pattern in smart contracts. It ensures that only authorized addresses can perform certain actions.

Best practices:
1. Use OpenZeppelin's Ownable or AccessControl
2. Implement role-based access control for complex permissions
3. Always check permissions before critical operations
4. Consider using multi-signature requirements for admin functions""",
        "category": "security_pattern",
        "pattern_type": "access_control",
        "severity": 4,
        "standard": "security",
        "version": "0.8.0",
        "references": [
            "https://docs.openzeppelin.com/contracts/4.x/api/access",
            "https://swcregistry.io/docs/SWC-105"
        ],
        "code_example": """// Using OpenZeppelin's Ownable
import "@openzeppelin/contracts/access/Ownable.sol";

contract SecureContract is Ownable {
    function adminFunction() public onlyOwner {
        // Only the owner can call this
    }
}

// Using AccessControl
import "@openzeppelin/contracts/access/AccessControl.sol";

contract RoleBasedContract is AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
    }
    
    function adminFunction() public onlyRole(ADMIN_ROLE) {
        // Only addresses with ADMIN_ROLE can call this
    }
}""",
        "description": "Essential security pattern for controlling access to contract functions"
    },
    {
        "content": """ERC-20 is the most widely used token standard on Ethereum. It defines a common interface for fungible tokens.

Key features:
1. Transfer and transferFrom for token movements
2. Approve and allowance for delegated transfers
3. Standard events for transfers and approvals
4. Optional metadata (name, symbol, decimals)""",
        "category": "token_standard",
        "pattern_type": "erc20",
        "severity": 0,
        "standard": "ERC-20",
        "version": "0.8.0",
        "references": [
            "https://eips.ethereum.org/EIPS/eip-20",
            "https://docs.openzeppelin.com/contracts/4.x/api/token/erc20"
        ],
        "code_example": """// Basic ERC-20 implementation
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MyToken is ERC20 {
    constructor(string memory name, string memory symbol) ERC20(name, symbol) {
        _mint(msg.sender, 1000000 * 10 ** decimals());
    }
    
    function mint(address to, uint256 amount) public {
        _mint(to, amount);
    }
}""",
        "description": "Standard interface for fungible tokens on Ethereum"
    }
]

def test_knowledge_base():
    base_url = "http://localhost:8000"
    
    print("\n=== Testing Knowledge Base Integration ===\n")
    
    # Test 1: Reset knowledge base
    print("1. Resetting knowledge base...")
    try:
        response = requests.post(f"{base_url}/rag/knowledge/reset")
        response.raise_for_status()
        print("✅ Knowledge base reset successfully")
    except Exception as e:
        print(f"❌ Error resetting knowledge base: {e}")
        return
    
    # Test 2: Add knowledge items
    print("\n2. Adding knowledge items...")
    for i, item in enumerate(KNOWLEDGE_ITEMS, 1):
        try:
            response = requests.post(
                f"{base_url}/rag/knowledge/add",
                json=item
            )
            if response.status_code != 200:
                print(f"❌ Error adding knowledge item {i}: {response.status_code} - {response.text}")
                return
            print(f"✅ Added knowledge item {i}: {item['category']} - {item['pattern_type']}")
        except Exception as e:
            print(f"❌ Error adding knowledge item {i}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print("Server response:", e.response.text)
            return
    
    # Test 3: Get knowledge base stats
    print("\n3. Getting knowledge base statistics...")
    try:
        response = requests.get(f"{base_url}/rag/knowledge/stats")
        response.raise_for_status()
        stats = response.json()["stats"]
        print("✅ Knowledge base stats:")
        print(f"Total items: {stats['count']}")
        print("Category distribution:")
        for category, count in stats["categories"].items():
            print(f"  - {category}: {count}")
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
    
    # Test 4: Test RAG integration with knowledge base
    print("\n4. Testing RAG integration...")
    test_questions = [
        "What are the best practices for preventing reentrancy attacks?",
        "How should I implement access control in my smart contract?",
        "What are the key features of ERC-20 tokens?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        try:
            print(f"\nQuestion {i}: {question}")
            response = requests.post(
                f"{base_url}/rag/query",
                json={"question": question}
            )
            response.raise_for_status()
            answer = response.json()["answer"]
            print("Answer:")
            print(answer)
            print("✅ Query successful")
        except Exception as e:
            print(f"❌ Error querying: {e}")

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
    
    test_knowledge_base() 