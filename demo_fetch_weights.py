"""
Demo: Fetching Update Weights for External Hashing

This demo shows how FederX provides raw weights that can be passed to
an external hash function (created by your teammate).

Workflow:
1. Clients submit updates to FederX
2. Admin fetches weights using the API
3. Weights are passed to external hash function
4. Hash can be used for verification/comparison

This is a simplified version - FederX just stores and serves weights,
your teammate's hash function handles the cryptographic verification.
"""

import requests
import numpy as np
import pickle
import base64
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'=' * 80}")
    print(f"{title.center(80)}")
    print(f"{'=' * 80}\n")


def print_step(step: str):
    """Print a step"""
    print(f"{Fore.CYAN}▸ {step}{Style.RESET_ALL}")


def print_success(message: str):
    """Print success"""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def create_random_model():
    """Create a random model"""
    return {
        'layer1.weight': np.random.randn(10, 5).astype(np.float32),
        'layer1.bias': np.random.randn(10).astype(np.float32),
        'layer2.weight': np.random.randn(1, 10).astype(np.float32),
        'layer2.bias': np.random.randn(1).astype(np.float32)
    }


def encode_weights(weights):
    """Encode weights to base64"""
    pickled = pickle.dumps(weights)
    return base64.b64encode(pickled).decode('utf-8')


def decode_weights(weights_b64):
    """Decode base64 weights"""
    pickled = base64.b64decode(weights_b64.encode('utf-8'))
    return pickle.loads(pickled)


# ============================================================
# EXTERNAL HASH FUNCTION (Your Teammate's Implementation)
# ============================================================

def external_hash_function(weights):
    """
    This represents your teammate's hash function.
    FederX just provides the weights, this function computes the hash.
    
    Replace this with your actual hash implementation.
    """
    import hashlib
    import json
    
    # Convert numpy arrays to lists for hashing
    weights_serializable = {}
    for key, value in weights.items():
        if isinstance(value, np.ndarray):
            weights_serializable[key] = value.tolist()
        else:
            weights_serializable[key] = value
    
    # Create deterministic JSON
    weights_json = json.dumps(weights_serializable, sort_keys=True)
    
    # Compute SHA-256 hash
    hash_value = hashlib.sha256(weights_json.encode()).hexdigest()
    
    return hash_value


def main():
    print_section("📦 FEDERX: FETCH WEIGHTS FOR EXTERNAL HASHING")
    print(f"{Fore.CYAN}FederX provides weights → Your hash function processes them{Style.RESET_ALL}\n")
    
    # ============ PHASE 1: SETUP ============
    print_section("📋 PHASE 1: Experiment Setup")
    
    print_step("Creating experiment...")
    
    response = requests.post(f"{BASE_URL}/experiment/create", json={
        "name": "weight_fetching_demo",
        "aggregation_method": "fedavg",
        "enable_trust": True,
        "auto_approve_threshold": 0.0  # Auto-approve all
    })
    
    exp_data = response.json()
    exp_id = exp_data["experiment_id"]
    print_success(f"Experiment created: {exp_id}")
    
    # ============ PHASE 2: CLIENT SUBMISSIONS ============
    print_section("📤 PHASE 2: Clients Submit Updates")
    
    clients = ["alice", "bob", "charlie"]
    update_ids = []
    original_weights = {}  # Store for comparison
    
    for client_id in clients:
        print_step(f"{client_id} submitting update...")
        
        # Create model update
        delta_weights = create_random_model()
        original_weights[client_id] = delta_weights
        
        # Submit to server
        response = requests.post(
            f"{BASE_URL}/experiment/{exp_id}/submit-update",
            json={
                "client_id": client_id,
                "delta_weights": encode_weights(delta_weights),
                "model_version": 0
            }
        )
        
        result = response.json()
        update_id = result["update_id"]
        update_ids.append((client_id, update_id))
        
        print_success(f"{client_id} → {update_id} (Status: {result['review_status']})")
    
    # ============ PHASE 3: FETCH WEIGHTS ============
    print_section("🔍 PHASE 3: Admin Fetches Weights from FederX")
    
    fetched_weights = {}
    
    for client_id, update_id in update_ids:
        print_step(f"Fetching weights for {update_id} ({client_id})...")
        
        response = requests.get(
            f"{BASE_URL}/experiment/{exp_id}/update/{update_id}/weights"
        )
        
        if response.status_code == 200:
            weight_data = response.json()
            
            # Decode the weights
            weights = decode_weights(weight_data["weights"])
            fetched_weights[client_id] = weights
            
            print_success(f"Fetched weights from {client_id}")
            print(f"   Update ID: {weight_data['update_id']}")
            print(f"   Client: {weight_data['client_id']}")
            print(f"   Timestamp: {weight_data['timestamp']}")
            print(f"   Trust Score: {weight_data['trust_score']}")
            print(f"   Review Status: {weight_data['review_status']}")
            
            # Show weight structure
            total_params = sum(w.size for w in weights.values())
            print(f"   Total Parameters: {total_params}")
        else:
            print(f"{Fore.RED}✗ Failed to fetch: {response.text}{Style.RESET_ALL}")
    
    # ============ PHASE 4: EXTERNAL HASHING ============
    print_section("🔐 PHASE 4: Pass Weights to External Hash Function")
    
    print(f"{Fore.YELLOW}This is where your teammate's hash function is called{Style.RESET_ALL}\n")
    
    weight_hashes = {}
    
    for client_id in clients:
        print_step(f"Computing hash for {client_id}'s weights...")
        
        # Get the weights (these came from FederX API)
        weights = fetched_weights[client_id]
        
        # Call external hash function (your teammate's code)
        hash_value = external_hash_function(weights)
        weight_hashes[client_id] = hash_value
        
        print_success(f"Hash computed: {hash_value[:32]}...")
    
    # ============ PHASE 5: VERIFICATION ============
    print_section("✅ PHASE 5: Verify Fetched Weights Match Originals")
    
    print_step("Comparing fetched weights with originals...")
    
    all_match = True
    for client_id in clients:
        original = original_weights[client_id]
        fetched = fetched_weights[client_id]
        
        # Compute hashes of both
        original_hash = external_hash_function(original)
        fetched_hash = external_hash_function(fetched)
        
        if original_hash == fetched_hash:
            print_success(f"{client_id}: Weights match ✓")
            print(f"   Original Hash: {original_hash[:32]}...")
            print(f"   Fetched Hash:  {fetched_hash[:32]}...")
        else:
            print(f"{Fore.RED}✗ {client_id}: Weights don't match!{Style.RESET_ALL}")
            all_match = False
    
    if all_match:
        print(f"\n{Fore.GREEN}{'=' * 80}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ ALL WEIGHTS VERIFIED - INTEGRITY CONFIRMED{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'=' * 80}{Style.RESET_ALL}\n")
    
    # ============ SUMMARY ============
    print_section("📊 SUMMARY")
    
    print(f"{Fore.GREEN}✓ FederX stored {len(update_ids)} updates{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ Admin fetched all weights via API{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ External hash function processed weights{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ All hashes computed successfully{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}API Endpoint Used:{Style.RESET_ALL}")
    print(f"  GET /experiment/{{exp_id}}/update/{{update_id}}/weights")
    
    print(f"\n{Fore.CYAN}Response Contains:{Style.RESET_ALL}")
    print(f"  • update_id: Unique identifier")
    print(f"  • client_id: Who submitted")
    print(f"  • weights: Base64 encoded (ready for your hash function)")
    print(f"  • timestamp: When submitted")
    print(f"  • trust_score: Client reliability")
    print(f"  • review_status: Admin review result")
    print(f"  • staleness: Version lag")
    
    print(f"\n{Fore.YELLOW}Integration with Your Teammate's Hash Function:{Style.RESET_ALL}")
    print(f"  1. Fetch weights from FederX API")
    print(f"  2. Decode base64 → get numpy arrays")
    print(f"  3. Pass to your hash function")
    print(f"  4. Use hash for verification/comparison")
    
    print(f"\n{Fore.GREEN}✓ Demo Complete!{Style.RESET_ALL}\n")


if __name__ == "__main__":
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            raise Exception("Server not responding")
        
        main()
    
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}✗ Cannot connect to FederX server!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please start the server first:{Style.RESET_ALL}")
        print(f"  python -m backend.server.main")
    except Exception as e:
        print(f"{Fore.RED}✗ Demo failed: {str(e)}{Style.RESET_ALL}")
