import { motion } from "framer-motion";
import type { TrainingTask } from "@/types/federated";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";

const logTypeColors: Record<string, string> = {
  info: "text-muted-foreground",
  success: "text-success",
  warning: "text-warning",
  error: "text-danger",
};

const TaskCard = ({ task, index }: { task: TrainingTask; index: number }) => {
  const progress = (task.round / task.totalRounds) * 100;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 + index * 0.1 }}
      className="card-surface p-5 space-y-4"
    >
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-semibold text-foreground">{task.modelName}</h3>
          <p className="text-sm text-muted-foreground">{task.description}</p>
        </div>
        <Badge variant={task.status === "running" ? "default" : "secondary"} className={task.status === "running" ? "bg-success/15 text-success border-success/30" : ""}>
          {task.status}
        </Badge>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="bg-secondary/50 rounded-md p-3 text-center">
          <p className="text-xs text-muted-foreground">Accuracy</p>
          <p className="text-lg font-mono-data text-success font-semibold">{task.accuracy}%</p>
        </div>
        <div className="bg-secondary/50 rounded-md p-3 text-center">
          <p className="text-xs text-muted-foreground">Loss</p>
          <p className="text-lg font-mono-data text-primary font-semibold">{task.loss}</p>
        </div>
        <div className="bg-secondary/50 rounded-md p-3 text-center">
          <p className="text-xs text-muted-foreground">Aggregation</p>
          <p className="text-sm font-mono-data text-foreground font-medium mt-0.5">{task.aggregationMethod}</p>
        </div>
      </div>

      <div>
        <div className="flex justify-between text-xs text-muted-foreground mb-1.5">
          <span>Round {task.round} / {task.totalRounds}</span>
          <span>{progress.toFixed(0)}%</span>
        </div>
        <Progress value={progress} className="h-1.5 bg-secondary" />
      </div>

      <div className="space-y-1.5 max-h-28 overflow-y-auto">
        {task.logs.map((log, i) => (
          <div key={i} className="flex gap-2 text-xs">
            <span className="font-mono-data text-muted-foreground shrink-0">{log.timestamp}</span>
            <span className={logTypeColors[log.type]}>{log.message}</span>
          </div>
        ))}
      </div>
    </motion.div>
  );
};

export default TaskCard;
