export const mockStocks = [
  { symbol: "AAPL", name: "Apple Inc.", price: 189.84, change: 2.34, changePercent: 1.25, volume: "52.3M", marketCap: "2.95T" },
  { symbol: "GOOGL", name: "Alphabet Inc.", price: 141.80, change: -1.22, changePercent: -0.85, volume: "28.1M", marketCap: "1.78T" },
  { symbol: "MSFT", name: "Microsoft Corp.", price: 378.91, change: 5.67, changePercent: 1.52, volume: "31.7M", marketCap: "2.81T" },
  { symbol: "AMZN", name: "Amazon.com Inc.", price: 178.25, change: 3.10, changePercent: 1.77, volume: "45.2M", marketCap: "1.85T" },
  { symbol: "TSLA", name: "Tesla Inc.", price: 248.42, change: -8.53, changePercent: -3.32, volume: "98.4M", marketCap: "789B" },
  { symbol: "NVDA", name: "NVIDIA Corp.", price: 495.22, change: 12.88, changePercent: 2.67, volume: "61.8M", marketCap: "1.22T" },
  { symbol: "META", name: "Meta Platforms", price: 326.49, change: 4.21, changePercent: 1.31, volume: "22.5M", marketCap: "838B" },
  { symbol: "JPM", name: "JPMorgan Chase", price: 172.33, change: -0.45, changePercent: -0.26, volume: "11.2M", marketCap: "498B" },
];

export const mockSignals = [
  { id: 1, symbol: "NVDA", name: "NVIDIA Corp.", type: "Bullish", confidence: 92, reason: "Strong breakout above resistance with high volume. RSI momentum confirms uptrend.", tags: ["Breakout", "High Volume"] },
  { id: 2, symbol: "AAPL", name: "Apple Inc.", type: "Bullish", confidence: 85, reason: "Golden cross formation on daily chart. Institutional buying detected.", tags: ["Golden Cross", "Institutional"] },
  { id: 3, symbol: "TSLA", name: "Tesla Inc.", type: "Bearish", confidence: 78, reason: "Head and shoulders pattern forming. Volume declining on rallies.", tags: ["Pattern", "Declining Volume"] },
  { id: 4, symbol: "AMZN", name: "Amazon.com Inc.", type: "Bullish", confidence: 88, reason: "Earnings beat expectations. Cloud revenue growing 30% YoY.", tags: ["Earnings Beat", "Growth"] },
  { id: 5, symbol: "MSFT", name: "Microsoft Corp.", type: "Bullish", confidence: 90, reason: "AI integration driving revenue. Strong support at current levels.", tags: ["AI Play", "Support"] },
];

export const mockHoldings = [
  { symbol: "AAPL", name: "Apple Inc.", quantity: 50, avgPrice: 165.20, currentPrice: 189.84, value: 9492, pnl: 1232, pnlPercent: 14.92 },
  { symbol: "MSFT", name: "Microsoft Corp.", quantity: 25, avgPrice: 340.00, currentPrice: 378.91, value: 9472.75, pnl: 972.75, pnlPercent: 11.44 },
  { symbol: "NVDA", name: "NVIDIA Corp.", quantity: 15, avgPrice: 420.50, currentPrice: 495.22, value: 7428.30, pnl: 1120.80, pnlPercent: 17.77 },
  { symbol: "GOOGL", name: "Alphabet Inc.", quantity: 40, avgPrice: 130.00, currentPrice: 141.80, value: 5672, pnl: 472, pnlPercent: 9.08 },
  { symbol: "AMZN", name: "Amazon.com Inc.", quantity: 30, avgPrice: 155.00, currentPrice: 178.25, value: 5347.50, pnl: 697.50, pnlPercent: 15.0 },
];

export const mockPortfolio = {
  totalValue: 37412.55,
  totalInvested: 32917.00,
  totalPnl: 4495.55,
  totalPnlPercent: 13.66,
  dayChange: 523.40,
  dayChangePercent: 1.42,
};

export const mockAlerts = [
  { id: 1, symbol: "AAPL", type: "Price Alert", message: "AAPL crossed above $185.00", timestamp: "2 min ago", read: false },
  { id: 2, symbol: "NVDA", type: "Signal Alert", message: "New bullish signal detected for NVDA", timestamp: "15 min ago", read: false },
  { id: 3, symbol: "TSLA", type: "Volume Alert", message: "Unusual volume spike in TSLA", timestamp: "1 hr ago", read: true },
  { id: 4, symbol: "MSFT", type: "Earnings", message: "MSFT earnings report in 3 days", timestamp: "3 hrs ago", read: true },
];

export const mockChartData = Array.from({ length: 30 }, (_, i) => ({
  date: new Date(2024, 0, i + 1).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
  price: 170 + Math.sin(i / 3) * 15 + Math.random() * 8,
  volume: Math.floor(30 + Math.random() * 40),
}));

export const mockPatterns = [
  { name: "Bullish Engulfing", detected: "2 days ago", confidence: 87, description: "Strong reversal pattern at support level" },
  { name: "Cup and Handle", detected: "5 days ago", confidence: 74, description: "Long-term continuation pattern forming" },
];

export const mockBacktest = {
  winRate: 68,
  totalTrades: 142,
  avgReturn: 3.2,
  maxDrawdown: -8.5,
  sharpeRatio: 1.85,
  profitFactor: 2.1,
};

export const mockFilings = [
  { company: "Apple Inc.", type: "10-K", date: "Nov 3, 2024", description: "Annual report filing" },
  { company: "NVIDIA Corp.", type: "8-K", date: "Oct 28, 2024", description: "Current report - material event" },
  { company: "Microsoft Corp.", type: "10-Q", date: "Oct 24, 2024", description: "Quarterly report filing" },
  { company: "Tesla Inc.", type: "8-K", date: "Oct 18, 2024", description: "Earnings announcement" },
];
