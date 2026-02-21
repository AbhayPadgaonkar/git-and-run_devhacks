# 🎯 FederX API Guide for Frontend Integration

**Base URL:** `http://localhost:8000`  
**Version:** v1.2 (Async Aggregation Enabled)  
**Status:** ✅ Production-Ready

---

## Quick Start

```javascript
// 1. Create experiment
const exp = await fetch("http://localhost:8000/experiment/create", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    name: "My FL Experiment",
    aggregation_method: "fedavg",
    enable_trust: true,
  }),
});
const { experiment_id } = await exp.json();

// 2. Submit client update (global model updates automatically!)
const update = await fetch(
  `http://localhost:8000/experiment/${experiment_id}/submit-update`,
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      client_id: "client_0",
      delta_weights: "gASV...", // Base64 encoded
      model_version: 0,
    }),
  },
);
const result = await update.json();
console.log(`✅ Global model updated to v${result.new_global_version}`);

// 3. Monitor experiment status
const status = await fetch(
  `http://localhost:8000/experiment/${experiment_id}/status`,
);
const data = await status.json();
console.log(
  `Total updates: ${data.total_updates}, Accepted: ${data.accepted_updates}`,
);
```

---

## Complete API Reference

### 1️⃣ Health & Status

#### `GET /health`

Check if server is running.

**Response:**

```json
{
  "status": "healthy"
}
```

**Frontend Use:**

```javascript
const checkHealth = async () => {
  try {
    const res = await fetch("http://localhost:8000/health");
    return res.status === 200;
  } catch {
    return false;
  }
};
```

---

#### `GET /`

Get server info & active experiment count.

**Response:**

```json
{
  "service": "FederX Federated Learning Server",
  "status": "running",
  "experiments": 5
}
```

**Frontend Use:**

```javascript
const Dashboard = () => {
  const [server, setServer] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/")
      .then((r) => r.json())
      .then(setServer);
  }, []);

  return <h1>Active Experiments: {server?.experiments}</h1>;
};
```

---

### 2️⃣ Experiment Management

#### `POST /experiment/create`

Create a new federated learning experiment.

**Request Body:**

```typescript
{
  name: string;                           // Required
  aggregation_method: "fedavg" | "median" | "trimmed_mean" | "trust_weighted";  // Default: "fedavg"
  enable_trust: boolean;                  // Default: true
  enable_clustering: boolean;             // Default: false
  trust_alpha?: number;                   // Optional, 0.0-1.0, default: 0.8
  cluster_similarity_threshold?: number;  // Optional, 0.0-1.0, default: 0.7
  initial_weights?: string;               // Optional, base64 encoded model weights
}
```

**Response:**

```json
{
  "experiment_id": "exp_0",
  "status": "created",
  "config": {
    "name": "My FL Experiment",
    "aggregation_method": "fedavg",
    "enable_trust": true,
    "enable_clustering": false,
    "trust_alpha": 0.8,
    "cluster_similarity_threshold": 0.7,
    "initial_weights": null
  }
}
```

**Frontend Component:**

```javascript
const CreateExperimentForm = () => {
  const [formData, setFormData] = useState({
    name: "",
    aggregation_method: "fedavg",
    enable_trust: true,
    enable_clustering: false,
  });

  const handleSubmit = async (e) => {
    e.preventDefault();

    const response = await fetch("http://localhost:8000/experiment/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });

    const result = await response.json();

    // Redirect to experiment page
    navigate(`/experiments/${result.experiment_id}`);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        placeholder="Experiment Name"
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
      />

      <select
        value={formData.aggregation_method}
        onChange={(e) =>
          setFormData({ ...formData, aggregation_method: e.target.value })
        }
      >
        <option value="fedavg">FedAvg (Standard)</option>
        <option value="median">Median (Robust)</option>
        <option value="trimmed_mean">Trimmed Mean</option>
        <option value="trust_weighted">Trust-Weighted</option>
      </select>

      <label>
        <input
          type="checkbox"
          checked={formData.enable_trust}
          onChange={(e) =>
            setFormData({ ...formData, enable_trust: e.target.checked })
          }
        />
        Enable Malicious Detection
      </label>

      <button type="submit">Create Experiment</button>
    </form>
  );
};
```

---

#### `GET /experiment/{exp_id}/status`

Get comprehensive experiment status.

**Example:** `GET /experiment/exp_0/status`

**Response:**

```json
{
  "id": "exp_0",
  "config": {
    "name": "My FL Experiment",
    "aggregation_method": "trust_weighted",
    "enable_trust": true,
    "enable_clustering": false
  },
  "status": "running",
  "created_at": "2026-02-21T10:30:00",
  "total_updates": 24,
  "accepted_updates": 22,
  "rejected_updates": 2,
  "clusters": {
    "cluster_0": {
      "version": 22,
      "client_count": 4,
      "last_updated": "2026-02-21T10:35:00"
    }
  },
  "pending_updates": 0,
  "trust_scores": {
    "client_0": 0.95,
    "client_1": 0.88,
    "client_2": 0.42,
    "client_3": 0.91
  }
}
```

**Frontend Component:**

```javascript
const ExperimentMonitor = ({ expId }) => {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    // Poll every 3 seconds for real-time updates
    const interval = setInterval(async () => {
      const res = await fetch(
        `http://localhost:8000/experiment/${expId}/status`,
      );
      const data = await res.json();
      setStatus(data);
    }, 3000);

    return () => clearInterval(interval);
  }, [expId]);

  if (!status) return <div>Loading...</div>;

  const acceptanceRate = (
    (status.accepted_updates / status.total_updates) *
    100
  ).toFixed(1);

  return (
    <div className="experiment-monitor">
      <h1>{status.config.name}</h1>
      <div className="stats">
        <StatCard
          label="Global Model Version"
          value={`v${status.clusters.cluster_0.version}`}
        />
        <StatCard label="Total Updates" value={status.total_updates} />
        <StatCard
          label="Accepted"
          value={status.accepted_updates}
          color="green"
        />
        <StatCard
          label="Rejected"
          value={status.rejected_updates}
          color="red"
        />
        <StatCard label="Acceptance Rate" value={`${acceptanceRate}%`} />
      </div>

      <h2>Client Trust Scores</h2>
      <div className="trust-scores">
        {Object.entries(status.trust_scores).map(([client, score]) => (
          <TrustScoreBar
            key={client}
            clientId={client}
            score={score}
            threshold={0.5}
          />
        ))}
      </div>

      <h2>Activity</h2>
      <p>
        Last updated:{" "}
        {new Date(status.clusters.cluster_0.last_updated).toLocaleString()}
      </p>
      <p>Active clients: {status.clusters.cluster_0.client_count}</p>
    </div>
  );
};
```

---

### 3️⃣ Model Operations

#### `GET /experiment/{exp_id}/global-model`

Download current global model weights.

**Query Parameters:**

- `cluster_id` (optional): Cluster ID, default: `"cluster_0"`

**Example:** `GET /experiment/exp_0/global-model?cluster_id=cluster_0`

**Response:**

```json
{
  "version": 22,
  "cluster_id": "cluster_0",
  "weights": "gASVhgIAA...base64_encoded_numpy_dict...",
  "timestamp": "2026-02-21T10:35:00"
}
```

**Frontend Use:**

```javascript
const downloadGlobalModel = async (expId) => {
  const res = await fetch(
    `http://localhost:8000/experiment/${expId}/global-model`,
  );
  const data = await res.json();

  return {
    version: data.version,
    weights: data.weights, // Base64 string
    timestamp: new Date(data.timestamp),
  };
};
```

---

#### `POST /experiment/{exp_id}/submit-update`

Submit client update. **⚡ Triggers immediate aggregation!**

**Request Body:**

```typescript
{
  client_id: string; // Required
  delta_weights: string; // Required - Base64 encoded weight deltas
  model_version: number; // Required - Version client trained from
}
```

**Response (Accepted):**

```json
{
  "update_id": "upd_24",
  "status": "processed",
  "cluster_id": "cluster_0",
  "accepted": true,
  "trust_score": 0.95,
  "message": "Update accepted & aggregated. Global model updated to v23",
  "new_global_version": 23 // ✨ Real-time version after async aggregation
}
```

**Response (Rejected):**

```json
{
  "update_id": "upd_25",
  "status": "processed",
  "cluster_id": "cluster_0",
  "accepted": false,
  "trust_score": 0.38,
  "message": "Rejected: ['magnitude_anomaly', 'direction_anomaly']",
  "new_global_version": null
}
```

**Frontend Component:**

```javascript
const ClientUpdateSubmitter = ({ expId, clientId }) => {
  const [status, setStatus] = useState("idle");
  const [version, setVersion] = useState(null);

  const submitUpdate = async (deltaWeights) => {
    setStatus("submitting");

    try {
      const res = await fetch(
        `http://localhost:8000/experiment/${expId}/submit-update`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            client_id: clientId,
            delta_weights: deltaWeights, // Base64 string
            model_version: version || 0,
          }),
        },
      );

      const result = await res.json();

      if (result.accepted) {
        setStatus("accepted");
        setVersion(result.new_global_version);

        toast.success(
          `✅ Update accepted! Global model updated to v${result.new_global_version}`,
          { duration: 3000 },
        );
      } else {
        setStatus("rejected");
        toast.error(`❌ Update rejected: ${result.message}`);
      }

      return result;
    } catch (error) {
      setStatus("error");
      toast.error(`Error: ${error.message}`);
    }
  };

  return (
    <div>
      <h3>Client: {clientId}</h3>
      <div>Status: {status}</div>
      <div>Current Version: v{version || 0}</div>
      <div>Trust Score: {lastResult?.trust_score}</div>

      <button
        onClick={() => submitUpdate(computeDelta())}
        disabled={status === "submitting"}
      >
        {status === "submitting" ? "Submitting..." : "Submit Update"}
      </button>
    </div>
  );
};
```

---

### 4️⃣ Advanced Operations

#### `POST /experiment/{exp_id}/aggregate` (Optional)

Manually trigger aggregation (rarely needed now with async mode).

**Query Parameters:**

- `cluster_id` (optional): default `"cluster_0"`

**Response:**

```json
{
  "status": "aggregated",
  "cluster_id": "cluster_0",
  "aggregated_updates": 0,
  "new_version": 23
}
```

**Note:** With async aggregation enabled, this endpoint is **not required**. Each update automatically triggers aggregation.

---

## Real-Time Dashboard Example

```javascript
import { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

const RealTimeDashboard = ({ expId }) => {
  const [status, setStatus] = useState(null);
  const [versionHistory, setVersionHistory] = useState([]);

  // Poll every 2 seconds
  useEffect(() => {
    const fetchStatus = async () => {
      const res = await fetch(
        `http://localhost:8000/experiment/${expId}/status`,
      );
      const data = await res.json();
      setStatus(data);

      // Track version history for chart
      setVersionHistory((prev) =>
        [
          ...prev,
          {
            time: new Date().toLocaleTimeString(),
            version: data.clusters.cluster_0.version,
            updates: data.total_updates,
          },
        ].slice(-20),
      ); // Keep last 20 data points
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 2000);

    return () => clearInterval(interval);
  }, [expId]);

  if (!status) return <div>Loading...</div>;

  return (
    <div className="dashboard">
      <header>
        <h1>{status.config.name}</h1>
        <span className="badge">
          {status.status === "running" ? "🟢 Running" : "🔴 Stopped"}
        </span>
      </header>

      <div className="metrics-grid">
        <MetricCard
          title="Global Model Version"
          value={`v${status.clusters.cluster_0.version}`}
          icon="🔄"
        />
        <MetricCard
          title="Total Updates"
          value={status.total_updates}
          icon="📊"
        />
        <MetricCard
          title="Acceptance Rate"
          value={`${((status.accepted_updates / status.total_updates) * 100).toFixed(1)}%`}
          icon="✅"
        />
        <MetricCard
          title="Active Clients"
          value={Object.keys(status.trust_scores).length}
          icon="👥"
        />
      </div>

      <div className="chart-section">
        <h2>Model Evolution</h2>
        <LineChart width={800} height={300} data={versionHistory}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="version" stroke="#8884d8" />
        </LineChart>
      </div>

      <div className="trust-section">
        <h2>Client Trust Scores</h2>
        {Object.entries(status.trust_scores)
          .sort(([, a], [, b]) => b - a)
          .map(([client, score]) => (
            <div key={client} className="trust-row">
              <span className="client-id">{client}</span>
              <div className="progress-bar">
                <div
                  className={`fill ${score < 0.5 ? "danger" : score < 0.8 ? "warning" : "success"}`}
                  style={{ width: `${score * 100}%` }}
                />
              </div>
              <span className="score">{(score * 100).toFixed(0)}%</span>
            </div>
          ))}
      </div>

      <div className="config-section">
        <h2>Configuration</h2>
        <ul>
          <li>Aggregation: {status.config.aggregation_method}</li>
          <li>
            Trust Detection:{" "}
            {status.config.enable_trust ? "✅ Enabled" : "❌ Disabled"}
          </li>
          <li>
            Clustering:{" "}
            {status.config.enable_clustering ? "✅ Enabled" : "❌ Disabled"}
          </li>
        </ul>
      </div>
    </div>
  );
};
```

---

## Best Practices

### 1. Polling Frequency

```javascript
// Good: 2-5 second polling for status
setInterval(fetchStatus, 3000);

// Bad: Too frequent, wastes resources
setInterval(fetchStatus, 100);
```

### 2. Error Handling

```javascript
const safeAPICall = async (url, options) => {
  try {
    const res = await fetch(url, options);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (error) {
    console.error("API Error:", error);
    toast.error("Connection error. Retrying...");
    return null;
  }
};
```

### 3. Real-Time Updates

```javascript
// Use WebSocket-style patterns with polling
const useRealtimeStatus = (expId) => {
  const [data, setData] = useState(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      const status = await fetch(`/experiment/${expId}/status`).then((r) =>
        r.json(),
      );
      setData(status);
    }, 2000);

    return () => clearInterval(interval);
  }, [expId]);

  return data;
};
```

---

## Summary

✅ **7 REST endpoints** - all CORS-enabled  
✅ **Async aggregation** - immediate model updates  
✅ **Real-time monitoring** - poll `/status` every 2-5 seconds  
✅ **Trust scoring** - track reliable vs malicious clients  
✅ **Multi-framework** - PyTorch, TensorFlow, scikit-learn

**Backend is 100% ready for frontend integration!** 🎉

Start building your dashboard with React, Vue, or Next.js!
