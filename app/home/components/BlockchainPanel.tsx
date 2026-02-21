import { motion } from "framer-motion";
import type { BlockchainRecord } from "@/types/federated";
import { ShieldCheck, ShieldAlert, Link2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";

const BlockchainPanel = ({ records }: { records: BlockchainRecord[] }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 0.6 }}
    className="card-surface p-5"
  >
    <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
      <Link2 className="w-5 h-5 text-primary" />
      Blockchain Integrity Verification
    </h2>

    <div className="space-y-2 max-h-[340px] overflow-y-auto pr-1">
      {records.map((record) => (
        <div
          key={record.id}
          className={`flex items-center justify-between p-3 rounded-md border transition-colors ${
            record.suspicious
              ? "border-danger/30 bg-danger/5"
              : "border-border/50 bg-secondary/20 hover:bg-secondary/40"
          }`}
        >
          <div className="flex items-center gap-3">
            {record.verified ? (
              <ShieldCheck className="w-4 h-4 text-success shrink-0" />
            ) : (
              <ShieldAlert className="w-4 h-4 text-danger shrink-0 animate-pulse-glow" />
            )}
            <div>
              <span className="text-sm font-medium text-foreground">{record.clientName}</span>
              <span className="text-xs text-muted-foreground ml-2">R{record.round}</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <code className="text-xs font-mono-data text-muted-foreground">{record.hash}</code>
            <Badge variant="outline" className={record.verified ? "bg-success/10 text-success border-success/30 text-xs" : "bg-danger/10 text-danger border-danger/30 text-xs"}>
              {record.verified ? "Verified" : "Failed"}
            </Badge>
            <span className="text-xs text-muted-foreground font-mono-data">{record.timestamp}</span>
          </div>
        </div>
      ))}
    </div>

    {records.some((r) => r.suspicious) && (
      <div className="mt-3 p-3 rounded-md border border-warning/30 bg-warning/5 text-sm text-warning">
        ⚠ Weight poisoning attempt detected — suspicious clients flagged for review. Influence reduced via robust aggregation.
      </div>
    )}
  </motion.div>
);

export default BlockchainPanel;
