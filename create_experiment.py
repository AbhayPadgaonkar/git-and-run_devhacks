"""Create a new federated learning experiment"""
import requests
import sys

SERVER_URL = "http://localhost:8000"


def create_experiment(
    name: str,
    aggregation_method: str = "fedavg",
    enable_trust: bool = True,
    enable_clustering: bool = False
):
    """Create new experiment on server"""
    
    url = f"{SERVER_URL}/experiment/create"
    
    config = {
        "name": name,
        "aggregation_method": aggregation_method,
        "enable_trust": enable_trust,
        "enable_clustering": enable_clustering
    }
    
    print(f"Creating experiment: {name}")
    print(f"Config: {config}")
    
    response = requests.post(url, json=config)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Experiment created successfully!")
        print(f"Experiment ID: {data['experiment_id']}")
        print(f"Status: {data['status']}")
        return data['experiment_id']
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        exp_name = sys.argv[1]
    else:
        exp_name = "MNIST Federated Learning"
    
    aggregation = sys.argv[2] if len(sys.argv) > 2 else "median"
    
    exp_id = create_experiment(
        name=exp_name,
        aggregation_method=aggregation,
        enable_trust=True,
        enable_clustering=False
    )
    
    if exp_id:
        print(f"\nYou can now run clients with:")
        print(f"  python client/examples/mnist_iid.py")
        print(f"\nCheck status with:")
        print(f"  curl http://localhost:8000/experiment/{exp_id}/status")
