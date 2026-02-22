# 📦 Weight Fetching API

## Overview

FederX provides a simple API endpoint to fetch the raw weights from any update. These weights can then be passed to your external hash function for verification.

**FederX's Role**: Store and serve weights  
**Your Hash Function's Role**: Compute hashes and verify integrity

---

## API Endpoint

### **GET** `/experiment/{exp_id}/update/{update_id}/weights`

Fetch complete weight data for a specific update.

#### Request

```http
GET /experiment/exp_0/update/upd_0/weights HTTP/1.1
Host: localhost:8000
```

#### Response

```json
{
  "update_id": "upd_0",
  "client_id": "alice",
  "experiment_id": "exp_0",
  "cluster_id": "cluster_0",
  "weights": "<base64_encoded_pickled_weights>",
  "timestamp": "2026-02-22T10:30:00",
  "base_version": 0,
  "staleness": 0,
  "trust_score": 0.95,
  "review_status": "auto_approved"
}
```

#### Response Fields

| Field           | Type   | Description                            |
| --------------- | ------ | -------------------------------------- |
| `update_id`     | string | Unique identifier for this update      |
| `client_id`     | string | Client who submitted the update        |
| `experiment_id` | string | Experiment identifier                  |
| `cluster_id`    | string | Cluster assignment                     |
| `weights`       | string | Base64 encoded pickled numpy arrays    |
| `timestamp`     | string | When update was submitted (ISO format) |
| `base_version`  | int    | Model version client trained from      |
| `staleness`     | int    | How many versions behind client was    |
| `trust_score`   | float  | Client reliability score (0.0 - 1.0)   |
| `review_status` | string | Admin review result                    |

---

## Usage with External Hash Function

### Step 1: Fetch Weights from FederX

```python
import requests

response = requests.get(
    "http://localhost:8000/experiment/exp_0/update/upd_0/weights"
)

weight_data = response.json()
```

### Step 2: Decode the Weights

```python
import pickle
import base64

# Decode base64
weights_b64 = weight_data["weights"]
weights_pickled = base64.b64decode(weights_b64.encode('utf-8'))

# Unpickle to get numpy arrays
weights = pickle.loads(weights_pickled)

# weights is now a dict of numpy arrays:
# {
#   'layer1.weight': array([[...]]),
#   'layer1.bias': array([...]),
#   ...
# }
```

### Step 3: Pass to Your Hash Function

```python
# Your teammate's hash function
from your_module import compute_hash

# Pass the weights to it
hash_value = compute_hash(weights)

# Now you have the hash to compare/verify
print(f"Hash: {hash_value}")
```

### Complete Example

```python
import requests
import pickle
import base64
from your_module import compute_hash  # Your teammate's function

# 1. Fetch weights
response = requests.get(
    "http://localhost:8000/experiment/exp_0/update/upd_0/weights"
)
weight_data = response.json()

# 2. Decode
weights_pickled = base64.b64decode(weight_data["weights"].encode('utf-8'))
weights = pickle.loads(weights_pickled)

# 3. Hash with your function
hash_value = compute_hash(weights)

# 4. Use the hash
print(f"Update: {weight_data['update_id']}")
print(f"Client: {weight_data['client_id']}")
print(f"Hash: {hash_value}")

# Store hash for verification
stored_hashes[weight_data['update_id']] = hash_value
```

---

## Use Cases

### 1. **Verify Weight Integrity**

Compare hash before and after aggregation:

```python
# Before aggregation
weights_before = fetch_weights("upd_0")
hash_before = compute_hash(weights_before)

# ... aggregation happens ...

# After aggregation
weights_after = fetch_weights("upd_0")
hash_after = compute_hash(weights_after)

# Verify no tampering
assert hash_before == hash_after, "Weights were modified!"
```

### 2. **Compare Client Updates**

```python
# Fetch weights from 3 clients
alice_weights = fetch_and_decode_weights("upd_0")
bob_weights = fetch_and_decode_weights("upd_1")
charlie_weights = fetch_and_decode_weights("upd_2")

# Compute hashes
alice_hash = compute_hash(alice_weights)
bob_hash = compute_hash(bob_weights)
charlie_hash = compute_hash(charlie_weights)

# Check for identical updates (possible collusion)
if alice_hash == bob_hash:
    print("⚠️ Alice and Bob submitted identical weights!")
```

### 3. **Audit Trail**

```python
# Get all updates for an experiment
all_updates = ["upd_0", "upd_1", "upd_2", ...]

audit_log = []
for update_id in all_updates:
    weight_data = fetch_weights(update_id)
    weights = decode_weights(weight_data["weights"])
    hash_value = compute_hash(weights)

    audit_log.append({
        "update_id": update_id,
        "client_id": weight_data["client_id"],
        "timestamp": weight_data["timestamp"],
        "hash": hash_value
    })

# Save audit log
save_audit_log(audit_log)
```

---

## Helper Functions

### Reusable Helper

```python
import requests
import pickle
import base64

def fetch_and_decode_weights(exp_id: str, update_id: str):
    """
    Fetch weights from FederX and decode to numpy arrays

    Args:
        exp_id: Experiment ID
        update_id: Update ID

    Returns:
        Dict of numpy arrays
    """
    # Fetch from API
    response = requests.get(
        f"http://localhost:8000/experiment/{exp_id}/update/{update_id}/weights"
    )

    if response.status_code != 200:
        raise Exception(f"Failed to fetch weights: {response.text}")

    weight_data = response.json()

    # Decode
    weights_pickled = base64.b64decode(weight_data["weights"].encode('utf-8'))
    weights = pickle.loads(weights_pickled)

    return weights, weight_data  # Return both weights and metadata


# Usage
weights, metadata = fetch_and_decode_weights("exp_0", "upd_0")
print(f"Client: {metadata['client_id']}")
print(f"Trust Score: {metadata['trust_score']}")

# Pass to your hash function
hash_value = compute_hash(weights)
```

---

## Integration Pattern

```python
class WeightVerifier:
    """Integrates FederX weight fetching with external hash function"""

    def __init__(self, base_url: str, hash_function):
        self.base_url = base_url
        self.compute_hash = hash_function
        self.hash_registry = {}  # Store hashes

    def fetch_and_hash(self, exp_id: str, update_id: str):
        """Fetch weights and compute hash"""
        # Fetch weights
        url = f"{self.base_url}/experiment/{exp_id}/update/{update_id}/weights"
        response = requests.get(url)
        weight_data = response.json()

        # Decode
        weights = pickle.loads(
            base64.b64decode(weight_data["weights"].encode('utf-8'))
        )

        # Compute hash
        hash_value = self.compute_hash(weights)

        # Store
        self.hash_registry[update_id] = {
            "hash": hash_value,
            "client_id": weight_data["client_id"],
            "timestamp": weight_data["timestamp"],
            "trust_score": weight_data["trust_score"]
        }

        return hash_value

    def verify_update(self, update_id: str, expected_hash: str):
        """Verify an update against expected hash"""
        if update_id not in self.hash_registry:
            raise ValueError(f"Update {update_id} not found")

        actual_hash = self.hash_registry[update_id]["hash"]
        return actual_hash == expected_hash


# Usage
from your_module import your_hash_function

verifier = WeightVerifier(
    base_url="http://localhost:8000",
    hash_function=your_hash_function
)

# Fetch and hash all updates
for update_id in ["upd_0", "upd_1", "upd_2"]:
    hash_value = verifier.fetch_and_hash("exp_0", update_id)
    print(f"{update_id}: {hash_value[:32]}...")

# Later: verify
is_valid = verifier.verify_update("upd_0", expected_hash="abc123...")
```

---

## Error Handling

```python
def safe_fetch_weights(exp_id: str, update_id: str):
    """Fetch weights with error handling"""
    try:
        response = requests.get(
            f"http://localhost:8000/experiment/{exp_id}/update/{update_id}/weights",
            timeout=10
        )

        if response.status_code == 404:
            return None, "Update not found"

        if response.status_code != 200:
            return None, f"Server error: {response.status_code}"

        weight_data = response.json()
        weights = pickle.loads(
            base64.b64decode(weight_data["weights"].encode('utf-8'))
        )

        return weights, weight_data

    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to FederX server"

    except Exception as e:
        return None, f"Error: {str(e)}"


# Usage
weights, result = safe_fetch_weights("exp_0", "upd_0")

if weights is None:
    print(f"Error: {result}")
else:
    print(f"Success! Fetched {len(weights)} layers")
    hash_value = compute_hash(weights)
```

---

## Demo Script

Run the complete demo:

```bash
# Start FederX server
python -m backend.server.main

# In another terminal:
python demo_fetch_weights.py
```

The demo shows:

1. ✅ Clients submit updates to FederX
2. ✅ Admin fetches weights via API
3. ✅ Weights passed to external hash function
4. ✅ Hashes computed successfully
5. ✅ Verification works correctly

---

## Summary

**What FederX Does**:

- ✅ Stores model updates from clients
- ✅ Provides API to fetch raw weights
- ✅ Handles base64 encoding/decoding
- ✅ Tracks metadata (trust score, timestamp, etc.)

**What Your Hash Function Does**:

- 🔐 Receives weights from FederX API
- 🔐 Computes cryptographic hash
- 🔐 Enables verification and comparison
- 🔐 Maintains hash registry

**Clean Separation of Concerns**: FederX handles FL logistics, your hash function handles cryptographic verification. Perfect! 🎯
