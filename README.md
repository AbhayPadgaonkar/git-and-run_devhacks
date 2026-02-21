# FederX - Federated Learning Platform

> Production-ready federated learning backend with trust-based aggregation, malicious detection, and multi-dataset support.

**Status:** ✅ Production-ready for hackathon deployment  
**Backend:** FastAPI + Python 3.12  
**Testing:** MNIST (99.07% accuracy), CIFAR-10 (69.34% accuracy)  
**Aggregation Methods:** 4 (FedAvg, Median, Trimmed Mean, Trust-Weighted)

---

## 🚀 Quick Start

### Backend Setup (< 5 minutes)

```bash
# 1. Navigate to backend
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start server
python -m app.server.main
```

Server runs at `http://localhost:8000`

### Client Setup (< 2 minutes)

```bash
# 1. Install client SDK
pip install client/federx_client

# 2. Use in your training code
from federx_client import FederXClient
from federx_client.adapters.pytorch import PyTorchAdapter

client = FederXClient(server_url="http://localhost:8000")
adapter = PyTorchAdapter(model)

# Get global weights
weights = client.get_weights()
adapter.set_weights(weights)

# Train locally
train(model, local_data)

# Upload updates
new_weights = adapter.get_weights()
client.update_weights(new_weights, num_samples=len(local_data))
```

---

## 🏗️ Architecture

### High-Level Overview

```
┌─────────────┐      HTTP/REST      ┌──────────────┐
│   Frontend  │ ◄──────────────────► │   Backend    │
│  (Next.js)  │                      │   (FastAPI)  │
└─────────────┘                      └──────┬───────┘
                                            │
                          ┌─────────────────┼─────────────────┐
                          │                 │                 │
                          ▼                 ▼                 ▼
                    ┌──────────┐      ┌──────────┐     ┌──────────┐
                    │ Client 1 │      │ Client 2 │     │ Client N │
                    └──────────┘      └──────────┘     └──────────┘
```

### Data Flow

```
1. Initialize Experiment
   Frontend → POST /experiment/init → Backend
   Backend → Returns experiment_id + initial_weights

2. Client Training Loop (per round)
   Client → GET /weights → Backend (get global model)
   Client → [LOCAL TRAINING] → Client
   Client → POST /update → Backend (upload delta)

3. Aggregation (after all clients update)
   Backend → [AGGREGATE ALL DELTAS] → Backend
   Backend → [TRUST SCORING] → Backend
   Backend → [MALICIOUS DETECTION] → Backend
   Backend → Updates global_weights

4. Next Round or Complete
   If rounds < max_rounds: goto step 2
   Else: Frontend → GET /weights → Final model
```

### Component Breakdown

**Backend (`backend/`)**

- `app/server/main.py` - FastAPI server with 6 REST endpoints
- `app/aggregation/` - 4 aggregation strategies (FedAvg, Median, Trimmed Mean, Trust-Weighted)
- `app/trust/` - Trust scoring (EMA) + malicious detection (3 methods)
- `app/models/` - Model weight serialization/deserialization

**Client SDK (`backend/client/federx_client/`)**

- `client.py` - HTTP client for server communication
- `adapters/pytorch.py` - PyTorch model weight extraction (with memory-safe `.copy()`)

**Frontend (`app/`)**

- Next.js 15 + TypeScript + TailwindCSS
- Dashboard, experiment creation, real-time monitoring

---

## 📡 API Reference

### Base URL

```
http://localhost:8000
```

### 1. POST `/experiment/init` - Initialize Experiment

**Request:**

```json
{
  "experiment_id": "mnist_exp_1",
  "num_clients": 3,
  "aggregation_method": "fedavg"
}
```

**Response:**

```json
{
  "status": "initialized",
  "experiment_id": "mnist_exp_1",
  "num_clients": 3,
  "aggregation_method": "fedavg"
}
```

**Aggregation Options:**

- `"fedavg"` - Weighted average (default, best for IID data)
- `"median"` - Coordinate-wise median (robust to outliers)
- `"trimmed_mean"` - Trimmed average (balanced robustness)
- `"trust_weighted"` - Trust-score weighted (best for Byzantine attacks)

---

### 2. POST `/weights/init` - Set Initial Model Weights

**Request:**

```json
{
  "experiment_id": "mnist_exp_1",
  "weights": {
    "layer1.weight": [0.1, 0.2, ...],
    "layer1.bias": [0.0, 0.0, ...]
  }
}
```

**Response:**

```json
{
  "status": "weights initialized"
}
```

**Usage:** Send initial model architecture weights before clients start training.

---

### 3. GET `/weights?experiment_id={id}` - Get Global Weights

**Request:**

```
GET /weights?experiment_id=mnist_exp_1
```

**Response:**

```json
{
  "layer1.weight": [0.15, 0.22, ...],
  "layer1.bias": [0.01, -0.02, ...]
}
```

**Usage:** Clients fetch latest global model before each training round.

---

### 4. POST `/update` - Upload Client Update

**Request:**

```json
{
  "experiment_id": "mnist_exp_1",
  "client_id": "client_0",
  "weights": {
    "layer1.weight": [0.16, 0.23, ...],
    "layer1.bias": [0.02, -0.01, ...]
  },
  "num_samples": 10000
}
```

**Response:**

```json
{
  "status": "update received",
  "trust_score": 1.0,
  "delta_norm": 23.45
}
```

**Notes:**

- `num_samples` weights the update (more samples = higher weight in FedAvg)
- Server computes delta automatically: `delta = new_weights - global_weights`
- Trust score updated using EMA: `trust = 0.9 * old_trust + 0.1 * (1 - malicious_score)`

---

### 5. POST `/round/complete` - Trigger Aggregation

**Request:**

```json
{
  "experiment_id": "mnist_exp_1"
}
```

**Response:**

```json
{
  "status": "round completed",
  "updates_aggregated": 3,
  "rejected_malicious": 0,
  "global_delta_norm": 21.3
}
```

**Usage:** Call after all clients upload updates to aggregate and advance to next round.

---

### 6. GET `/status?experiment_id={id}` - Get Experiment Status

**Request:**

```
GET /status?experiment_id=mnist_exp_1
```

**Response:**

```json
{
  "experiment_id": "mnist_exp_1",
  "current_round": 2,
  "num_clients": 3,
  "updates_received": 3,
  "aggregation_method": "fedavg",
  "trust_scores": {
    "client_0": 1.0,
    "client_1": 1.0,
    "client_2": 1.0
  }
}
```

---

## 🖥️ Frontend Integration Guide

### Recommended Stack

```
Next.js 15 + TypeScript + TailwindCSS + Recharts (visualization)
```

### API Client Setup

Create `lib/federx-api.ts`:

```typescript
export class FederXAPI {
  private baseURL: string;

  constructor(baseURL = "http://localhost:8000") {
    this.baseURL = baseURL;
  }

  async initExperiment(params: {
    experiment_id: string;
    num_clients: number;
    aggregation_method: "fedavg" | "median" | "trimmed_mean" | "trust_weighted";
  }) {
    const res = await fetch(`${this.baseURL}/experiment/init`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    return res.json();
  }

  async getStatus(experimentId: string) {
    const res = await fetch(
      `${this.baseURL}/status?experiment_id=${experimentId}`,
    );
    return res.json();
  }

  async getWeights(experimentId: string) {
    const res = await fetch(
      `${this.baseURL}/weights?experiment_id=${experimentId}`,
    );
    return res.json();
  }

  async completeRound(experimentId: string) {
    const res = await fetch(`${this.baseURL}/round/complete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ experiment_id: experimentId }),
    });
    return res.json();
  }
}
```

### Example Component: Experiment Dashboard

Create `app/dashboard/page.tsx`:

```typescript
"use client";

import { useState, useEffect } from "react";
import { FederXAPI } from "@/lib/federx-api";

export default function Dashboard() {
  const [experiments, setExperiments] = useState<string[]>([]);
  const [selectedExp, setSelectedExp] = useState<string | null>(null);
  const [status, setStatus] = useState<any>(null);

  const api = new FederXAPI();

  useEffect(() => {
    if (!selectedExp) return;

    const interval = setInterval(async () => {
      const data = await api.getStatus(selectedExp);
      setStatus(data);
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(interval);
  }, [selectedExp]);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Federated Learning Dashboard</h1>

      {status && (
        <div className="grid grid-cols-3 gap-4">
          <div className="p-4 bg-blue-100 rounded">
            <p className="text-sm text-gray-600">Current Round</p>
            <p className="text-2xl font-bold">{status.current_round}</p>
          </div>

          <div className="p-4 bg-green-100 rounded">
            <p className="text-sm text-gray-600">Updates Received</p>
            <p className="text-2xl font-bold">{status.updates_received}/{status.num_clients}</p>
          </div>

          <div className="p-4 bg-purple-100 rounded">
            <p className="text-sm text-gray-600">Aggregation Method</p>
            <p className="text-lg font-semibold uppercase">{status.aggregation_method}</p>
          </div>
        </div>
      )}

      {status?.trust_scores && (
        <div className="mt-6">
          <h2 className="text-xl font-semibold mb-3">Client Trust Scores</h2>
          <div className="space-y-2">
            {Object.entries(status.trust_scores).map(([client, score]) => (
              <div key={client} className="flex items-center gap-3">
                <span className="font-mono">{client}</span>
                <div className="flex-1 bg-gray-200 rounded-full h-4">
                  <div
                    className="bg-green-500 h-4 rounded-full"
                    style={{ width: `${(score as number) * 100}%` }}
                  />
                </div>
                <span className="font-bold">{((score as number) * 100).toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

### Example Component: Create Experiment Form

Create `app/create/page.tsx`:

```typescript
"use client";

import { useState } from "react";
import { FederXAPI } from "@/lib/federx-api";
import { useRouter } from "next/navigation";

export default function CreateExperiment() {
  const router = useRouter();
  const api = new FederXAPI();

  const [formData, setFormData] = useState({
    experiment_id: "",
    num_clients: 3,
    aggregation_method: "fedavg" as const,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    await api.initExperiment(formData);
    router.push(`/dashboard?exp=${formData.experiment_id}`);
  };

  return (
    <div className="max-w-md mx-auto p-8">
      <h1 className="text-2xl font-bold mb-6">Create New Experiment</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">
            Experiment ID
          </label>
          <input
            type="text"
            value={formData.experiment_id}
            onChange={(e) => setFormData({ ...formData, experiment_id: e.target.value })}
            className="w-full px-3 py-2 border rounded"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            Number of Clients
          </label>
          <input
            type="number"
            min="1"
            value={formData.num_clients}
            onChange={(e) => setFormData({ ...formData, num_clients: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border rounded"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            Aggregation Method
          </label>
          <select
            value={formData.aggregation_method}
            onChange={(e) => setFormData({ ...formData, aggregation_method: e.target.value as any })}
            className="w-full px-3 py-2 border rounded"
          >
            <option value="fedavg">FedAvg (Weighted Average)</option>
            <option value="median">Median (Robust)</option>
            <option value="trimmed_mean">Trimmed Mean (Balanced)</option>
            <option value="trust_weighted">Trust-Weighted (Byzantine)</option>
          </select>
        </div>

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded font-semibold hover:bg-blue-700"
        >
          Create Experiment
        </button>
      </form>
    </div>
  );
}
```

---

## 🔄 User Flow (Frontend → Backend → Clients)

### Step 1: Dashboard Landing

**Frontend:** User sees list of experiments, clicks "Create New"

### Step 2: Experiment Configuration

**Frontend:** Form with fields:

- Experiment ID (e.g., "mnist_hackathon_v1")
- Number of clients (e.g., 3)
- Aggregation method (dropdown: FedAvg/Median/Trimmed/Trust)
- Dataset type (MNIST/CIFAR10/Custom)

**Action:** User submits → `POST /experiment/init`

### Step 3: Client Connection

**Backend:** Experiment initialized, waiting for clients

**Frontend:** Shows status panel:

```
Experiment: mnist_hackathon_v1
Status: Waiting for clients (0/3 connected)
```

**Clients:** Start training scripts, connect to server

### Step 4: Training Rounds

**Per Round:**

1. **Clients:** Fetch global weights (`GET /weights`)
2. **Clients:** Train locally on private data
3. **Clients:** Upload updates (`POST /update`)
4. **Backend:** Collects all updates
5. **Frontend/Backend:** Trigger aggregation (`POST /round/complete`)
6. **Backend:** Aggregates, updates trust scores, detects malicious updates
7. **Frontend:** Displays:
   - Round progress (3/10 completed)
   - Trust scores per client (bar chart)
   - Delta norms (line chart showing convergence)
   - Malicious rejections (if any)

### Step 5: Real-Time Monitoring

**Frontend:** Polls `/status` every 2 seconds, updates UI:

- Current round number
- Updates received (3/3)
- Average trust score
- Aggregation method in use

### Step 6: Training Completion

**Backend:** All rounds completed

**Frontend:** Shows completion message:

```
✅ Training Complete!
Final Model Ready
10 rounds completed
3 clients participated
0 malicious updates detected
```

### Step 7: Model Download

**Frontend:** "Download Final Model" button

**Action:** `GET /weights?experiment_id=mnist_hackathon_v1`

**Response:** Final model weights (JSON)

**Frontend:** Converts to downloadable format (JSON file or PyTorch `.pth`)

---

## 🧪 Testing & Validation

### Backend Tests Completed

✅ **MNIST Dataset** (3 clients, 3 rounds)

- Initial accuracy: 8.42%
- Round 1: 98.32%
- Round 2: 99.01%
- Final: **99.07%**
- All clients: Trust score 1.0

✅ **CIFAR-10 Dataset** (3 clients, 3 rounds)

- Initial accuracy: 9.89%
- Round 1: 48.75%
- Round 2: 63.21%
- Final: **69.34%**

✅ **All Aggregation Methods**

- FedAvg: 98.49%
- Median: 98.38%
- Trimmed Mean: 98.38%
- Trust-Weighted: 98.49%

✅ **Malicious Detection**

- Synthetic attack (10× oversized updates): 100% detection
- Trust scores degrade correctly
- Malicious updates rejected

### Run Tests Yourself

```bash
# MNIST workflow test
python test_fl_workflow.py

# CIFAR-10 test
python test_cifar10.py

# Production readiness (all methods)
python test_production_readiness.py
```

---

## 🚀 Production Deployment

### Backend (Cloud Run / Railway / Render)

**Dockerfile:**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
CMD ["uvicorn", "app.server.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Deploy:**

```bash
# Build
docker build -t federx-backend .

# Run locally
docker run -p 8080:8080 federx-backend

# Deploy to Cloud Run
gcloud run deploy federx-backend --source . --platform managed --region us-central1
```

### Frontend (Vercel / Netlify)

**vercel.json:**

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "env": {
    "NEXT_PUBLIC_API_URL": "https://your-backend.run.app"
  }
}
```

**Deploy:**

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### Environment Variables

**Backend (.env):**

```env
PORT=8000
LOG_LEVEL=INFO
TRUST_ALPHA=0.1
MALICIOUS_THRESHOLD_MULTIPLIER=3.0
```

**Frontend (.env.local):**

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🐛 Troubleshooting

### Issue: "All client deltas are zero"

**Cause:** Memory sharing between numpy arrays and torch tensors

**Fix:** Already fixed in `client/federx_client/adapters/pytorch.py` (added `.copy()` and `.clone()`)

**Verify:**

```python
weights = adapter.get_weights()
# Should return independent numpy arrays, not views
```

---

### Issue: "First aggregation fails"

**Cause:** Empty dict `{}` evaluated as falsy

**Fix:** Already fixed in `backend/server/main.py` (use `None` instead of `{}`)

---

### Issue: "Initialization updates rejected as malicious"

**Cause:** Trust system flags server init updates

**Fix:** Already fixed - client IDs starting with `"init_"` or `"server_init"` bypass malicious detection

---

### Issue: "Trust scores don't update"

**Cause:** Trust engine not called after aggregation

**Fix:** Ensure `POST /round/complete` is called after all client updates

---

## 📊 Performance Benchmarks

| Dataset  | Clients | Rounds | Method         | Accuracy | Time  |
| -------- | ------- | ------ | -------------- | -------- | ----- |
| MNIST    | 3       | 3      | FedAvg         | 99.07%   | ~45s  |
| MNIST    | 3       | 3      | Trust-Weighted | 98.49%   | ~48s  |
| CIFAR-10 | 3       | 3      | FedAvg         | 69.34%   | ~120s |

**Hardware:** CPU-only (Intel i7), no GPU

---

## 📚 Additional Resources

- **Production Readiness Report:** See `PRODUCTION_READINESS_REPORT.md` for detailed bug analysis and recommendations
- **Test Scripts:** `test_fl_workflow.py`, `test_cifar10.py`, `test_production_readiness.py`
- **Backend Code:** `backend/app/server/main.py` (FastAPI endpoints)
- **Client SDK:** `backend/client/federx_client/` (PyTorch adapter)

---

## 🎯 Hackathon Checklist

Frontend Implementation:

- [ ] Create experiment creation form
- [ ] Build dashboard with real-time status updates
- [ ] Add trust score visualization (bar/line charts)
- [ ] Implement round progress tracker
- [ ] Add model download functionality
- [ ] Display malicious detection alerts

Backend (Already Done):

- [x] FastAPI server with 6 endpoints
- [x] 4 aggregation methods
- [x] Trust scoring system
- [x] Malicious detection (3 methods)
- [x] MNIST & CIFAR-10 testing
- [x] Production validation

Integration:

- [ ] Connect frontend to backend API
- [ ] Test end-to-end flow
- [ ] Add error handling & loading states
- [ ] Deploy backend to cloud
- [ ] Deploy frontend to Vercel

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👥 Team

Built for 24-hour hackathon. Backend validated and production-ready.

For questions or issues, check the troubleshooting section or review test scripts.
