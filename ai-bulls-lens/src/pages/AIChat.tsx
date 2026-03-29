import { DashboardLayout } from "@/components/DashboardLayout";
import { Send, User, TrendingUp, Activity, PieChart, ArrowRight, History, X } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import { useNavigate } from "react-router-dom";
import { api } from "@/lib/api";

interface ChatAction {
  label: string;
  to: string;
  icon: string;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  actions?: ChatAction[];
}

interface HistoryItem {
  id: number;
  query: string;
  symbol: string;
  intent: string;
  recommendation: string;
  confidence: number;
  summary: string;
  created_at: string;
}

const WELCOME_MSG =
  "I'm **BullsEye AI**, your market analysis assistant. I can help you with:\n\n- 📊 Stock analysis and explanations\n- 📈 Technical indicators\n- 🔍 Market trends\n- 💡 Investment insights\n\nWhat would you like to know?";

export default function AIChat() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: "assistant", content: WELCOME_MSG },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [historyItems, setHistoryItems] = useState<HistoryItem[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  // Load chat history on mount
  useEffect(() => {
    api.ai
      .history()
      .then((res) => {
        if (res.history && res.history.length > 0) {
          setHistoryItems(res.history);
          // Rebuild messages from history (most recent 10, reversed to chronological)
          const restored: ChatMessage[] = [];
          const items = res.history.slice(0, 10).reverse();
          for (const h of items) {
            restored.push({ role: "user", content: h.query });
            if (h.summary) {
              restored.push({ role: "assistant", content: h.summary });
            }
          }
          if (restored.length > 0) {
            setMessages([
              { role: "assistant", content: WELCOME_MSG },
              ...restored,
            ]);
          }
        }
      })
      .catch(() => {
        // Silently fail — history is optional
      });
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const res = await api.ai.chat(userMsg);
      let responseMd = res.summary || "";

      if (res.reasoning && res.reasoning.length > 0) {
        responseMd += "\n\n**Reasoning:**\n" + res.reasoning.map((r: string) => `- ${r}`).join("\n");
      }

      if (res.final_recommendation) {
        responseMd += `\n\n**Recommendation:** \`${res.final_recommendation}\` (Confidence: ${res.confidence_label})`;
      }

      if (res.beginner_tip) {
        responseMd += `\n\n💡 **Tip:** ${res.beginner_tip}`;
      }

      if (res.market_data?.price && res.market_data.price > 0) {
        responseMd = `*Current Price: ₹${res.market_data.price}*\n\n` + responseMd;
      }

      let actions: ChatAction[] = [];
      if (res.symbol) {
        actions.push({ label: `${res.symbol} Analysis`, to: `/stock/${res.symbol}`, icon: "trending" });
        if (res.signals?.active_signals?.length > 0 || res.signals?.total > 0) {
          actions.push({ label: "Opportunity Radar", to: "/signals", icon: "activity" });
        }
      } else if (res.intent === "portfolio_review") {
        actions.push({ label: "Open Portfolio", to: "/portfolio", icon: "piechart" });
      } else if (res.intent === "market_overview") {
        actions.push({ label: "Market Overview", to: "/markets", icon: "trending" });
      }
      
      if (actions.length === 0) {
          actions.push({ label: "View Signals", to: "/signals", icon: "activity" });
      }

      setMessages((prev) => [...prev, { role: "assistant", content: responseMd, actions }]);
    } catch (err: any) {
      setMessages((prev) => [...prev, { role: "assistant", content: `❌ Error: ${err.message || "Failed to contact AI Engine"}` }]);
    } finally {
      setLoading(false);
    }
  };

  const loadHistoryItem = (item: HistoryItem) => {
    setMessages([
      { role: "assistant", content: WELCOME_MSG },
      { role: "user", content: item.query },
      ...(item.summary ? [{ role: "assistant" as const, content: item.summary }] : []),
    ]);
    setShowHistory(false);
  };

  return (
    <DashboardLayout>
      <div className="flex flex-col h-[calc(100vh-7.5rem)]">
        {/* Header */}
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="/bullseye.png" alt="BullsEye" className="h-8 w-8 rounded-lg object-contain" />
            <div>
              <h1 className="text-2xl font-heading font-bold text-foreground">BullsEye AI</h1>
              <p className="text-sm text-muted-foreground">Ask questions about markets, stocks, and strategies</p>
            </div>
          </div>
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-secondary hover:bg-secondary/80 text-xs font-medium text-secondary-foreground transition-colors border border-border/30"
            title="Chat History"
          >
            <History className="w-4 h-4" />
            <span className="hidden sm:inline">History</span>
            {historyItems.length > 0 && (
              <span className="ml-1 px-1.5 py-0.5 rounded-full bg-primary/20 text-primary text-[10px] font-bold">
                {historyItems.length}
              </span>
            )}
          </button>
        </div>

        {/* History Sidebar */}
        <AnimatePresence>
          {showHistory && historyItems.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-4 bg-card border border-border rounded-xl overflow-hidden"
            >
              <div className="flex items-center justify-between px-4 py-2 border-b border-border">
                <span className="text-sm font-medium text-foreground">Recent Conversations</span>
                <button onClick={() => setShowHistory(false)} className="p-1 hover:bg-secondary rounded">
                  <X className="w-3.5 h-3.5 text-muted-foreground" />
                </button>
              </div>
              <div className="max-h-48 overflow-y-auto">
                {historyItems.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => loadHistoryItem(item)}
                    className="w-full text-left px-4 py-2.5 hover:bg-secondary/50 transition-colors border-b border-border/30 last:border-0"
                  >
                    <div className="text-sm text-foreground truncate">{item.query}</div>
                    <div className="flex items-center gap-2 mt-0.5">
                      {item.symbol && (
                        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-primary/10 text-primary">
                          {item.symbol}
                        </span>
                      )}
                      <span className="text-[10px] text-muted-foreground">
                        {new Date(item.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 pb-4">
          {messages.map((msg, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
              className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}
            >
              {msg.role === "assistant" && (
                <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1 overflow-hidden">
                  <img src="/bullseye.png" alt="AI" className="h-6 w-6 object-contain" />
                </div>
              )}
              <div className={`max-w-[80%] rounded-xl p-4 text-sm ${
                msg.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "bg-card border border-border text-foreground"
              }`}>
                {msg.role === "assistant" ? (
                  <div className="flex flex-col gap-3">
                    <div className="prose prose-sm prose-invert max-w-none [&_table]:text-foreground [&_th]:text-muted-foreground [&_td]:text-foreground [&_strong]:text-foreground [&_h2]:text-foreground [&_h3]:text-foreground [&_p]:text-foreground/90 [&_li]:text-foreground/90">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                    {msg.actions && msg.actions.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2 pt-2 border-t border-border/50">
                        {msg.actions.map((action, idx) => (
                           <button key={idx} onClick={() => navigate(action.to)} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-secondary hover:bg-secondary/80 text-xs font-medium text-secondary-foreground transition-colors border border-border/30">
                              {action.icon === "trending" && <TrendingUp className="w-3.5 h-3.5 text-primary" />}
                              {action.icon === "activity" && <Activity className="w-3.5 h-3.5 text-warning" />}
                              {action.icon === "piechart" && <PieChart className="w-3.5 h-3.5 text-accent" />}
                              {action.label}
                              <ArrowRight className="w-3 h-3 ml-0.5 opacity-50" />
                           </button>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
                  msg.content
                )}
              </div>
              {msg.role === "user" && (
                <div className="h-8 w-8 rounded-lg bg-secondary flex items-center justify-center flex-shrink-0 mt-1">
                  <User className="h-4 w-4 text-muted-foreground" />
                </div>
              )}
            </motion.div>
          ))}
          {loading && (
            <div className="flex gap-3">
              <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 overflow-hidden">
                <img src="/bullseye.png" alt="AI" className="h-6 w-6 object-contain animate-pulse" />
              </div>
              <div className="bg-card border border-border rounded-xl p-4">
                <div className="flex gap-1">
                  <span className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        <form onSubmit={(e) => { e.preventDefault(); handleSend(); }}
          className="flex gap-3 p-3 bg-card border border-border rounded-xl"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about any stock or market trend..."
            className="flex-1 bg-transparent outline-none text-sm text-foreground placeholder:text-muted-foreground"
          />
          <button type="submit" disabled={loading || !input.trim()}
            className="p-2 rounded-lg bg-primary text-primary-foreground hover:opacity-90 transition-opacity disabled:opacity-40"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>
    </DashboardLayout>
  );
}
