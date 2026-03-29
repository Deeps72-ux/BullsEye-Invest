const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

// ─── Core fetch helper ───────────────────────────────────────────────────────
async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem("bullseye_token");
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  const res = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers: { ...headers, ...(options?.headers as Record<string, string>) },
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
    throw new Error(err?.error || `API Error: ${res.status}`);
  }
  return res.json();
}

// ─── Types ───────────────────────────────────────────────────────────────────
export interface Stock {
  symbol: string;
  name: string;
  sector?: string;
  price: number;
  change: number;
  changePercent: number;
  volume: string;
  marketCap: string;
  chartData?: ChartPoint[];
}

export interface ChartPoint {
  date: string;
  price: number;
  volume: number;
}

export interface Signal {
  id: number;
  symbol: string;
  name: string;
  type: string;       // "Bullish" | "Bearish" | "Neutral"
  confidence: number;
  reason: string;
  tags: string[];
  createdAt: string;
}

export interface Holding {
  symbol: string;
  name: string;
  quantity: number;
  avgPrice: number;
  currentPrice: number;
  value: number;
  pnl: number;
  pnlPercent: number;
}

export interface PortfolioSummary {
  totalValue: number;
  totalInvested: number;
  totalPnl: number;
  totalPnlPercent: number;
  dayChange: number;
  dayChangePercent: number;
}

export interface AlertItem {
  id: number;
  symbol: string;
  type: string;
  message: string;
  timestamp: string;
  read: boolean;
}

export interface Filing {
  company: string;
  symbol: string;
  type: string;
  date: string;
  description: string;
}

export interface Pattern {
  name: string;
  confidence: number;
  description: string;
  detected: string;
}

export interface BacktestResult {
  symbol: string;
  strategy?: string;
  winRate: number | null;
  avgReturn: number;
  totalTrades: number;
  maxDrawdown: number;
  sharpeRatio: number;
  profitFactor: number;
}

// ─── API client ───────────────────────────────────────────────────────────────
export const api = {
  auth: {
    login: (data: { username?: string; email?: string; password: string }) =>
      fetchApi<{ token: string; refresh: string; user_id: number }>(
        "/auth/login/",
        { method: "POST", body: JSON.stringify(data) },
      ),
    register: (data: { name: string; email: string; password: string }) =>
      fetchApi<{ token: string; refresh: string }>(
        "/auth/register/",
        { method: "POST", body: JSON.stringify(data) },
      ),
    profile: () => fetchApi<any>("/auth/profile/"),
  },

  market: {
    stocks: (q?: string) =>
      fetchApi<Stock[]>(`/market/stocks/${q ? `?q=${encodeURIComponent(q)}` : ""}`),
    stock: (symbol: string) => fetchApi<Stock>(`/market/stock/${symbol}/`),
    filings: () => fetchApi<Filing[]>("/market/filings/"),
  },

  signals: {
    opportunities: () => fetchApi<Signal[]>("/signals/opportunities/"),
    stock: (symbol: string) => fetchApi<Signal[]>(`/signals/stock/${symbol}/`),
  },

  analytics: {
    patterns: (symbol: string) =>
      fetchApi<{ symbol: string; patterns: Pattern[] }>(`/analytics/patterns/${symbol}/`),
    indicators: (symbol: string) => fetchApi<any>(`/analytics/indicators/${symbol}/`),
    backtest: (symbol: string) => fetchApi<BacktestResult>(`/analytics/backtest/${symbol}/`),
  },

  portfolio: {
    summary: () => fetchApi<PortfolioSummary>("/portfolio/"),
    holdings: () => fetchApi<Holding[]>("/portfolio/holdings/"),
    analysis: () => fetchApi<{ risk: string; insights: string[] }>("/portfolio/analysis/"),
  },

  alerts: {
    list: () => fetchApi<AlertItem[]>("/alerts/"),
    markRead: (id: number) =>
      fetchApi<any>(`/alerts/${id}/read/`, { method: "PATCH" }),
    markAllRead: () =>
      fetchApi<any>("/alerts/read-all/", { method: "POST" }),
    subscribe: (data: { symbol: string; type: string }) =>
      fetchApi<any>("/alerts/subscribe/", { method: "POST", body: JSON.stringify(data) }),
  },

  ai: {
    chat: (query: string) =>
      fetchApi<any>("/ai/chat/", {
        method: "POST",
        body: JSON.stringify({ query }),
      }),
    explain: (symbol: string) =>
      fetchApi<any>(`/ai/explain/${symbol}/`),
    history: () =>
      fetchApi<{ count: number; history: any[] }>("/ai/history/"),
  },
};
