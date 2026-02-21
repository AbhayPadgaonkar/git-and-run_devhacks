export interface ClientNode {
  id: string;
  name: string;
  organization: string;
  status: "active" | "delayed" | "suspicious" | "blocked";
  trustScore: number;
  lastUpdate: string;
  updatesSubmitted: number;
  dataPoints: number;
  hashVerified: boolean;
  latency: number;
}

export interface TrainingTask {
  id: string;
  modelName: string;
  description: string;
  accuracy: number;
  loss: number;
  aggregationMethod: string;
  round: number;
  totalRounds: number;
  status: "running" | "converged" | "paused";
  clientCount: number;
  logs: { timestamp: string; message: string; type: "info" | "warning" | "error" | "success" }[];
}

export interface BlockchainRecord {
  id: string;
  clientName: string;
  hash: string;
  timestamp: string;
  verified: boolean;
  round: number;
  suspicious: boolean;
}

export interface ConvergencePoint {
  round: number;
  loss: number;
  accuracy: number;
  clientUpdates: number;
}

export interface FederatedProject {
  id: string;
  name: string;
  description: string;
  status: "active" | "completed" | "paused";
  tasksCount: number;
  nodesCount: number;
  createdAt: string;
}
