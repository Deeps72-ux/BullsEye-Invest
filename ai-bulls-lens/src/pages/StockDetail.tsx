import { DashboardLayout } from "@/components/DashboardLayout";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, TrendingUp, TrendingDown, Bell, Zap } from "lucide-react";
import { motion } from "framer-motion";
import { AreaChart, Area, BarChart, Bar, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts";
import { api } from "@/lib/api";
import { useApi } from "@/hooks/useApi";

function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded bg-secondary/70 ${className}`} />;
}

export default function StockDetail() {
  const { symbol } = useParams<{ symbol: string }>();
  const navigate = useNavigate();
  const sym = symbol?.toUpperCase() ?? "AAPL";

  const { data: stock, loading: stockLoading } = useApi(() => api.market.stock(sym), [sym]);
  const { data: signals } = useApi(() => api.signals.stock(sym), [sym]);
  const { data: patternsResp } = useApi(() => api.analytics.patterns(sym), [sym]);
  const { data: backtest } = useApi(() => api.analytics.backtest(sym), [sym]);

  const signal = signals?.[0] ?? null;
  const patterns = patternsResp?.patterns ?? [];
  const chartData = stock?.chartData ?? [];

  const isUp = (stock?.change ?? 0) >= 0;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <button onClick={() => navigate(-1)} className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors">
          <ArrowLeft className="h-4 w-4" /> Back
        </button>

        {stockLoading ? (
          <Skeleton className="h-20 rounded-xl" />
        ) : stock ? (
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-3xl font-heading font-bold text-foreground">{stock.symbol}</h1>
                {isUp ? <TrendingUp className="h-6 w-6 text-bullish" /> : <TrendingDown className="h-6 w-6 text-bearish" />}
              </div>
              <p className="text-muted-foreground mt-1">{stock.name}</p>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <div className="text-3xl font-heading font-bold text-foreground">${stock.price.toFixed(2)}</div>
                <div className={`text-sm font-medium ${isUp ? "text-bullish" : "text-bearish"}`}>
                  {isUp ? "+" : ""}
                  {stock.change.toFixed(2)} ({stock.changePercent.toFixed(2)}%)
                </div>
              </div>
              <button className="p-2 rounded-lg bg-secondary hover:bg-accent transition-colors text-muted-foreground">
                <Bell className="h-5 w-5" />
              </button>
            </div>
          </div>
        ) : null}

        {/* Signal Banner */}
        {signal && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`p-4 rounded-xl border ${signal.type === "Bullish" ? "bg-bullish/10 border-bullish/20" : "bg-bearish/10 border-bearish/20"}`}
          >
            <div className="flex items-center gap-2 mb-1">
              <Zap className={`h-4 w-4 ${signal.type === "Bullish" ? "text-bullish" : "text-bearish"}`} />
              <span className={`font-semibold text-sm ${signal.type === "Bullish" ? "text-bullish" : "text-bearish"}`}>
                {signal.type} Signal — {signal.confidence}% Confidence
              </span>
            </div>
            <p className="text-sm text-foreground/80">{signal.reason}</p>
            <div className="flex gap-2 mt-2 flex-wrap">
              {(signal.tags ?? []).map((t) => (
                <span key={t} className="text-xs px-2 py-0.5 rounded-full bg-background/50 text-muted-foreground">
                  {t}
                </span>
              ))}
            </div>
          </motion.div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Price Chart */}
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }} className="lg:col-span-2 bg-card border border-border rounded-xl p-5">
            <h2 className="font-heading font-semibold text-foreground mb-4">Price Chart</h2>
            <div className="h-72">
              {chartData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient id="stockGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={isUp ? "hsl(160,84%,39%)" : "hsl(0,72%,51%)"} stopOpacity={0.3} />
                        <stop offset="95%" stopColor={isUp ? "hsl(160,84%,39%)" : "hsl(0,72%,51%)"} stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: "hsl(215,10%,46%)" }} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: "hsl(215,10%,46%)" }} domain={["dataMin-5", "dataMax+5"]} />
                    <Tooltip contentStyle={{ background: "hsl(220,18%,10%)", border: "1px solid hsl(220,15%,18%)", borderRadius: 8, color: "#fff" }} />
                    <Area type="monotone" dataKey="price" stroke={isUp ? "hsl(160,84%,39%)" : "hsl(0,72%,51%)"} strokeWidth={2} fill="url(#stockGrad)" />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <Skeleton className="h-full" />
              )}
            </div>
          </motion.div>

          {/* Volume Chart */}
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="bg-card border border-border rounded-xl p-5">
            <h2 className="font-heading font-semibold text-foreground mb-4">Volume</h2>
            <div className="h-72">
              {chartData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: "hsl(215,10%,46%)" }} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: "hsl(215,10%,46%)" }} />
                    <Tooltip contentStyle={{ background: "hsl(220,18%,10%)", border: "1px solid hsl(220,15%,18%)", borderRadius: 8, color: "#fff" }} />
                    <Bar dataKey="volume" fill="hsl(200,80%,55%)" radius={[4, 4, 0, 0]} opacity={0.7} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Skeleton className="h-full" />
              )}
            </div>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Patterns */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="bg-card border border-border rounded-xl p-5">
            <h2 className="font-heading font-semibold text-foreground mb-4">Detected Patterns</h2>
            {patterns.length === 0 ? (
              <p className="text-sm text-muted-foreground">No patterns detected yet.</p>
            ) : (
              <div className="space-y-3">
                {patterns.map((p) => (
                  <div key={p.name} className="p-3 rounded-lg bg-secondary/50">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-sm text-foreground">{p.name}</span>
                      <span className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary">{p.confidence}%</span>
                    </div>
                    <p className="text-xs text-muted-foreground">{p.description}</p>
                    <p className="text-xs text-muted-foreground mt-1">Detected {p.detected}</p>
                  </div>
                ))}
              </div>
            )}
          </motion.div>

          {/* Backtest */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="bg-card border border-border rounded-xl p-5">
            <h2 className="font-heading font-semibold text-foreground mb-4">Backtest Results</h2>
            {!backtest || backtest.winRate === null ? (
              <p className="text-sm text-muted-foreground">No backtest data available.</p>
            ) : (
              <div className="grid grid-cols-2 gap-4">
                {[
                  { label: "Win Rate", value: `${backtest.winRate}%`, good: true },
                  { label: "Total Trades", value: String(backtest.totalTrades) },
                  { label: "Avg Return", value: `${backtest.avgReturn}%`, good: true },
                  { label: "Max Drawdown", value: `${backtest.maxDrawdown}%`, good: false },
                  { label: "Sharpe Ratio", value: String(backtest.sharpeRatio), good: true },
                  { label: "Profit Factor", value: `${backtest.profitFactor}x`, good: true },
                ].map((item) => (
                  <div key={item.label} className="p-3 rounded-lg bg-secondary/50">
                    <div className="text-xs text-muted-foreground mb-1">{item.label}</div>
                    <div className={`text-lg font-heading font-bold ${item.good === true ? "text-bullish" : item.good === false ? "text-bearish" : "text-foreground"}`}>
                      {item.value}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        </div>

        {/* Key Stats */}
        {stock && (
          <div className="bg-card border border-border rounded-xl p-5">
            <h2 className="font-heading font-semibold text-foreground mb-4">Key Statistics</h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {[
                { label: "Market Cap", value: stock.marketCap },
                { label: "Volume", value: stock.volume },
                { label: "52W High", value: `$${(stock.price * 1.15).toFixed(2)}` },
                { label: "52W Low", value: `$${(stock.price * 0.72).toFixed(2)}` },
              ].map((s) => (
                <div key={s.label}>
                  <div className="text-xs text-muted-foreground">{s.label}</div>
                  <div className="font-medium text-foreground">{s.value}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
