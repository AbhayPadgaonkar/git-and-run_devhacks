"""Quick test to verify the server is working"""
import requests
import json

SERVER_URL = "http://localhost:8000"

def test_server():
    print("Testing FederX Server...")
    print("="*60)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{SERVER_URL}/health")
        if response.status_code == 200:
            print("✓ Server is alive!")
            print(f"  Response: {response.json()}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"✗ Cannot connect to server: {e}")
        print("  Make sure to run: python run_server.py")
        return
    
    # Test 2: Create experiment
    print("\n2. Creating experiment...")
    try:
        response = requests.post(
            f"{SERVER_URL}/experiment/create",
            json={
                "name": "Test MNIST Experiment",
                "aggregation_method": "fedavg",
                "enable_trust": True,
                "enable_clustering": False
            }
        )
        if response.status_code == 200:
            data = response.json()
            exp_id = data["experiment_id"]
            print(f"✓ Experiment created: {exp_id}")
            print(f"  Response: {data}")
        else:
            print(f"✗ Create experiment failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return
    except Exception as e:
        print(f"✗ Error: {e}")
        return
    
    # Test 3: Get experiment status
    print("\n3. Getting experiment status...")
    try:
        response = requests.get(f"{SERVER_URL}/experiment/{exp_id}/status")
        if response.status_code == 200:
            print("✓ Got experiment status!")
            print(f"  Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"✗ Get status failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "="*60)
    print("✓ Backend is working! Ready for federated learning.")
    print(f"   Experiment ID: {exp_id}")
    print(f"   API Docs: {SERVER_URL}/docs")
    print("="*60)

if __name__ == "__main__":
    test_server()
