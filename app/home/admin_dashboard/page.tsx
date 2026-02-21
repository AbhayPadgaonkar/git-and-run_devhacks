'use client'

import { useState } from "react";
import StatsBar from "../components/StatsBar"
import TaskCard from "../components/TaskCard";
import ClientNodesPanel from "../components/ClientNodesPanel";
import BlockchainPanel from "../components/BlockchainPanel";
import ConvergenceChart from "../components/ConvergenceChart";
import PrivacyBanner from "../components/PrivacyBanner";
import {
  mockClients,
  mockTasks,
  mockBlockchainRecords,
  mockConvergence,
  mockProjects,
} from "../mockData";
import {
  Radio,
  ChevronDown,
  Circle,
  FolderOpen,
  Pause,
  CheckCircle2,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const statusIcon = (status: string) => {
  if (status === "active")
    return <Circle className="w-2 h-2 fill-success text-success" />;
  if (status === "paused")
    return <Pause className="w-2.5 h-2.5 text-warning" />;
  return <CheckCircle2 className="w-2.5 h-2.5 text-muted-foreground" />;
};

export default function AdminDashboard() {
  const [selectedProject, setSelectedProject] = useState(mockProjects[0]);

  return (
    <div className="min-h-screen bg-background bg-grid">
  

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        <StatsBar />

        {/* Task Cards */}
        <div>
          <h2 className="text-sm font-medium text-muted-foreground mb-3 uppercase tracking-wider">
            Active Training Tasks
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {mockTasks.map((task, i) => (
              <TaskCard key={task.id} task={task} index={i} />
            ))}
          </div>
        </div>

        <ConvergenceChart data={mockConvergence} />
        <ClientNodesPanel clients={mockClients} />
        <BlockchainPanel records={mockBlockchainRecords} />
        <PrivacyBanner />
      </main>
    </div>
  );
}
