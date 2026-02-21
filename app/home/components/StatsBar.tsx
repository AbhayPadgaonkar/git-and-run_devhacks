import { Activity, Shield, Users, Zap } from "lucide-react";
import { motion } from "framer-motion";

const stats = [
  { label: "Active Tasks", value: "3", icon: Activity, accent: "primary" as const },
  { label: "Client Nodes", value: "5 / 6", icon: Users, accent: "success" as const },
  { label: "Avg. Accuracy", value: "91.8%", icon: Zap, accent: "primary" as const },
  { label: "Security Status", value: "1 Alert", icon: Shield, accent: "warning" as const },
];

const accentMap = {
  primary: "text-primary glow-primary border-primary/20",
  success: "text-success glow-success border-success/20",
  warning: "text-warning glow-warning border-warning/20",
};

const StatsBar = () => (
  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
    {stats.map((stat, i) => (
      <motion.div
        key={stat.label}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: i * 0.1 }}
        className={`card-surface p-5 flex items-center gap-4 ${accentMap[stat.accent]}`}
      >
        <div className="p-2.5 rounded-lg bg-secondary">
          <stat.icon className="w-5 h-5" />
        </div>
        <div>
          <p className="text-sm text-muted-foreground">{stat.label}</p>
          <p className="text-2xl font-semibold font-mono-data">{stat.value}</p>
        </div>
      </motion.div>
    ))}
  </div>
);

export default StatsBar;
