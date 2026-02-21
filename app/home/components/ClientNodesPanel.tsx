import { useState } from "react";
import { motion } from "framer-motion";
import type { ClientNode } from "@/types/federated";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Pause, Ban, Play, ShieldCheck, ShieldAlert } from "lucide-react";

const statusStyles: Record<string, string> = {
  active: "bg-success/15 text-success border-success/30",
  delayed: "bg-warning/15 text-warning border-warning/30",
  suspicious: "bg-danger/15 text-danger border-danger/30",
  blocked: "bg-muted text-muted-foreground border-muted",
};

const ClientNodesPanel = ({ clients: initialClients }: { clients: ClientNode[] }) => {
  const [clients, setClients] = useState(initialClients);

  const toggleBlock = (id: string) => {
    setClients((prev) =>
      prev.map((c) =>
        c.id === id
          ? { ...c, status: c.status === "blocked" ? "active" : "blocked", trustScore: c.status === "blocked" ? 0.5 : c.trustScore }
          : c
      )
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
      className="card-surface p-5"
    >
      <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
        <ShieldCheck className="w-5 h-5 text-primary" />
        Active Client Nodes
      </h2>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-muted-foreground text-xs border-b border-border">
              <th className="text-left py-2 px-3 font-medium">Node</th>
              <th className="text-left py-2 px-3 font-medium">Organization</th>
              <th className="text-center py-2 px-3 font-medium">Status</th>
              <th className="text-center py-2 px-3 font-medium">Trust</th>
              <th className="text-center py-2 px-3 font-medium">Hash</th>
              <th className="text-right py-2 px-3 font-medium">Last Update</th>
              <th className="text-right py-2 px-3 font-medium">Latency</th>
              <th className="text-center py-2 px-3 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {clients.map((client) => (
              <tr key={client.id} className="border-b border-border/50 hover:bg-secondary/30 transition-colors">
                <td className="py-3 px-3 font-mono-data font-medium text-foreground">{client.name}</td>
                <td className="py-3 px-3 text-muted-foreground">{client.organization}</td>
                <td className="py-3 px-3 text-center">
                  <Badge variant="outline" className={statusStyles[client.status]}>
                    {client.status}
                  </Badge>
                </td>
                <td className="py-3 px-3 text-center">
                  <span className={`font-mono-data font-semibold ${client.trustScore > 0.8 ? "text-success" : client.trustScore > 0.5 ? "text-warning" : "text-danger"}`}>
                    {client.trustScore.toFixed(2)}
                  </span>
                </td>
                <td className="py-3 px-3 text-center">
                  {client.hashVerified ? (
                    <ShieldCheck className="w-4 h-4 text-success mx-auto" />
                  ) : (
                    <ShieldAlert className="w-4 h-4 text-danger mx-auto animate-pulse-glow" />
                  )}
                </td>
                <td className="py-3 px-3 text-right font-mono-data text-muted-foreground">{client.lastUpdate}</td>
                <td className="py-3 px-3 text-right font-mono-data text-muted-foreground">{client.latency}ms</td>
                <td className="py-3 px-3 text-center">
                  <div className="flex items-center justify-center gap-1">
                    {client.status === "blocked" ? (
                      <Button size="sm" variant="ghost" className="h-7 px-2 text-success hover:text-success hover:bg-success/10" onClick={() => toggleBlock(client.id)}>
                        <Play className="w-3.5 h-3.5" />
                      </Button>
                    ) : (
                      <>
                        <Button size="sm" variant="ghost" className="h-7 px-2 text-warning hover:text-warning hover:bg-warning/10">
                          <Pause className="w-3.5 h-3.5" />
                        </Button>
                        <Button size="sm" variant="ghost" className="h-7 px-2 text-danger hover:text-danger hover:bg-danger/10" onClick={() => toggleBlock(client.id)}>
                          <Ban className="w-3.5 h-3.5" />
                        </Button>
                      </>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
};

export default ClientNodesPanel;
