export const NAV_ITEMS = [
  { label: "Executive Overview", href: "/overview", icon: "LayoutDashboard" },
  { label: "Queue Compliance", href: "/queue", icon: "Clock" },
  { label: "Security & Operations", href: "/security", icon: "Shield" },
  { label: "AI Insights Chat", href: "/chat", icon: "MessageSquare" },
  { label: "Trends & Analytics", href: "/trends", icon: "TrendingUp" },
] as const;

export const CHART_COLORS = {
  primary: "#3b82f6",
  secondary: "#f97316",
  success: "#22c55e",
  danger: "#ef4444",
  warning: "#eab308",
  muted: "#71717a",
  info: "#06b6d4",
  purple: "#a855f7",
};

export const DEFAULT_REPORT_DATE = "2026-01-24";

// Hardcoded dark-theme colors for Recharts SVG elements.
// SVG presentation attributes (fill, stroke) cannot resolve CSS custom properties.
export const CHART_THEME = {
  axis: "#a1a1aa",        // zinc-400 — axis labels, tick text
  grid: "#27272a",        // zinc-800 — grid lines
  tooltipBg: "#18181b",   // zinc-900 — tooltip background
  tooltipBorder: "#3f3f46", // zinc-700 — tooltip border
  tooltipText: "#f4f4f5", // zinc-100 — tooltip text
  tooltipLabel: "#a1a1aa", // zinc-400 — tooltip label text
  legendText: "#d4d4d8",  // zinc-300 — legend text
};
