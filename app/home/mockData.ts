import type { ClientNode, TrainingTask, BlockchainRecord, ConvergencePoint, FederatedProject } from "@/types/federated";

export const mockProjects: FederatedProject[] = [
  { id: "p1", name: "FinShield", description: "Cross-bank fraud & AML detection", status: "active", tasksCount: 3, nodesCount: 6, createdAt: "2025-11-02" },
  { id: "p2", name: "MedPrivacy", description: "Federated medical imaging diagnostics", status: "active", tasksCount: 2, nodesCount: 4, createdAt: "2025-12-15" },
  { id: "p3", name: "RetailEdge", description: "Privacy-preserving recommendation engine", status: "paused", tasksCount: 1, nodesCount: 3, createdAt: "2026-01-08" },
  { id: "p4", name: "AutoDrive-FL", description: "Autonomous driving sensor fusion", status: "completed", tasksCount: 4, nodesCount: 8, createdAt: "2025-09-20" },
];

export const mockClients: ClientNode[] = [
  { id: "c1", name: "Node Alpha", organization: "Bank A — JPMorgan", status: "active", trustScore: 0.97, lastUpdate: "12s ago", updatesSubmitted: 342, dataPoints: 125000, hashVerified: true, latency: 45 },
  { id: "c2", name: "Node Beta", organization: "Bank B — Goldman Sachs", status: "active", trustScore: 0.94, lastUpdate: "28s ago", updatesSubmitted: 338, dataPoints: 98000, hashVerified: true, latency: 62 },
  { id: "c3", name: "Node Gamma", organization: "Insurance C — Allianz", status: "delayed", trustScore: 0.81, lastUpdate: "4m ago", updatesSubmitted: 290, dataPoints: 76000, hashVerified: true, latency: 230 },
  { id: "c4", name: "Node Delta", organization: "Bank D — HSBC", status: "suspicious", trustScore: 0.42, lastUpdate: "1m ago", updatesSubmitted: 315, dataPoints: 110000, hashVerified: false, latency: 180 },
  { id: "c5", name: "Node Epsilon", organization: "Fintech E — Stripe", status: "active", trustScore: 0.91, lastUpdate: "8s ago", updatesSubmitted: 340, dataPoints: 145000, hashVerified: true, latency: 38 },
  { id: "c6", name: "Node Zeta", organization: "Bank F — Deutsche Bank", status: "blocked", trustScore: 0.15, lastUpdate: "12m ago", updatesSubmitted: 102, dataPoints: 50000, hashVerified: false, latency: 0 },
];

export const mockTasks: TrainingTask[] = [
  {
    id: "t1", modelName: "FraudNet-CNN", description: "Cross-institutional fraud detection via CNN", accuracy: 94.7, loss: 0.0831,
    aggregationMethod: "Trimmed Mean", round: 342, totalRounds: 500, status: "running", clientCount: 5,
    logs: [
      { timestamp: "14:32:08", message: "Round 342 aggregation complete — trimmed mean applied", type: "success" },
      { timestamp: "14:31:55", message: "Node Delta weight divergence detected (σ > 3.2)", type: "warning" },
      { timestamp: "14:31:42", message: "Node Alpha submitted update — hash verified ✓", type: "info" },
      { timestamp: "14:31:30", message: "Node Beta submitted update — hash verified ✓", type: "info" },
    ],
  },
  {
    id: "t2", modelName: "AML-Transformer", description: "Anti-money laundering pattern recognition", accuracy: 89.2, loss: 0.1547,
    aggregationMethod: "Krum", round: 178, totalRounds: 400, status: "running", clientCount: 4,
    logs: [
      { timestamp: "14:30:12", message: "Round 178 complete — Krum selection applied", type: "success" },
      { timestamp: "14:29:58", message: "Node Gamma delayed — using stale weights", type: "warning" },
      { timestamp: "14:29:45", message: "Accuracy improved +0.3% over last 10 rounds", type: "info" },
    ],
  },
  {
    id: "t3", modelName: "CreditScore-LSTM", description: "Privacy-preserving credit scoring", accuracy: 91.5, loss: 0.1203,
    aggregationMethod: "Median", round: 256, totalRounds: 300, status: "running", clientCount: 5,
    logs: [
      { timestamp: "14:28:33", message: "Round 256 — approaching convergence threshold", type: "success" },
      { timestamp: "14:28:20", message: "Node Zeta blocked — repeated hash failures", type: "error" },
    ],
  },
];

export const mockBlockchainRecords: BlockchainRecord[] = [
  { id: "b1", clientName: "Node Alpha", hash: "0xa3f8c91d...7e2b", timestamp: "14:32:05", verified: true, round: 342, suspicious: false },
  { id: "b2", clientName: "Node Beta", hash: "0x7b2e45f1...9c3a", timestamp: "14:31:52", verified: true, round: 342, suspicious: false },
  { id: "b3", clientName: "Node Delta", hash: "0xd4c1a8e3...1f7d", timestamp: "14:31:40", verified: false, round: 342, suspicious: true },
  { id: "b4", clientName: "Node Epsilon", hash: "0x92f7b3d6...4a8c", timestamp: "14:31:28", verified: true, round: 342, suspicious: false },
  { id: "b5", clientName: "Node Alpha", hash: "0x6e9d2c4f...8b1a", timestamp: "14:30:15", verified: true, round: 341, suspicious: false },
  { id: "b6", clientName: "Node Zeta", hash: "0xf1a5d873...2e9c", timestamp: "14:28:10", verified: false, round: 340, suspicious: true },
  { id: "b7", clientName: "Node Gamma", hash: "0x83c4f2a1...5d7e", timestamp: "14:27:55", verified: true, round: 340, suspicious: false },
  { id: "b8", clientName: "Node Beta", hash: "0x4d8e1b9c...a3f6", timestamp: "14:27:40", verified: true, round: 340, suspicious: false },
];

export const mockConvergence: ConvergencePoint[] = Array.from({ length: 35 }, (_, i) => {
  const round = (i + 1) * 10;
  const baseLoss = 2.5 * Math.exp(-0.008 * round) + 0.08;
  const noise = (Math.random() - 0.5) * 0.04;
  return {
    round,
    loss: parseFloat((baseLoss + noise).toFixed(4)),
    accuracy: parseFloat((100 - (baseLoss + noise) * 30 + Math.random() * 2).toFixed(1)),
    clientUpdates: Math.floor(3 + Math.random() * 3),
  };
});
