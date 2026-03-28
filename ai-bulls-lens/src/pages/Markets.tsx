import { DashboardLayout } from "@/components/DashboardLayout";
import { mockStocks, mockFilings } from "@/lib/mock-data";
import { Search, TrendingUp, TrendingDown, FileText } from "lucide-react";
import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";

export default function Markets() {
  const [searchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get("q") || "");
  const navigate = useNavigate();

  const filtered = mockStocks.filter(
    (s) => s.symbol.toLowerCase().includes(query.toLowerCase()) || s.name.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-heading font-bold text-foreground">Markets</h1>
            <p className="text-sm text-muted-foreground mt-1">Browse and search all tracked stocks</p>
          </div>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Filter stocks..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="pl-9 pr-4 py-2 text-sm bg-secondary rounded-lg border-none outline-none focus:ring-2 focus:ring-primary/30 w-full sm:w-64 text-foreground placeholder:text-muted-foreground"
            />
          </div>
        </div>

        {/* Stocks Table */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
          className="bg-card border border-border rounded-xl overflow-hidden"
        >
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left p-4 text-muted-foreground font-medium">Symbol</th>
                  <th className="text-left p-4 text-muted-foreground font-medium hidden sm:table-cell">Name</th>
                  <th className="text-right p-4 text-muted-foreground font-medium">Price</th>
                  <th className="text-right p-4 text-muted-foreground font-medium">Change</th>
                  <th className="text-right p-4 text-muted-foreground font-medium hidden md:table-cell">Volume</th>
                  <th className="text-right p-4 text-muted-foreground font-medium hidden lg:table-cell">Market Cap</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((stock) => (
                  <tr key={stock.symbol}
                    className="border-b border-border last:border-0 hover:bg-secondary/50 transition-colors cursor-pointer"
                    onClick={() => navigate(`/stock/${stock.symbol}`)}
                  >
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        {stock.change >= 0 ? <TrendingUp className="h-4 w-4 text-bullish" /> : <TrendingDown className="h-4 w-4 text-bearish" />}
                        <span className="font-heading font-semibold text-foreground">{stock.symbol}</span>
                      </div>
                    </td>
                    <td className="p-4 text-muted-foreground hidden sm:table-cell">{stock.name}</td>
                    <td className="p-4 text-right font-medium text-foreground">${stock.price.toFixed(2)}</td>
                    <td className={`p-4 text-right font-medium ${stock.change >= 0 ? "text-bullish" : "text-bearish"}`}>
                      {stock.change >= 0 ? "+" : ""}{stock.changePercent.toFixed(2)}%
                    </td>
                    <td className="p-4 text-right text-muted-foreground hidden md:table-cell">{stock.volume}</td>
                    <td className="p-4 text-right text-muted-foreground hidden lg:table-cell">{stock.marketCap}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>

        {/* Filings */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          className="bg-card border border-border rounded-xl p-5"
        >
          <h2 className="font-heading font-semibold text-foreground mb-4 flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" /> Recent Filings
          </h2>
          <div className="space-y-3">
            {mockFilings.map((f, i) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-secondary/50">
                <div>
                  <div className="font-medium text-sm text-foreground">{f.company}</div>
                  <div className="text-xs text-muted-foreground">{f.description}</div>
                </div>
                <div className="text-right">
                  <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-primary/10 text-primary">{f.type}</span>
                  <div className="text-xs text-muted-foreground mt-1">{f.date}</div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </DashboardLayout>
  );
}
