const BASE_URL = "http://127.0.0.1:8000/api";

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem("bullseye_token");
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
  const res = await fetch(`${BASE_URL}${endpoint}`, { ...options, headers: { ...headers, ...options?.headers } });
  if (!res.ok) throw new Error(`API Error: ${res.status}`);
  return res.json();
}

export const api = {
  auth: {
    login: (data: { email: string; password: string }) =>
      fetchApi<{ token: string }>("/auth/login/", { method: "POST", body: JSON.stringify(data) }),
    register: (data: { name: string; email: string; password: string }) =>
      fetchApi<{ token: string }>("/auth/register/", { method: "POST", body: JSON.stringify(data) }),
    profile: () => fetchApi<any>("/auth/profile/"),
  },
  market: {
    stocks: () => fetchApi<any[]>("/market/stocks/"),
    stock: (symbol: string) => fetchApi<any>(`/market/stock/${symbol}/`),
    filings: () => fetchApi<any[]>("/market/filings/"),
  },
  signals: {
    opportunities: () => fetchApi<any[]>("/signals/opportunities/"),
    stock: (symbol: string) => fetchApi<any>(`/signals/stock/${symbol}/`),
  },
  analytics: {
    patterns: (symbol: string) => fetchApi<any>(`/analytics/patterns/${symbol}/`),
    indicators: (symbol: string) => fetchApi<any>(`/analytics/indicators/${symbol}/`),
    backtest: (symbol: string) => fetchApi<any>(`/analytics/backtest/${symbol}/`),
  },
  portfolio: {
    summary: () => fetchApi<any>("/portfolio/"),
    holdings: () => fetchApi<any[]>("/portfolio/holdings/"),
    analysis: () => fetchApi<any>("/portfolio/analysis/"),
  },
  alerts: {
    list: () => fetchApi<any[]>("/alerts/"),
    subscribe: (data: { symbol: string; type: string }) =>
      fetchApi<any>("/alerts/subscribe/", { method: "POST", body: JSON.stringify(data) }),
  },
  ai: {
    chat: (message: string) =>
      fetchApi<{ response: string }>("/ai/chat/", { method: "POST", body: JSON.stringify({ message }) }),
    explain: (symbol: string) => fetchApi<{ explanation: string }>(`/ai/explain/${symbol}/`),
  },
  dashboard: () => fetchApi<any>("/dashboard/"),
  search: (q: string) => fetchApi<any[]>(`/search/?q=${encodeURIComponent(q)}`),
};
