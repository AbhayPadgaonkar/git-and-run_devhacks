# FederX - Federated Learning System

Complete federated learning system with:

- ✅ Async aggregation (FedAvg, Median, Trimmed Mean, Trust-Weighted)
- ✅ Malicious update detection
- ✅ Trust scoring
- ✅ Multi-task clustering
- ✅ Framework-agnostic (PyTorch support)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Server

```bash
python run_server.py
```

Server will start at `http://localhost:8000`

- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### 3. Create Experiment

```bash
python create_experiment.py "MNIST Test" median
```

This creates an experiment with ID `exp_0`

### 4. Run Clients

Open multiple terminals and run:

```bash
# Terminal 1 - Normal client
cd client/examples
python mnist_iid.py

# Terminal 2 - Another normal client
python mnist_iid.py

# Terminal 3 - Malicious client (to test detection)
python malicious_client.py
```

### 5. Check Status

```bash
curl http://localhost:8000/experiment/exp_0/status
```

## Architecture

```
federx/
├── backend/
│   ├── server/         # FastAPI server
│   ├── aggregation/    # FedAvg, Median, TrimmedMean, TrustWeighted
│   ├── trust/          # Malicious detection & trust scoring
│   ├── clustering/     # Multi-task support
│   └── utils/          # Serialization, logging
├── client/
│   └── federx_client/  # Python client SDK
│       ├── client.py   # FederatedClient class
│       └── adapters/   # PyTorch adapter
└── data/               # Local storage (created automatically)
```

## API Endpoints

### Create Experiment

```bash
POST /experiment/create
{
  "name": "My Experiment",
  "aggregation_method": "median",
  "enable_trust": true,
  "enable_clustering": false
}
```

### Get Global Model

```bash
GET /experiment/{exp_id}/global-model?cluster_id=cluster_0
```

### Submit Update

```bash
POST /experiment/{exp_id}/submit-update
{
  "client_id": "client_1",
  "delta_weights": "<base64_encoded>",
  "model_version": 0
}
```

### Get Status

```bash
GET /experiment/{exp_id}/status
```

## Testing Scenarios

### 1. Normal Federation (IID Data)

```bash
# Run 3-5 normal clients
python client/examples/mnist_iid.py
```

Expected: Model converges, all clients maintain high trust scores

### 2. Malicious Attack Detection

```bash
# Run 3 normal clients + 1 malicious
python client/examples/mnist_iid.py  # x3
python client/examples/malicious_client.py
```

Expected:

- Malicious updates rejected
- Malicious client trust score drops
- Model stays robust

### 3. Different Aggregation Methods

```bash
# FedAvg (vulnerable)
python create_experiment.py "FedAvg Test" fedavg

# Median (robust)
python create_experiment.py "Median Test" median

# Trimmed Mean (robust)
python create_experiment.py "Trimmed Test" trimmed_mean

# Trust-Weighted (adaptive)
python create_experiment.py "Trust Test" trust_weighted
```

## Client SDK Usage

```python
from federx_client import FederatedClient, PyTorchAdapter

# Initialize client
client = FederatedClient(
    server_url="http://localhost:8000",
    experiment_id="exp_0",
    client_id="my_client",
    adapter=PyTorchAdapter()
)

# Training loop
for round in range(10):
    # Fetch global model
    global_weights = client.fetch_global_model()

    # Load into local model
    if global_weights:
        client.adapter.set_weights(model, global_weights)

    # Train locally
    train(model, data_loader)

    # Submit update
    old_weights = client.adapter.get_weights(model_before)
    new_weights = client.adapter.get_weights(model_after)
    delta = {k: new_weights[k] - old_weights[k] for k in new_weights}

    response = client.submit_update(delta)
    print(f"Accepted: {response['accepted']}, Trust: {response['trust_score']}")
```

## Next Steps

- [ ] Test complete backend with multiple clients
- [ ] Integrate Firebase (replace local JSON storage)
- [ ] Build Next.js dashboard
- [ ] Add TensorFlow and Scikit-learn adapters
- [ ] Add blockchain audit layer

## Hackathon Status

✅ **Backend Complete**:

- FastAPI server with all endpoints
- All 4 aggregation methods
- Malicious detection (3 methods)
- Trust scoring
- Clustering for multi-task
- PyTorch client SDK
- Example scripts

Ready for testing! 🚀
