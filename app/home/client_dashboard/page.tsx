"use client";

import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { 
  Activity, CheckCircle2, XCircle, AlertTriangle, 
  History, TrendingUp, ShieldCheck, Cpu,
  Database, Server, RefreshCw
} from "lucide-react";

// Shadcn Chart Imports
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { 
  Area, AreaChart, Bar, BarChart, CartesianGrid, 
  XAxis, YAxis, PieChart, Pie, Cell 
} from "recharts";

// ==========================================
// MOCK DATA (Client Specific Telemetry)
// ==========================================
const clientKPIs = {
  activeTasks: 2,
  localAccuracy: "91.4%",
  acceptanceRate: 94,
  trustScore: 98,
};

const localConvergenceData = [
  { round: "R1", accuracy: 65.2, loss: 0.85 },
  { round: "R2", accuracy: 72.4, loss: 0.68 },
  { round: "R3", accuracy: 78.1, loss: 0.51 },
  { round: "R4", accuracy: 84.5, loss: 0.42 },
  { round: "R5", accuracy: 88.9, loss: 0.31 },
  { round: "R6", accuracy: 90.2, loss: 0.28 },
  { round: "R7", accuracy: 91.4, loss: 0.25 },
];

const acceptanceData = [
  { name: "Accepted", value: 94, color: "var(--color-emerald-500)" },
  { name: "Rejected", value: 4, color: "var(--color-destructive)" },
  { name: "Delayed", value: 2, color: "var(--color-amber-500)" },
];

const trustScoreTrend = [
  { epoch: "E1", score: 85 },
  { epoch: "E2", score: 88 },
  { epoch: "E3", score: 82 }, // Dip due to a rejection
  { epoch: "E4", score: 90 },
  { epoch: "E5", score: 95 },
  { epoch: "E6", score: 98 },
];

const updateLogs = [
  { id: "UPD-104", status: "Accepted", reason: "Valid gradient", round: "R7", time: "2 mins ago" },
  { id: "UPD-103", status: "Accepted", reason: "Valid gradient", round: "R6", time: "15 mins ago" },
  { id: "UPD-102", status: "Rejected", reason: "High Deviation (L2 Norm)", round: "R5", time: "30 mins ago" },
  { id: "UPD-101", status: "Delayed", reason: "Network Latency > 500ms", round: "R4", time: "45 mins ago" },
  { id: "UPD-100", status: "Accepted", reason: "Valid gradient", round: "R3", time: "1 hr ago" },
];

const completedTasks = [
  { id: "TASK-771", name: "Retail Demand Forecasting", type: "LSTM", finalAcc: "89.5%", rounds: 120, status: "Completed" },
  { id: "TASK-652", name: "NLP Sentiment Analysis", type: "Transformer", finalAcc: "94.2%", rounds: 50, status: "Completed" },
  { id: "TASK-503", name: "Edge Vision Model", type: "MobileNetV3", finalAcc: "81.1%", rounds: 35, status: "Aborted" },
];

// Chart Configs
const convergenceConfig = {
  accuracy: { label: "Local Acc", color: "var(--color-primary)" },
  loss: { label: "Local Loss", color: "var(--color-destructive)" },
} satisfies ChartConfig;

const trustConfig = {
  score: { label: "Trust Score", color: "var(--color-primary)" },
} satisfies ChartConfig;

export default function ClientDashboard() {
  return (
    <div className="relative min-h-screen bg-background text-foreground overflow-x-hidden selection:bg-primary/20 selection:text-primary pb-20">
      
      {/* ========================================================= */}
      {/* ENTERPRISE GRID & GLOWS (Background)                      */}
      {/* ========================================================= */}
      <div className="fixed inset-0 z-0 pointer-events-none flex justify-center">
         <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808025_1px,transparent_1px),linear-gradient(to_bottom,#80808025_1px,transparent_1px)] bg-[size:40px_40px]" />
         <div className="absolute top-[-10%] w-[80vw] h-[50vh] bg-primary/15 blur-[120px] rounded-[100%] mix-blend-normal" />
         <div className="absolute bottom-[-10%] right-[-20%] w-[60vw] h-[60vh] bg-emerald-500/10 blur-[150px] rounded-[100%] mix-blend-normal" />
      </div>

      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-8">
        
        {/* ================= HEADER ================= */}
        <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-border/50 pb-6">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20 text-[10px] uppercase">Node Identity Verified</Badge>
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight text-foreground flex items-center gap-3">
              <Cpu className="h-8 w-8 text-primary" />
              Bank A (NY Branch)
            </h1>
            <p className="text-muted-foreground text-sm mt-1">
              Local workspace: Training telemetry, update logs, and node reputation.
            </p>
          </div>

          <div className="flex gap-3">
            <Button variant="outline" className="bg-card/50 backdrop-blur-md border-border shadow-sm hover:bg-muted/50 h-10">
              <RefreshCw className="mr-2 h-4 w-4 text-muted-foreground" /> Sync Weights
            </Button>
            <Button className="bg-primary hover:bg-primary/90 text-primary-foreground shadow-sm h-10">
              <Database className="mr-2 h-4 w-4" /> Manage Datasets
            </Button>
          </div>
        </header>

        {/* ================= KPI RIBBON ================= */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 w-full">
          <MetricCard title="Active Enrollments" value={clientKPIs.activeTasks} icon={<Activity size={18}/>} subtitle="Federated jobs running locally" />
          <MetricCard title="Peak Local Accuracy" value={clientKPIs.localAccuracy} icon={<TrendingUp size={18}/>} subtitle="Fraud Detection CNN" />
          <MetricCard title="Update Acceptance" value={`${clientKPIs.acceptanceRate}%`} icon={<CheckCircle2 size={18}/>} subtitle="Aggregator approval rate" />
          <MetricCard title="Reputation / Trust" value={clientKPIs.trustScore} icon={<ShieldCheck size={18}/>} subtitle="Excellent standing" />
        </div>

        {/* ================= MIDDLE ROW: LOCAL TRAINING & ACCEPTANCE ================= */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 w-full">
          
          {/* LEFT: Local Convergence Chart (Takes 2/3) */}
          <Card className="lg:col-span-2 bg-card/70 backdrop-blur-xl border-border shadow-sm flex flex-col overflow-hidden group hover:border-primary/50 transition-colors">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg text-foreground">Local Model Progress</CardTitle>
              <CardDescription>Accuracy and Loss metrics across local training rounds (Fraud Detection CNN).</CardDescription>
            </CardHeader>
            <CardContent className="flex-1 min-h-[280px] pt-4">
              <ChartContainer config={convergenceConfig} className="h-full w-full">
                <AreaChart data={localConvergenceData} margin={{ left: -20, right: 10 }}>
                  <defs>
                    <linearGradient id="fillAccLocal" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--color-primary)" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="var(--color-primary)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid vertical={false} strokeDasharray="3 3" stroke="var(--color-border)" opacity={0.5} />
                  <XAxis dataKey="round" tickLine={false} axisLine={false} tickMargin={10} fontSize={12} stroke="var(--color-muted-foreground)" />
                  <YAxis yAxisId="left" tickLine={false} axisLine={false} tickMargin={10} fontSize={12} stroke="var(--color-muted-foreground)" tickFormatter={(v) => `${v}%`} />
                  <ChartTooltip cursor={false} content={<ChartTooltipContent indicator="dot" />} />
                  <Area yAxisId="left" type="monotone" dataKey="accuracy" stroke="var(--color-primary)" fill="url(#fillAccLocal)" strokeWidth={2} />
                  <Area yAxisId="left" type="monotone" dataKey="loss" stroke="var(--color-destructive)" fill="transparent" strokeWidth={2} strokeDasharray="4 4" />
                </AreaChart>
              </ChartContainer>
            </CardContent>
          </Card>

          {/* RIGHT: Acceptance Ratio Donut (Takes 1/3) */}
          <Card className="lg:col-span-1 bg-card/70 backdrop-blur-xl border-border shadow-sm flex flex-col group hover:border-primary/50 transition-colors">
            <CardHeader className="pb-2 border-b border-border/50 bg-muted/20">
              <CardTitle className="text-lg text-foreground">Update Status</CardTitle>
              <CardDescription className="text-xs">Global aggregator responses to your pushed gradients.</CardDescription>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col justify-center items-center pt-6">
              <div className="h-[180px] w-full">
                <ChartContainer config={{}} className="h-full w-full">
                  <PieChart>
                    <ChartTooltip content={<ChartTooltipContent hideLabel />} />
                    <Pie
                      data={acceptanceData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                      stroke="none"
                    >
                      {acceptanceData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                  </PieChart>
                </ChartContainer>
              </div>
              <div className="flex gap-4 mt-4 w-full justify-center text-xs font-medium">
                <div className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Accepted</div>
                <div className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-destructive"></span> Rejected</div>
                <div className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> Delayed</div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* ================= BOTTOM ROW: LOGS & TRUST TREND ================= */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 w-full">
          
          {/* LEFT: Transparency / Update Logs (Takes 2/3) */}
          <Card className="lg:col-span-2 bg-card/70 backdrop-blur-xl border-border shadow-sm flex flex-col overflow-hidden">
            <CardHeader className="pb-4 border-b border-border/50 bg-muted/20 flex flex-row justify-between items-center">
              <div>
                <CardTitle className="text-lg text-foreground flex items-center gap-2">
                  <History size={18} className="text-primary"/> Transparency Logs
                </CardTitle>
                <CardDescription className="text-xs mt-1">Detailed history of gradient transmissions and server responses.</CardDescription>
              </div>
            </CardHeader>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm whitespace-nowrap">
                <thead className="bg-muted/30 text-muted-foreground text-[10px] uppercase tracking-wider border-b border-border">
                  <tr>
                    <th className="px-6 py-3 font-semibold">Update ID</th>
                    <th className="px-6 py-3 font-semibold">Round</th>
                    <th className="px-6 py-3 font-semibold">Status</th>
                    <th className="px-6 py-3 font-semibold">Server Reason</th>
                    <th className="px-6 py-3 font-semibold text-right">Time</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/50">
                  {updateLogs.map((log) => (
                    <tr key={log.id} className="transition-colors hover:bg-muted/20">
                      <td className="px-6 py-3 font-mono text-xs text-muted-foreground">{log.id}</td>
                      <td className="px-6 py-3 font-semibold text-foreground">{log.round}</td>
                      <td className="px-6 py-3">
                        <LogStatus status={log.status} />
                      </td>
                      <td className="px-6 py-3 text-xs">
                        {log.status === "Rejected" ? (
                          <span className="text-destructive font-medium">{log.reason}</span>
                        ) : (
                          <span className="text-muted-foreground">{log.reason}</span>
                        )}
                      </td>
                      <td className="px-6 py-3 text-right text-xs text-muted-foreground">{log.time}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* RIGHT: Trust Score Trend (Bar Chart) */}
          <Card className="lg:col-span-1 bg-card/70 backdrop-blur-xl border-border shadow-sm flex flex-col group hover:border-primary/50 transition-colors">
            <CardHeader className="pb-2 border-b border-border/50 bg-muted/20">
              <CardTitle className="text-lg text-foreground flex items-center gap-2">
                <ShieldCheck size={18} className="text-primary" /> Node Reputation
              </CardTitle>
              <CardDescription className="text-xs">Trust score adjustments by the Byzantine filter.</CardDescription>
            </CardHeader>
            <CardContent className="flex-1 min-h-[220px] pt-6">
              <ChartContainer config={trustConfig} className="h-full w-full">
                <BarChart data={trustScoreTrend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid vertical={false} strokeDasharray="3 3" stroke="var(--color-border)" opacity={0.5} />
                  <XAxis dataKey="epoch" tickLine={false} axisLine={false} tickMargin={10} fontSize={12} stroke="var(--color-muted-foreground)" />
                  <YAxis tickLine={false} axisLine={false} tickMargin={10} fontSize={12} stroke="var(--color-muted-foreground)" domain={[60, 100]} />
                  <ChartTooltip cursor={{ fill: 'var(--color-muted)', opacity: 0.4 }} content={<ChartTooltipContent />} />
                  <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                    {trustScoreTrend.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.score < 85 ? "var(--color-destructive)" : "var(--color-primary)"} />
                    ))}
                  </Bar>
                </BarChart>
              </ChartContainer>
            </CardContent>
          </Card>

        </div>

        {/* ================= BOTTOM ROW 2: PAST EXPERIMENTS ================= */}
        <section>
          <div className="flex items-center justify-between mb-4 mt-6">
            <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-widest flex items-center gap-2">
              <Server className="h-4 w-4 text-muted-foreground" />
              Completed Federated Tasks
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {completedTasks.map((task) => (
              <div key={task.id} className="p-5 rounded-xl border border-border bg-card/70 backdrop-blur-md shadow-sm hover:border-primary/50 transition-colors">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h4 className="font-bold text-foreground text-sm">{task.name}</h4>
                    <div className="text-[10px] font-mono text-muted-foreground mt-1">{task.type}</div>
                  </div>
                  <Badge variant="outline" className={`text-[10px] uppercase tracking-wider ${task.status === 'Completed' ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' : 'bg-destructive/10 text-destructive border-destructive/20'}`}>
                    {task.status}
                  </Badge>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs border-t border-border/50 pt-3 mt-2">
                  <div>
                    <span className="text-muted-foreground block mb-0.5">Final Accuracy</span>
                    <span className="font-bold text-foreground">{task.finalAcc}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground block mb-0.5">Rounds Contributed</span>
                    <span className="font-semibold text-primary">{task.rounds}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

      </main>
    </div>
  );
}

// ==========================================
// UTILITY COMPONENTS
// ==========================================

function MetricCard({ title, value, icon, subtitle }: any) {
  return (
    <Card className="bg-card/70 backdrop-blur-xl border-border shadow-sm group hover:border-primary/50 transition-colors">
      <CardContent className="p-6">
        <div className="flex justify-between items-start mb-4">
          <div className="text-xs font-bold text-muted-foreground uppercase tracking-wider">{title}</div>
          <div className="p-2 rounded-lg bg-primary/10 text-primary">
            {icon}
          </div>
        </div>
        <div className="text-3xl font-extrabold text-foreground mb-1">{value}</div>
        <div className="text-xs font-medium text-muted-foreground">{subtitle}</div>
      </CardContent>
    </Card>
  );
}

function LogStatus({ status }: { status: string }) {
  if (status === "Accepted") {
    return <Badge variant="outline" className="bg-emerald-500/10 text-emerald-500 border-emerald-500/20 text-[10px] uppercase"><CheckCircle2 size={10} className="mr-1"/> Accepted</Badge>;
  }
  if (status === "Delayed") {
    return <Badge variant="outline" className="bg-amber-500/10 text-amber-500 border-amber-500/20 text-[10px] uppercase"><AlertTriangle size={10} className="mr-1"/> Delayed</Badge>;
  }
  if (status === "Rejected") {
    return <Badge variant="outline" className="bg-destructive/10 text-destructive border-destructive/20 text-[10px] uppercase"><XCircle size={10} className="mr-1"/> Rejected</Badge>;
  }
  return <Badge variant="outline">{status}</Badge>;
}