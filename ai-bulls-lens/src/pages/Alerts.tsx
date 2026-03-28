import { DashboardLayout } from "@/components/DashboardLayout";
import { Bell, BellOff, Check } from "lucide-react";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import { useApi } from "@/hooks/useApi";
import { useState } from "react";

function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded bg-secondary/70 ${className}`} />;
}

export default function Alerts() {
  const { data: alertsData, loading, refetch } = useApi(() => api.alerts.list(), []);
  const [localRead, setLocalRead] = useState<Set<number>>(new Set());

  const alerts = (alertsData ?? []).map((a) => ({
    ...a,
    read: a.read || localRead.has(a.id),
  }));

  const markRead = async (id: number) => {
    setLocalRead((prev) => new Set([...prev, id]));
    try {
      await api.alerts.markRead(id);
    } catch {}
  };

  const markAllRead = async () => {
    const ids = (alertsData ?? []).map((a) => a.id);
    setLocalRead(new Set(ids));
    try {
      await api.alerts.markAllRead();
    } catch {}
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-heading font-bold text-foreground flex items-center gap-2">
              <Bell className="h-6 w-6 text-primary" /> Alerts
            </h1>
            <p className="text-sm text-muted-foreground mt-1">Stay updated on your stocks</p>
          </div>
          <button onClick={markAllRead} className="text-xs text-primary hover:underline flex items-center gap-1">
            <Check className="h-3 w-3" /> Mark all read
          </button>
        </div>

        <div className="space-y-3">
          {loading
            ? Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-20 rounded-xl" />)
            : alerts.map((alert, i) => (
                <motion.div
                  key={alert.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.08 }}
                  onClick={() => markRead(alert.id)}
                  className={`bg-card border rounded-xl p-4 cursor-pointer transition-all ${
                    alert.read ? "border-border opacity-60" : "border-primary/30 hover:border-primary/50"
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3">
                      <div
                        className={`mt-0.5 h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                          alert.read ? "bg-secondary" : "bg-primary/10"
                        }`}
                      >
                        {alert.read ? (
                          <BellOff className="h-4 w-4 text-muted-foreground" />
                        ) : (
                          <Bell className="h-4 w-4 text-primary" />
                        )}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-heading font-semibold text-sm text-foreground">{alert.symbol}</span>
                          <span className="text-xs px-2 py-0.5 rounded-full bg-secondary text-muted-foreground">{alert.type}</span>
                        </div>
                        <p className="text-sm text-foreground/80 mt-1">{alert.message}</p>
                      </div>
                    </div>
                    <span className="text-xs text-muted-foreground whitespace-nowrap">{alert.timestamp}</span>
                  </div>
                </motion.div>
              ))}
        </div>
      </div>
    </DashboardLayout>
  );
}
