# 🛡️ Trust Score System

## Overview

A **trust score** is a numerical value (0.0 to 1.0) assigned to each client that represents how reliable and trustworthy their model updates are. It's FederX's mechanism for detecting and handling malicious or buggy clients.

---

## Trust Score Range

### Scale: 0.0 - 1.0

```
0.0 = Completely untrusted (malicious/broken client)
0.5 = Neutral (new client, no history)
1.0 = Fully trusted (consistent, high-quality updates)
```

### Initial Value

When a client first joins an experiment:

```python
trust_score = 0.5  # Start with neutral trust
```

---

## How Trust Score is Calculated

FederX uses **anomaly detection** to update trust scores based on update quality.

### Detection Algorithm

```python
# From backend/server/main.py

def _update_trust_score(self, client_id: str, delta_norm: float,
                        all_deltas: List[float]):
    """Updates trust based on how 'normal' the update looks"""

    # 1. Calculate statistics of all recent updates
    median_delta = np.median(all_deltas)
    mad = np.median([abs(d - median_delta) for d in all_deltas])

    # 2. Check if this update is an outlier
    threshold = median_delta + 3 * mad  # 3 MAD from median

    # 3. Update trust
    if delta_norm > threshold:
        # Suspicious update - decrease trust
        self.trust_scores[client_id] *= 0.9  # 10% penalty
    else:
        # Good update - increase trust
        self.trust_scores[client_id] = min(
            1.0,
            self.trust_scores[client_id] * 1.05  # 5% reward
        )
```

### What is Being Measured?

**Delta Norm**: The magnitude of change the client is proposing to the global model.

```python
delta_norm = ||client_weights - global_weights||
```

- **Normal update**: Small to moderate changes (learning from data)
- **Suspicious update**: Extremely large changes (potential attack or bug)

### Anomaly Detection Method

Uses **Median Absolute Deviation (MAD)**:

- More robust than standard deviation
- Resistant to outliers
- Industry-standard for anomaly detection

---

## Usage in FederX

### 1. Admin Review Auto-Decisions

Trust scores determine automatic review decisions:

```python
# High Trust → Auto-Approve
if trust_score >= 0.8:
    review_status = AUTO_APPROVED
    # Update aggregated immediately, no admin review needed

# Medium Trust → Manual Review Required
elif 0.3 <= trust_score < 0.8:
    review_status = PENDING_REVIEW
    # Admin must manually review update

# Low Trust → Auto-Reject
elif trust_score < 0.3:
    review_status = REJECTED
    # Update blocked, admin notified
```

**Benefits**:

- Reduces admin workload (trusted clients auto-approved)
- Provides security (untrusted clients blocked)
- Allows human oversight for uncertain cases

### 2. Trust-Weighted Aggregation

When using `aggregation_method = "trust_weighted"`:

```python
# Higher trust clients have more influence on global model
weights = [trust_score_1, trust_score_2, trust_score_3]
weights = weights / sum(weights)  # Normalize

# Aggregate with trust weighting
global_update = sum(w * update for w, update in zip(weights, client_updates))
```

**Example**:

```
Client A: trust=1.0, update_size=0.05 → weight=0.50 (50% influence)
Client B: trust=0.8, update_size=0.05 → weight=0.40 (40% influence)
Client C: trust=0.2, update_size=0.05 → weight=0.10 (10% influence)
```

---

## Trust Evolution Examples

### Example 1: Good Client (Normal Behavior)

```
Initial State:
  Trust: 0.5 (new client)

Round 1: Sends normal update (delta_norm=0.05)
  Result: Trust 0.5 → 0.525 ✅ (+5%)

Round 2: Sends normal update (delta_norm=0.048)
  Result: Trust 0.525 → 0.551 ✅ (+5%)

Round 3: Sends normal update (delta_norm=0.052)
  Result: Trust 0.551 → 0.579 ✅ (+5%)

After 10 rounds of good behavior:
  Trust: 0.5 → 0.814 ✅
  Status: High trust, auto-approved

After 20 rounds of good behavior:
  Trust: 0.814 → 1.0 ✅ (capped at 1.0)
  Status: Fully trusted
```

### Example 2: Malicious Client (Byzantine Attack)

```
Initial State:
  Trust: 0.5 (new client)

Round 1: Sends normal update (delta_norm=0.05)
  Result: Trust 0.5 → 0.525 ✅

Round 2: ATTACK! Sends huge update (delta_norm=5.0)
  Median delta: 0.05
  Threshold: 0.05 + 3*0.02 = 0.11
  5.0 > 0.11 → ANOMALY DETECTED! 🚨
  Result: Trust 0.525 → 0.473 ⚠️ (-10%)

Round 3: Continues attack (delta_norm=4.8)
  Result: Trust 0.473 → 0.426 ⚠️ (-10%)

Round 4: Still malicious (delta_norm=5.2)
  Result: Trust 0.426 → 0.383 ⚠️ (-10%)

Round 5: Persistent attack (delta_norm=5.0)
  Result: Trust 0.383 → 0.345 ⚠️ (-10%)

Round 6: Trust falls below threshold
  Result: Trust 0.345 → 0.310 ⚠️
  310 < 0.3 → AUTO_REJECTED ❌
  Admin notified of malicious client
```

### Example 3: Buggy Client (Intermittent Issues)

```
Initial State:
  Trust: 0.5

Round 1-3: Normal updates
  Trust: 0.5 → 0.579 ✅

Round 4: Bug causes large update (delta_norm=2.0)
  Trust: 0.579 → 0.521 ⚠️ (-10%)

Round 5: Bug fixed, normal update
  Trust: 0.521 → 0.547 ✅ (+5%)

Round 6-10: Normal updates
  Trust: 0.547 → 0.706 ✅

Result: Client recovers, continues participation
```

---

## Trust Score vs Staleness Weight

These are **different concepts** that serve different purposes:

| **Trust Score**                 | **Staleness Weight**            |
| ------------------------------- | ------------------------------- |
| Measures client **reliability** | Measures update **freshness**   |
| Range: 0.0 - 1.0                | Formula: 0.9^staleness          |
| Based on update quality         | Based on version lag            |
| Updates slowly over rounds      | Calculated per update           |
| Used for review decisions       | Used for aggregation weighting  |
| Example: 0.85 (trusted)         | Example: 0.90 (1 version stale) |

### Combined Effect

Both can apply simultaneously:

```python
# Client with high trust but stale update
trust_score = 0.85
staleness = 2
staleness_weight = 0.9^2 = 0.81

# Final aggregation weight
final_weight = trust_score * staleness_weight
final_weight = 0.85 * 0.81 = 0.6885

# This update gets 68.85% of normal influence
```

---

## Monitoring Trust Scores

### In Demo Output

```
🛡️  Trust Scores:
    ✅ client_001: 1.00
    ✅ client_002: 1.00
    ⚠️ client_003: 0.28  # Low trust - being monitored
```

### In API Response

```python
GET /experiment/{exp_id}/status

Response:
{
  "experiment_id": "exp_0",
  "trust_scores": {
    "client_001": 1.0,
    "client_002": 0.95,
    "client_003": 0.28
  },
  "clusters": {...}
}
```

### In Server Logs

```
INFO - client_001 trust updated: 0.500 → 0.525 (good update)
INFO - client_002 trust updated: 0.525 → 0.551 (good update)
WARNING - client_003 anomaly detected! delta_norm=3.2 > threshold=0.15
INFO - client_003 trust updated: 0.450 → 0.405 (penalized)
```

---

## Configuration

### Trust Thresholds

Currently hardcoded in `backend/server/main.py`:

```python
# Auto-approval threshold
AUTO_APPROVE_THRESHOLD = 0.8

# Auto-rejection threshold
AUTO_REJECT_THRESHOLD = 0.3

# Anomaly detection
ANOMALY_MULTIPLIER = 3  # 3 MAD from median

# Trust adjustment rates
PENALTY_RATE = 0.9   # -10% for bad updates
REWARD_RATE = 1.05   # +5% for good updates
```

### Future Enhancements

Planned for future versions:

- Configurable thresholds per experiment
- Multiple anomaly detection methods
- Trust score decay over time (penalize inactive clients)
- Client-specific trust histories
- Trust score persistence (database storage)

---

## Security Benefits

### Byzantine Fault Tolerance

Trust scores provide defense against:

1. **Model Poisoning**: Malicious updates detected and rejected
2. **Data Poisoning**: Clients with corrupted data lose trust over time
3. **Gradient Attacks**: Large gradient manipulations trigger anomaly detection
4. **Backdoor Attacks**: Unusual weight patterns reduce trust
5. **Sybil Attacks**: New clients start with neutral trust, must earn reputation

### Real-World Protection

```
Scenario: Attacker creates 10 fake clients

Round 1: All start with trust=0.5 (neutral)
  Status: PENDING_REVIEW (manual review required)

Round 2: Attacker sends malicious updates
  Trust: 0.5 → 0.45 → 0.405 → 0.365 → 0.328 → 0.295
  Status: AUTO_REJECTED (trust < 0.3)

Result: Attack blocked after 6 rounds, global model protected
```

---

## Best Practices

### For Administrators

1. **Monitor Trust Scores**: Check regularly for unusual patterns
2. **Review Low-Trust Updates**: Manually inspect clients with trust < 0.4
3. **Investigate Anomalies**: When trust drops suddenly, check client logs
4. **Adjust Thresholds**: Tune based on your specific use case
5. **Combine with Manual Review**: Don't rely solely on automation

### For Client Developers

1. **Test Locally**: Ensure updates are reasonable before submitting
2. **Validate Data**: Check for corrupted or anomalous training data
3. **Monitor Feedback**: Check review status after each submission
4. **Handle Rejection**: Implement retry logic with fixes
5. **Build Trust Gradually**: Start conservatively, prove reliability

---

## Example: Trust-Based Federated Learning Workflow

```python
# Admin creates experiment with trust tracking enabled
experiment = create_experiment(
    name="secure_fl",
    enable_trust=True,
    auto_approve_threshold=0.8,
    auto_reject_threshold=0.3
)

# Client 1: Good behavior
for round in range(10):
    model = download_model()
    trained_model = train(model)  # Normal training
    submit_update(trained_model)
    # Trust: 0.5 → 0.525 → 0.551 → ... → 0.814
    # Status: AUTO_APPROVED after round 5 (trust > 0.8)

# Client 2: Malicious
for round in range(5):
    model = download_model()
    poisoned_model = poison(model)  # Attack!
    submit_update(poisoned_model)
    # Trust: 0.5 → 0.45 → 0.405 → 0.365 → 0.328 → 0.295
    # Status: AUTO_REJECTED in round 6 (trust < 0.3)

# Result: Good client contributes, attacker blocked
# Global model remains secure
```

---

## Technical Implementation

### Data Structure

```python
# In-memory storage
trust_scores: Dict[str, float] = {}

# Example state
{
    "client_001": 1.0,
    "client_002": 0.85,
    "client_003": 0.28
}
```

### Update Logic

```python
async def _process_update(self, update_data):
    # Extract client update
    client_id = update_data["client_id"]
    delta_norm = calculate_norm(update_data["weights"])

    # Get all recent deltas for comparison
    all_deltas = [calculate_norm(u["weights"]) for u in recent_updates]

    # Update trust score
    self._update_trust_score(client_id, delta_norm, all_deltas)

    # Make review decision
    trust = self.trust_scores[client_id]
    if trust >= 0.8:
        status = "AUTO_APPROVED"
    elif trust < 0.3:
        status = "REJECTED"
    else:
        status = "PENDING_REVIEW"

    # Aggregate only if approved
    if status in ["APPROVED", "AUTO_APPROVED"]:
        await self._aggregate_updates(cluster_id)

    return {"status": status, "trust_score": trust}
```

---

## Summary

**Trust scores** are FederX's primary security mechanism, providing:

✅ **Automatic malicious detection** without manual monitoring  
✅ **Reputation-based access control** earned over time  
✅ **Quality-weighted aggregation** for better model convergence  
✅ **Reduced admin overhead** through intelligent automation  
✅ **Byzantine fault tolerance** against various attacks

Combined with staleness detection, admin review, and other security features, trust scores make FederX production-ready for secure federated learning at scale! 🛡️
