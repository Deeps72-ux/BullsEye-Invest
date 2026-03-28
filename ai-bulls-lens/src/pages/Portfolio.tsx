import { DashboardLayout } from "@/components/DashboardLayout";
import { DollarSign, TrendingUp, ArrowUpRight, ArrowDownRight, Lightbulb } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { api } from "@/lib/api";
import { useApi } from "@/hooks/useApi";

const COLORS = ["hsl(160,84%,39%)", "hsl(200,80%,55%)", "hsl(38,92%,50%)", "hsl(280,65%,60%)", "hsl(340,75%,55%)"];

function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded bg-secondary/70 ${className}`} />;
}

export default function Portfolio() {
  const navigate = useNavigate();

  const { data: portfolio, loading: portfolioLoading } = useApi(() => api.portfolio.summary(), []);
  const { data: holdings, loading: holdingsLoading } = useApi(() => api.portfolio.holdings(), []);
  const { data: analysis } = useApi(() => api.portfolio.analysis(), []);

  const pieData = (holdings ?? []).map((h) => ({ name: h.symbol, value: h.value }));
  const insights: string[] = analysis?.insights ?? [];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <h1 className="text-2xl font-heading font-bold text-foreground">Portfolio</h1>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {portfolioLoading
            ? Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-28 rounded-xl" />)
            : [
                { label: "Total Value", value: portfolio ? `$${portfolio.totalValue.toLocaleString()}` : "—", icon: DollarSign },
                { label: "Total P&L", value: portfolio ? `$${portfolio.totalPnl.toLocaleString()}` : "—", change: portfolio?.totalPnlPercent, icon: TrendingUp },
                { label: "Today", value: portfolio ? `$${portfolio.dayChange.toFixed(0)}` : "—", change: portfolio?.dayChangePercent, icon: TrendingUp },
              ].map((c, i) => (
                <motion.div
                  key={c.label}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="bg-card border border-border rounded-xl p-5"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-muted-foreground">{c.label}</span>
                    <c.icon className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div className="text-2xl font-heading font-bold text-foreground">{c.value}</div>
                  {c.change !== undefined && (
                    <span className={`text-sm font-medium flex items-center gap-0.5 ${c.change >= 0 ? "text-bullish" : "text-bearish"}`}>
                      {c.change >= 0 ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
                      {Math.abs(c.change).toFixed(2)}%
                    </span>
                  )}
                </motion.div>
              ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Holdings Table */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="lg:col-span-2 bg-card border border-border rounded-xl overflow-hidden"
          >
            <div className="p-5 border-b border-border">
              <h2 className="font-heading font-semibold text-foreground">Holdings</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left p-4 text-muted-foreground font-medium">Stock</th>
                    <th className="text-right p-4 text-muted-foreground font-medium">Qty</th>
                    <th className="text-right p-4 text-muted-foreground font-medium hidden sm:table-cell">Avg Price</th>
                    <th className="text-right p-4 text-muted-foreground font-medium">Value</th>
                    <th className="text-right p-4 text-muted-foreground font-medium">P&L</th>
                  </tr>
                </thead>
                <tbody>
                  {holdingsLoading
                    ? Array.from({ length: 5 }).map((_, i) => (
                        <tr key={i} className="border-b border-border">
                          {Array.from({ length: 5 }).map((_, j) => (
                            <td key={j} className="p-4"><Skeleton className="h-4" /></td>
                          ))}
                        </tr>
                      ))
                    : (holdings ?? []).map((h) => (
                        <tr
                          key={h.symbol}
                          className="border-b border-border last:border-0 hover:bg-secondary/50 cursor-pointer transition-colors"
                          onClick={() => navigate(`/stock/${h.symbol}`)}
                        >
                          <td className="p-4">
                            <div className="font-heading font-semibold text-foreground">{h.symbol}</div>
                            <div className="text-xs text-muted-foreground">{h.name}</div>
                          </td>
                          <td className="p-4 text-right text-foreground">{h.quantity}</td>
                          <td className="p-4 text-right text-muted-foreground hidden sm:table-cell">${h.avgPrice.toFixed(2)}</td>
                          <td className="p-4 text-right font-medium text-foreground">${h.value.toLocaleString()}</td>
                          <td className="p-4 text-right">
                            <div className={`font-medium ${h.pnl >= 0 ? "text-bullish" : "text-bearish"}`}>
                              {h.pnl >= 0 ? "+" : ""}${h.pnl.toFixed(0)}
                            </div>
                            <div className={`text-xs ${h.pnlPercent >= 0 ? "text-bullish" : "text-bearish"}`}>
                              {h.pnlPercent >= 0 ? "+" : ""}
                              {h.pnlPercent.toFixed(2)}%
                            </div>
                          </td>
                        </tr>
                      ))}
                </tbody>
              </table>
            </div>
          </motion.div>

          {/* Allocation Pie */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="bg-card border border-border rounded-xl p-5"
          >
            <h2 className="font-heading font-semibold text-foreground mb-4">Allocation</h2>
            <div className="h-56">
              {holdingsLoading ? (
                <Skeleton className="h-full rounded-full" />
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={pieData} cx="50%" cy="50%" innerRadius={55} outerRadius={85} dataKey="value" paddingAngle={3}>
                      {pieData.map((_, i) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ background: "hsl(220,18%,10%)", border: "1px solid hsl(220,15%,18%)", borderRadius: 8, color: "#fff" }} />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
            <div className="flex flex-wrap gap-2 mt-2">
              {pieData.map((d, i) => (
                <span key={d.name} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ background: COLORS[i % COLORS.length] }} />
                  {d.name}
                </span>
              ))}
            </div>
          </motion.div>
        </div>

        {/* AI Insights */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-card border border-border rounded-xl p-5"
        >
          <h2 className="font-heading font-semibold text-foreground mb-4 flex items-center gap-2">
            <Lightbulb className="h-5 w-5 text-warning" /> AI Insights
          </h2>
          <div className="space-y-3">
            {insights.map((text, i) => (
              <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-secondary/50">
                <span className="text-xs text-warning font-medium mt-0.5">#{i + 1}</span>
                <p className="text-sm text-foreground/80">{text}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </DashboardLayout>
  );
}
