import { DashboardLayout } from "@/components/DashboardLayout";
import { mockSignals } from "@/lib/mock-data";
import { Zap, ArrowRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

export default function Signals() {
  const navigate = useNavigate();

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-heading font-bold text-foreground flex items-center gap-2">
            <Zap className="h-6 w-6 text-primary" /> Opportunity Radar
          </h1>
          <p className="text-sm text-muted-foreground mt-1">AI-generated trading signals and opportunities</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {mockSignals.map((signal, i) => (
            <motion.div key={signal.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              onClick={() => navigate(`/stock/${signal.symbol}`)}
              className={`bg-card border rounded-xl p-5 cursor-pointer hover:shadow-lg transition-all ${
                signal.type === "Bullish" ? "border-bullish/20 hover:border-bullish/40" : "border-bearish/20 hover:border-bearish/40"
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className={`h-10 w-10 rounded-lg flex items-center justify-center font-heading font-bold text-sm ${
                    signal.type === "Bullish" ? "bg-bullish/10 text-bullish" : "bg-bearish/10 text-bearish"
                  }`}>
                    {signal.symbol.slice(0, 2)}
                  </div>
                  <div>
                    <div className="font-heading font-semibold text-foreground">{signal.symbol}</div>
                    <div className="text-xs text-muted-foreground">{signal.name}</div>
                  </div>
                </div>
                <span className={`text-xs font-semibold px-3 py-1 rounded-full ${
                  signal.type === "Bullish" ? "bg-bullish/10 text-bullish" : "bg-bearish/10 text-bearish"
                }`}>
                  {signal.type}
                </span>
              </div>

              {/* Confidence Bar */}
              <div className="mb-3">
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="text-muted-foreground">Confidence</span>
                  <span className={`font-semibold ${signal.confidence >= 85 ? "text-bullish" : signal.confidence >= 70 ? "text-warning" : "text-bearish"}`}>
                    {signal.confidence}%
                  </span>
                </div>
                <div className="h-2 bg-secondary rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${signal.confidence}%` }}
                    transition={{ delay: i * 0.1 + 0.3, duration: 0.6 }}
                    className={`h-full rounded-full ${signal.confidence >= 85 ? "bg-bullish" : signal.confidence >= 70 ? "bg-warning" : "bg-bearish"}`}
                  />
                </div>
              </div>

              <p className="text-sm text-muted-foreground mb-3">{signal.reason}</p>

              <div className="flex items-center justify-between">
                <div className="flex gap-2">
                  {signal.tags.map((t) => (
                    <span key={t} className="text-xs px-2 py-0.5 rounded-full bg-secondary text-muted-foreground">{t}</span>
                  ))}
                </div>
                <ArrowRight className="h-4 w-4 text-muted-foreground" />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
}
