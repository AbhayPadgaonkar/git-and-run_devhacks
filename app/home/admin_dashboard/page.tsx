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
  Activity
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";

const statusIcon = (status: string) => {
  if (status === "active")
    return <Circle className="w-2 h-2 fill-emerald-500 text-emerald-500 animate-pulse" />;
  if (status === "paused")
    return <Pause className="w-2.5 h-2.5 text-amber-500" />;
  return <CheckCircle2 className="w-2.5 h-2.5 text-muted-foreground" />;
};

export default function AdminDashboard() {
  // Assuming mockProjects has at least one item, otherwise default to a fallback
  const [selectedProject, setSelectedProject] = useState(mockProjects?.[0] || { name: "Default Project", status: "active" });

  return (
    // 1. STRICT THEME WRAPPER: Matches global.css exactly
    <div className="relative min-h-screen bg-background text-foreground overflow-hidden selection:bg-primary/20 selection:text-primary">
      
      {/* ========================================================= */}
      {/* 2. ENTERPRISE GRID & GLOWS (Bulletproof Background)       */}
      {/* ========================================================= */}
      <div className="fixed inset-0 z-0 pointer-events-none flex justify-center">
         {/* Continuous Architectural Grid */}
         <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808025_1px,transparent_1px),linear-gradient(to_bottom,#80808025_1px,transparent_1px)] bg-[size:40px_40px]" />
         
         {/* Top Primary Glow */}
         <div className="absolute top-[-10%] w-[80vw] h-[50vh] bg-primary/20 blur-[120px] rounded-[100%] mix-blend-normal" />
         
         {/* Bottom Primary Glow */}
         <div className="absolute bottom-[-10%] w-[80vw] h-[50vh] bg-primary/10 blur-[150px] rounded-[100%] mix-blend-normal" />
      </div>

      {/* ========================================================= */}
      {/* 3. MAIN CONTENT WRAPPER (z-10 sits above the grid)        */}
      {/* ========================================================= */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        {/* DASHBOARD HEADER & PROJECT SELECTOR */}
        <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-border/50 pb-6">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-foreground flex items-center gap-3">
              <Activity className="h-8 w-8 text-primary" />
              Control Plane
            </h1>
            <p className="text-muted-foreground text-sm mt-1">
              Supervise federated training tasks and edge node telemetry.
            </p>
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" className="bg-card/50 backdrop-blur-md border-border shadow-sm hover:bg-muted/50 transition-colors h-10 px-4">
                <FolderOpen className="mr-2 h-4 w-4 text-primary" />
                {selectedProject?.name || "Select Project"}
                <ChevronDown className="ml-2 h-4 w-4 text-muted-foreground" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-64 bg-card/90 backdrop-blur-xl border-border">
              <DropdownMenuLabel className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Active Workspaces</DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-border/50" />
              {mockProjects?.map((p: any) => (
                <DropdownMenuItem 
                  key={p.id} 
                  onClick={() => setSelectedProject(p)}
                  className="cursor-pointer focus:bg-primary/10 focus:text-primary transition-colors"
                >
                  <div className="flex items-center w-full">
                    {statusIcon(p.status)} 
                    <span className="ml-3 font-medium">{p.name}</span>
                  </div>
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </header>

        {/* STATS BAR */}
        <div className="w-full">
          <StatsBar />
        </div>

        {/* ACTIVE TASKS GRID */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-widest flex items-center gap-2">
              <Radio className="h-3 w-3 text-primary animate-pulse" />
              Active Training Tasks
            </h2>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {mockTasks.map((task, i) => (
              <TaskCard key={task.id} task={task} index={i} />
            ))}
          </div>
        </section>

        {/* CHARTS & PANELS */}
        <section className="space-y-6">
          <ConvergenceChart data={mockConvergence} />
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
             <div className="lg:col-span-2">
               <ClientNodesPanel clients={mockClients} />
             </div>
             <div className="lg:col-span-1">
               <BlockchainPanel records={mockBlockchainRecords} />
             </div>
          </div>
          
          <PrivacyBanner />
        </section>

      </main>
    </div>
  );
}