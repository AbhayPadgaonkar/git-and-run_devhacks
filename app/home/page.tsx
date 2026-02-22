import React from "react";
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

import { ArrowUpRightIcon, FolderClosed as IconFolderCode } from "lucide-react";
type projectProps = {
  id: number;
  title: string;
  client: string;
  description: string;
  status: string;
  progress: number;
  nodes: number;
  lastUpdated: string;
};

// Mock data reflecting federated learning/tech projects
const projects: projectProps[] | null = [
  {
    id: 1,
    title: "MedCorp Data Aggregation",
    client: "MedCorp Health",
    description: "Training predictive models on distributed hospital records.",
    status: "Training",
    progress: 78,
    nodes: 12,
    lastUpdated: "2 hours ago",
  },
  {
    id: 2,
    title: "SecureBank Fraud Detection",
    client: "SecureBank Ltd.",
    description:
      "Cross-border transaction analysis with privacy-preserving FL.",
    status: "Validating",
    progress: 95,
    nodes: 8,
    lastUpdated: "15 mins ago",
  },
  {
    id: 3,
    title: "SmartCity Edge Analytics",
    client: "Gov Infrastructure",
    description: "Traffic optimization using edge device local updates.",
    status: "Queued",
    progress: 0,
    nodes: 45,
    lastUpdated: "1 day ago",
  },
  {
    id: 4,
    title: "SmartCity Edge Analytics",
    client: "Gov Infrastructure",
    description: "Traffic optimization using edge device local updates.",
    status: "Queued",
    progress: 0,
    nodes: 45,
    lastUpdated: "1 day ago",
  },
  {
    id: 5,
    title: "SmartCity Edge Analytics",
    client: "Gov Infrastructure",
    description: "Traffic optimization using edge device local updates.",
    status: "Queued",
    progress: 0,
    nodes: 45,
    lastUpdated: "1 day ago",
  },
  {
    id: 6,
    title: "SmartCity Edge Analytics",
    client: "Gov Infrastructure",
    description: "Traffic optimization using edge device local updates.",
    status: "Queued",
    progress: 0,
    nodes: 45,
    lastUpdated: "1 day ago",
  },
  {
    id: 7,
    title: "SmartCity Edge Analytics",
    client: "Gov Infrastructure",
    description: "Traffic optimization using edge device local updates.",
    status: "Queued",
    progress: 0,
    nodes: 45,
    lastUpdated: "1 day ago",
  },
];

export default function ProjectMenu() {
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
        <Button className="bg-violet-700 hover:bg-violet-800 text-white">
          <Plus className="mr-2 h-4 w-4" /> New Project
        </Button>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full rounded-xl min-h-screen bg-primary/5 p-4 overflow-y-auto">
        {projects && projects.length > 0 ? (
          projects.map((project) => (
            <Card
              key={project.id}
              className="flex flex-col  border-slate-200 shadow-sm hover:shadow-md max-h-full transition-shadow"
            >
              <CardHeader className="pb-4">
                <div className="flex justify-between items-start">
                  <div className="space-y-1">
                    <CardTitle className="text-xl text-slate-900">
                      {project.title}
                    </CardTitle>
                    <CardDescription className="text-violet-600 font-medium">
                      {project.client}
                    </CardDescription>
                  </div>
                  <Badge
                    variant="secondary"
                    className={`
                    ${project.status === "Training" ? "bg-blue-100 text-blue-700" : ""}
                    ${project.status === "Validating" ? "bg-violet-100 text-violet-700" : ""}
                    ${project.status === "Queued" ? "bg-slate-100 text-slate-700" : ""}
                  `}
                  >
                    <Activity className="mr-1 h-3 w-3" />
                    {project.status}
                  </Badge>
                </div>
              </CardHeader>

              <CardContent className="flex-grow space-y-4">
                <p className="text-sm text-slate-600 line-clamp-2">
                  {project.description}
                </p>

                {/* Progress Section */}
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium text-slate-700">
                      Model Convergence
                    </span>
                    <span className="text-slate-500">{project.progress}%</span>
                  </div>
                  <Progress value={project.progress} className="h-2" />
                </div>

                {/* Stats Row */}
                <div className="flex items-center space-x-4 text-sm text-slate-500 pt-2">
                  <div className="flex items-center">
                    <Network className="mr-1 h-4 w-4 text-violet-500" />
                    {project.nodes} Nodes
                  </div>
                  <div className="flex items-center">
                    <Clock className="mr-1 h-4 w-4 text-slate-400" />
                    {project.lastUpdated}
                  </div>
                </div>
              </CardContent>

              <CardFooter className="pt-4 border-t border-slate-100">
                <Button
                  variant="outline"
                  className="w-full text-violet-700 border-violet-200 hover:bg-violet-50"
                >
                  View Dashboard
                </Button>
              </CardFooter>
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
                  You haven&apos;t joined any projects yet. Get started by
                  joining your first project.
                </EmptyDescription>
              </EmptyHeader>
              <EmptyContent className="flex-row justify-center gap-2">
                <Button>Join New Project</Button>
              </EmptyContent>
            </Empty>
          </div>
        )}
      </div>
    </div>
  );
}
