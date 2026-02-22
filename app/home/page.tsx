"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Activity, Network, Clock, Plus } from "lucide-react";
import { Spinner } from "@/components/ui/spinner";
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ArrowUpRightIcon, FolderClosed as IconFolderCode } from "lucide-react";
import { db } from "@/app/lib/firebase";
import { collection, getDocs, addDoc, Timestamp } from "firebase/firestore";
import { useAuth } from "@/app/context/AuthContext";

type Experiment = {
  id: string;
  name: string;
  description: string;
  modelType: string;
  status: string;
  currentRound: number;
  totalRounds: number;
  currentAccuracy: number;
  currentLoss: number;
  clientsEnrolled: number;
  aggregationMethod: string;
  enableTrust: boolean;
  requireAdminReview: boolean;
  autoApproveThreshold: number;
  minClientsPerRound: number;
  maxStaleness: number;
  targetAccuracy: number;
  createdBy: string;
  createdAt: any;
  lastUpdated: any;
};

export default function ProjectMenu() {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const { user } = useAuth();
  const router = useRouter();

  const [formData, setFormData] = useState({
    name: "",
    description: "",
    modelType: "CNN",
    aggregationMethod: "fedavg",
    totalRounds: 10,
    targetAccuracy: 0.85,
    minClientsPerRound: 2,
    enableTrust: true,
    requireAdminReview: true,
    autoApproveThreshold: 0.8,
    maxStaleness: 5,
  });

  useEffect(() => {
    if (user?.email) {
      fetchExperiments();
    }
  }, [user?.email]);

  const fetchExperiments = async () => {
    try {
      setLoading(true);
      const querySnapshot = await getDocs(collection(db, "experiments"));
      const experimentsData: Experiment[] = [];
      querySnapshot.forEach((docSnap) => {
        const data = docSnap.data() as Experiment;
        // Filter by current user's email
        if (data.createdBy === user?.email) {
          experimentsData.push({ ...data, id: docSnap.id });
        }
      });
      setExperiments(experimentsData);
    } catch (error) {
      console.error("Error fetching experiments:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateExperiment = async () => {
    if (!formData.name.trim()) {
      alert("Please enter a project name");
      return;
    }

    try {
      setCreating(true);
      const now = Timestamp.now();
      const experimentId = `exp_${Date.now()}`;

      const newExperiment = {
        id: experimentId,
        name: formData.name,
        description: formData.description,
        modelType: formData.modelType,
        aggregationMethod: formData.aggregationMethod,
        totalRounds: formData.totalRounds,
        targetAccuracy: formData.targetAccuracy,
        minClientsPerRound: formData.minClientsPerRound,
        enableTrust: formData.enableTrust,
        requireAdminReview: formData.requireAdminReview,
        autoApproveThreshold: formData.autoApproveThreshold,
        maxStaleness: formData.maxStaleness,
        status: "created",
        currentRound: 0,
        currentAccuracy: 0,
        currentLoss: 0,
        clientsEnrolled: 0,
        createdBy: user?.email || "unknown",
        createdAt: now,
        lastUpdated: now,
      };

      await addDoc(collection(db, "experiments"), newExperiment);

      // Reset form and close dialog
      setFormData({
        name: "",
        description: "",
        modelType: "CNN",
        aggregationMethod: "fedavg",
        totalRounds: 10,
        targetAccuracy: 0.85,
        minClientsPerRound: 2,
        enableTrust: true,
        requireAdminReview: true,
        autoApproveThreshold: 0.8,
        maxStaleness: 5,
      });
      setDialogOpen(false);

      // Refresh experiments list
      await fetchExperiments();
    } catch (error) {
      console.error("Error creating experiment:", error);
      alert("Failed to create experiment. Please try again.");
    } finally {
      setCreating(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "training":
      case "running":
        return "bg-blue-100 text-blue-700";
      case "validating":
      case "completed":
        return "bg-violet-100 text-violet-700";
      case "created":
      case "queued":
        return "bg-slate-100 text-slate-700";
      case "paused":
        return "bg-yellow-100 text-yellow-700";
      case "failed":
        return "bg-red-100 text-red-700";
      default:
        return "bg-slate-100 text-slate-700";
    }
  };

  const formatTimestamp = (timestamp: any) => {
    if (!timestamp) return "N/A";
    const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "just now";
    if (diffMins < 60) return `${diffMins} mins ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    return `${diffDays} days ago`;
  };

  if (loading) {
    return (
      <div className="flex flex-col w-full max-w-7xl mt-24 mx-auto space-y-6">
        <div className="flex justify-center items-center min-h-[400px]">
          <Spinner />
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col w-full max-w-7xl mt-24 mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center w-full">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900">
            Ongoing Projects
          </h2>
          <p className="text-slate-500">
            Manage and monitor your active training clusters.
          </p>
        </div>

        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-violet-700 hover:bg-violet-800 text-white">
              <Plus className="mr-2 h-4 w-4" /> New Project
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create New Federated Learning Project</DialogTitle>
              <DialogDescription>
                Configure your federated learning experiment parameters
              </DialogDescription>
            </DialogHeader>

            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="name">Project Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  placeholder="e.g., MNIST Classification"
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="description">Description</Label>
                <Input
                  id="description"
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  placeholder="Brief description of the project"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="modelType">Model Type</Label>
                  <Select
                    value={formData.modelType}
                    onValueChange={(value) =>
                      setFormData({ ...formData, modelType: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="CNN">CNN</SelectItem>
                      <SelectItem value="RNN">RNN</SelectItem>
                      <SelectItem value="LSTM">LSTM</SelectItem>
                      <SelectItem value="Transformer">Transformer</SelectItem>
                      <SelectItem value="MLP">MLP</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="aggregationMethod">Aggregation Method</Label>
                  <Select
                    value={formData.aggregationMethod}
                    onValueChange={(value) =>
                      setFormData({ ...formData, aggregationMethod: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="fedavg">FedAvg</SelectItem>
                      <SelectItem value="median">Median</SelectItem>
                      <SelectItem value="trimmed_mean">Trimmed Mean</SelectItem>
                      <SelectItem value="trust_weighted">
                        Trust Weighted
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="totalRounds">Total Rounds</Label>
                  <Input
                    id="totalRounds"
                    type="number"
                    value={formData.totalRounds}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        totalRounds: parseInt(e.target.value) || 10,
                      })
                    }
                  />
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="minClientsPerRound">Min Clients/Round</Label>
                  <Input
                    id="minClientsPerRound"
                    type="number"
                    value={formData.minClientsPerRound}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        minClientsPerRound: parseInt(e.target.value) || 2,
                      })
                    }
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="targetAccuracy">Target Accuracy</Label>
                  <Input
                    id="targetAccuracy"
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    value={formData.targetAccuracy}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        targetAccuracy: parseFloat(e.target.value) || 0.85,
                      })
                    }
                  />
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="autoApproveThreshold">
                    Auto Approve Threshold
                  </Label>
                  <Input
                    id="autoApproveThreshold"
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    value={formData.autoApproveThreshold}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        autoApproveThreshold: parseFloat(e.target.value) || 0.8,
                      })
                    }
                  />
                </div>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="maxStaleness">Max Staleness (rounds)</Label>
                <Input
                  id="maxStaleness"
                  type="number"
                  value={formData.maxStaleness}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      maxStaleness: parseInt(e.target.value) || 5,
                    })
                  }
                />
              </div>

              <div className="flex gap-4">
                <div className="flex items-center space-x-2">
                  <input
                    id="enableTrust"
                    type="checkbox"
                    checked={formData.enableTrust}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        enableTrust: e.target.checked,
                      })
                    }
                    className="rounded"
                  />
                  <Label htmlFor="enableTrust" className="cursor-pointer">
                    Enable Trust Scoring
                  </Label>
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    id="requireAdminReview"
                    type="checkbox"
                    checked={formData.requireAdminReview}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        requireAdminReview: e.target.checked,
                      })
                    }
                    className="rounded"
                  />
                  <Label
                    htmlFor="requireAdminReview"
                    className="cursor-pointer"
                  >
                    Require Admin Review
                  </Label>
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setDialogOpen(false)}
                disabled={creating}
              >
                Cancel
              </Button>
              <Button
                onClick={handleCreateExperiment}
                disabled={creating}
                className="bg-violet-700 hover:bg-violet-800"
              >
                {creating ? "Creating..." : "Create Project"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full rounded-xl bg-primary/5 p-4">
        {experiments && experiments.length > 0 ? (
          experiments.map((experiment) => (
            <Card
              key={experiment.id}
              className="flex flex-col border-slate-200 shadow-sm hover:shadow-md h-fit transition-shadow cursor-pointer"
              onClick={() => router.push(`/home/${experiment.id}`)}
            >
              <CardHeader className="pb-4">
                <div className="flex justify-between items-start">
                  <div className="space-y-1">
                    <CardTitle className="text-xl text-slate-900">
                      {experiment.name}
                    </CardTitle>
                    <CardDescription className="text-violet-600 font-medium">
                      {experiment.modelType} · {experiment.aggregationMethod}
                    </CardDescription>
                  </div>
                  <Badge
                    variant="secondary"
                    className={getStatusColor(experiment.status)}
                  >
                    <Activity className="mr-1 h-3 w-3" />
                    {experiment.status}
                  </Badge>
                </div>
              </CardHeader>

              <CardContent className="flex-grow space-y-4">
                <p className="text-sm text-slate-600 line-clamp-2">
                  {experiment.description || "No description provided"}
                </p>

                {/* Progress Section */}
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium text-slate-700">
                      Training Progress
                    </span>
                    <span className="text-slate-500">
                      {experiment.currentRound}/{experiment.totalRounds}
                    </span>
                  </div>
                  <Progress
                    value={
                      (experiment.currentRound / experiment.totalRounds) * 100
                    }
                    className="h-2"
                  />
                </div>

                {/* Stats Section */}
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-slate-500">Accuracy:</span>
                    <span className="ml-1 font-medium">
                      {(experiment.currentAccuracy * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500">Loss:</span>
                    <span className="ml-1 font-medium">
                      {experiment.currentLoss.toFixed(4)}
                    </span>
                  </div>
                </div>

                {/* Stats Row */}
                <div className="flex items-center space-x-4 text-sm text-slate-500 pt-2">
                  <div className="flex items-center">
                    <Network className="mr-1 h-4 w-4 text-violet-500" />
                    {experiment.clientsEnrolled} Clients
                  </div>
                  <div className="flex items-center">
                    <Clock className="mr-1 h-4 w-4 text-slate-400" />
                    {formatTimestamp(experiment.lastUpdated)}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <div className="col-span-full w-full flex justify-center items-center">
            <Empty>
              <EmptyHeader>
                <EmptyMedia variant="icon">
                  <IconFolderCode />
                </EmptyMedia>
                <EmptyTitle className="font-semibold text-3xl">
                  No Projects Yet
                </EmptyTitle>
                <EmptyDescription className="w-full text-base">
                  You haven&apos;t created any projects yet. Get started by
                  creating your first federated learning project.
                </EmptyDescription>
              </EmptyHeader>
              <EmptyContent className="flex-row justify-center gap-2">
                <Button
                  onClick={() => setDialogOpen(true)}
                  className="bg-violet-700 hover:bg-violet-800 text-white"
                >
                  <Plus className="mr-2 h-4 w-4" /> Create New Project
                </Button>
              </EmptyContent>
            </Empty>
          </div>
        )}
      </div>
    </div>
  );
}
