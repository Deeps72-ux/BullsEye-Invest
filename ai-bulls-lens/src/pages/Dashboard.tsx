import { DashboardLayout } from "@/components/DashboardLayout";
import { TrendingUp, TrendingDown, DollarSign, BarChart3, Radar, ArrowUpRight, ArrowDownRight, RefreshCw } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { AreaChart, Area, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts";
import { api } from "@/lib/api";
import { useApi } from "@/hooks/useApi";

const fadeIn = {
  hidden: { opacity: 0, y: 12 },
  visible: (i: number) => ({ opacity: 1, y: 0, transition: { delay: i * 0.08, duration: 0.4 } }),
};

function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded bg-secondary/70 ${className}`} />;
}

export default function Dashboard() {
  const navigate = useNavigate();

  const { data: stocks, loading: stocksLoading } = useApi(() => api.market.stocks(), []);
  const { data: signals, loading: signalsLoading } = useApi(() => api.signals.opportunities(), []);
  const { data: portfolio, loading: portfolioLoading } = useApi(() => api.portfolio.summary(), []);
  // Chart data from AAPL detail (first stock)
  const { data: aaplDetail } = useApi(() => api.market.stock("AAPL"), []);

  const topMovers = stocks
    ? [...stocks].sort((a, b) => Math.abs(b.changePercent) - Math.abs(a.changePercent)).slice(0, 4)
    : [];

  const chartData = aaplDetail?.chartData ?? [];

  const isLoading = stocksLoading || signalsLoading || portfolioLoading;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-heading font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground text-sm mt-1">Welcome back. Here's your market overview.</p>
        </div>

        {/* Portfolio Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {isLoading
            ? Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-28 rounded-xl" />)
            : [
                {
                  label: "Portfolio Value",
                  value: portfolio ? `$${portfolio.totalValue.toLocaleString()}` : "—",
                  icon: DollarSign,
                  change: portfolio?.dayChangePercent,
                  sub: portfolio ? `$${portfolio.dayChange.toFixed(0)} today` : "",
                },
                {
                  label: "Total Returns",
                  value: portfolio ? `$${portfolio.totalPnl.toLocaleString()}` : "—",
                  icon: TrendingUp,
                  change: portfolio?.totalPnlPercent,
                  sub: "All time",
                },
                {
                  label: "Top Signals",
                  value: signals ? signals.filter((s) => s.confidence > 85).length.toString() : "—",
                  icon: Radar,
                  sub: "High confidence",
                },
                {
                  label: "Active Stocks",
                  value: stocks ? stocks.length.toString() : "—",
                  icon: BarChart3,
                  sub: "Being tracked",
                },
              ].map((card, i) => (
                <motion.div
                  key={card.label}
                  custom={i}
                  initial="hidden"
                  animate="visible"
                  variants={fadeIn}
                  className="bg-card border border-border rounded-xl p-5 hover:border-primary/30 transition-colors"
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm text-muted-foreground">{card.label}</span>
                    <card.icon className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div className="text-2xl font-heading font-bold text-foreground">{card.value}</div>
                  <div className="flex items-center gap-1 mt-1">
                    {card.change !== undefined && (
                      <span className={`text-xs font-medium flex items-center gap-0.5 ${card.change >= 0 ? "text-bullish" : "text-bearish"}`}>
                        {card.change >= 0 ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
                        {Math.abs(card.change).toFixed(2)}%
                      </span>
                    )}
                    <span className="text-xs text-muted-foreground">{card.sub}</span>
                  </div>
                </motion.div>
              ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chart */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="lg:col-span-2 bg-card border border-border rounded-xl p-5"
          >
            <h2 className="font-heading font-semibold text-foreground mb-4">Portfolio Performance (AAPL)</h2>
            <div className="h-64">
              {chartData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="hsl(160, 84%, 39%)" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="hsl(160, 84%, 39%)" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: "hsl(215, 10%, 46%)" }} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: "hsl(215, 10%, 46%)" }} domain={["dataMin - 5", "dataMax + 5"]} />
                    <Tooltip contentStyle={{ background: "hsl(220, 18%, 10%)", border: "1px solid hsl(220, 15%, 18%)", borderRadius: "8px", color: "hsl(210, 20%, 95%)" }} />
                    <Area type="monotone" dataKey="price" stroke="hsl(160, 84%, 39%)" strokeWidth={2} fill="url(#colorPrice)" />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <Skeleton className="h-full" />
              )}
            </div>
          </motion.div>

          {/* Top Signals */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="bg-card border border-border rounded-xl p-5"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-heading font-semibold text-foreground">Top Signals</h2>
              <button onClick={() => navigate("/signals")} className="text-xs text-primary hover:underline">
                View all
              </button>
            </div>
            <div className="space-y-3">
              {signalsLoading
                ? Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-12 rounded-lg" />)
                : (signals ?? []).slice(0, 4).map((signal) => (
                    <div
                      key={signal.id}
                      className="flex items-center justify-between p-3 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors cursor-pointer"
                      onClick={() => navigate(`/stock/${signal.symbol}`)}
                    >
                      <div>
                        <div className="font-medium text-sm text-foreground">{signal.symbol}</div>
                        <div className="text-xs text-muted-foreground">{signal.name}</div>
                      </div>
                      <div className="text-right">
                        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${signal.type === "Bullish" ? "bg-bullish/10 text-bullish" : "bg-bearish/10 text-bearish"}`}>
                          {signal.type}
                        </span>
                        <div className="text-xs text-muted-foreground mt-1">{signal.confidence}%</div>
                      </div>
                    </div>
                  ))}
            </div>
          </motion.div>
        </div>

        {/* Top Movers */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }} className="bg-card border border-border rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-heading font-semibold text-foreground">Top Movers</h2>
            <button onClick={() => navigate("/markets")} className="text-xs text-primary hover:underline">
              View all
            </button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {stocksLoading
              ? Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-24 rounded-lg" />)
              : topMovers.map((stock) => (
                  <div
                    key={stock.symbol}
                    className="p-4 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors cursor-pointer"
                    onClick={() => navigate(`/stock/${stock.symbol}`)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-heading font-semibold text-foreground">{stock.symbol}</span>
                      {stock.change >= 0 ? <TrendingUp className="h-4 w-4 text-bullish" /> : <TrendingDown className="h-4 w-4 text-bearish" />}
                    </div>
                    <div className="text-lg font-semibold text-foreground">${stock.price.toFixed(2)}</div>
                    <div className={`text-sm font-medium ${stock.change >= 0 ? "text-bullish" : "text-bearish"}`}>
                      {stock.change >= 0 ? "+" : ""}
                      {stock.change.toFixed(2)} ({stock.changePercent.toFixed(2)}%)
                    </div>
                  </div>
                ))}
          </div>
        </motion.div>
      </div>
    </DashboardLayout>
  );
}
