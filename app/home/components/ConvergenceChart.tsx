import { motion } from "framer-motion";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from "recharts";
import type { ConvergencePoint } from "../federated";
import { TrendingDown } from "lucide-react";

const ConvergenceChart = ({ data }: { data: ConvergencePoint[] }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 0.7 }}
    className="card-surface p-5"
  >
    <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
      <TrendingDown className="w-5 h-5 text-primary" />
      Training Convergence — FraudNet-CNN
    </h2>

    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div>
        <p className="text-xs text-muted-foreground mb-2 font-medium">Loss over Rounds</p>
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="lossGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="hsl(187, 100%, 50%)" stopOpacity={0.3} />
                <stop offset="100%" stopColor="hsl(187, 100%, 50%)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(222, 20%, 18%)" />
            <XAxis dataKey="round" tick={{ fill: "hsl(215, 20%, 55%)", fontSize: 11 }} stroke="hsl(222, 20%, 18%)" />
            <YAxis tick={{ fill: "hsl(215, 20%, 55%)", fontSize: 11 }} stroke="hsl(222, 20%, 18%)" />
            <Tooltip
              contentStyle={{ background: "hsl(222, 40%, 9%)", border: "1px solid hsl(222, 20%, 18%)", borderRadius: 8, color: "hsl(210, 40%, 92%)", fontSize: 12 }}
            />
            <Area type="monotone" dataKey="loss" stroke="hsl(187, 100%, 50%)" fill="url(#lossGradient)" strokeWidth={2} dot={false} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div>
        <p className="text-xs text-muted-foreground mb-2 font-medium">Accuracy over Rounds</p>
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="accGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="hsl(142, 71%, 45%)" stopOpacity={0.3} />
                <stop offset="100%" stopColor="hsl(142, 71%, 45%)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(222, 20%, 18%)" />
            <XAxis dataKey="round" tick={{ fill: "hsl(215, 20%, 55%)", fontSize: 11 }} stroke="hsl(222, 20%, 18%)" />
            <YAxis tick={{ fill: "hsl(215, 20%, 55%)", fontSize: 11 }} stroke="hsl(222, 20%, 18%)" domain={[25, 100]} />
            <Tooltip
              contentStyle={{ background: "hsl(222, 40%, 9%)", border: "1px solid hsl(222, 20%, 18%)", borderRadius: 8, color: "hsl(210, 40%, 92%)", fontSize: 12 }}
            />
            <Area type="monotone" dataKey="accuracy" stroke="hsl(142, 71%, 45%)" fill="url(#accGradient)" strokeWidth={2} dot={false} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  </motion.div>
);

export default ConvergenceChart;
