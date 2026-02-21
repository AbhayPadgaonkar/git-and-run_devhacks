import { motion } from "framer-motion";
import { Shield, Cpu, Lock, Eye } from "lucide-react";

const features = [
  { icon: Lock, title: "Differential Privacy", desc: "ε = 1.0 noise applied to all gradient updates before transmission" },
  { icon: Shield, title: "Secure Aggregation", desc: "Trimmed mean removes top/bottom 20% of weight updates" },
  { icon: Eye, title: "No Raw Data Sharing", desc: "Only encrypted model gradients leave client environments" },
  { icon: Cpu, title: "Byzantine Fault Tolerance", desc: "Krum & median aggregation handle up to 30% malicious clients" },
];

const PrivacyBanner = () => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    transition={{ delay: 0.8 }}
    className="card-surface p-5 border-primary/20"
  >
    <h2 className="text-lg font-semibold text-foreground mb-3 flex items-center gap-2">
      <Shield className="w-5 h-5 text-primary" />
      Privacy & Security Guarantees
    </h2>
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {features.map((f) => (
        <div key={f.title} className="bg-secondary/40 rounded-md p-3 border border-border/50">
          <f.icon className="w-4 h-4 text-primary mb-2" />
          <p className="text-sm font-medium text-foreground">{f.title}</p>
          <p className="text-xs text-muted-foreground mt-1">{f.desc}</p>
        </div>
      ))}
    </div>
  </motion.div>
);

export default PrivacyBanner;
