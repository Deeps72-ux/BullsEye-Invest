import { DashboardLayout } from "@/components/DashboardLayout";
import { Send, Bot, User } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

const mockResponses: Record<string, string> = {
  default: "I'm **BullsEye AI**, your market analysis assistant. I can help you with:\n\n- 📊 Stock analysis and explanations\n- 📈 Technical indicators\n- 🔍 Market trends\n- 💡 Investment insights\n\nWhat would you like to know?",
  aapl: "## Apple Inc. (AAPL)\n\n**Current Analysis:**\n- Price: $189.84 (+1.25%)\n- Trend: **Bullish** — trading above 50 & 200 DMA\n- RSI: 62 (neutral-bullish)\n\n**Key Points:**\n1. Strong institutional buying pressure\n2. Golden cross confirmed on daily chart\n3. iPhone 16 cycle driving revenue expectations\n\n**Recommendation:** Hold/Accumulate on dips near $180 support.",
  market: "## Market Overview\n\nThe broader market is showing **mixed signals**:\n\n| Index | Change | Trend |\n|-------|--------|-------|\n| S&P 500 | +0.8% | Bullish |\n| NASDAQ | +1.2% | Bullish |\n| Russell 2000 | -0.3% | Neutral |\n\n**Key drivers:** AI sector momentum, upcoming Fed meeting, and strong earnings season.",
};

export default function AIChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: "assistant", content: mockResponses.default },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    // Mock response
    setTimeout(() => {
      const lower = userMsg.toLowerCase();
      let response = "That's a great question! Based on current market data, I'd recommend looking at the **Signals** page for AI-generated opportunities. You can also check individual stock pages for detailed technical analysis.\n\nWould you like me to analyze a specific stock?";
      if (lower.includes("aapl") || lower.includes("apple")) response = mockResponses.aapl;
      else if (lower.includes("market") || lower.includes("overview")) response = mockResponses.market;

      setMessages((prev) => [...prev, { role: "assistant", content: response }]);
      setLoading(false);
    }, 1000);
  };

  return (
    <DashboardLayout>
      <div className="flex flex-col h-[calc(100vh-7.5rem)]">
        <div className="mb-4">
          <h1 className="text-2xl font-heading font-bold text-foreground flex items-center gap-2">
            <Bot className="h-6 w-6 text-primary" /> AI Chat
          </h1>
          <p className="text-sm text-muted-foreground mt-1">Ask questions about markets, stocks, and strategies</p>
        </div>

        <div className="flex-1 overflow-y-auto space-y-4 pb-4">
          {messages.map((msg, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
              className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}
            >
              {msg.role === "assistant" && (
                <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <Bot className="h-4 w-4 text-primary" />
                </div>
              )}
              <div className={`max-w-[80%] rounded-xl p-4 text-sm ${
                msg.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "bg-card border border-border text-foreground"
              }`}>
                {msg.role === "assistant" ? (
                  <div className="prose prose-sm prose-invert max-w-none [&_table]:text-foreground [&_th]:text-muted-foreground [&_td]:text-foreground [&_strong]:text-foreground [&_h2]:text-foreground [&_h3]:text-foreground [&_p]:text-foreground/90 [&_li]:text-foreground/90">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
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
              <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                <Bot className="h-4 w-4 text-primary animate-pulse-glow" />
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
