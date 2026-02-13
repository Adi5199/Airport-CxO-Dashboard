export interface GateConfig {
  id: string;
  label: string;
  x: number;
  y: number;
  width: number;
  height: number;
  edge: "top" | "right";
  centerX: number;
  centerY: number;
}

export interface LoungeConfig {
  id: string;
  label: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

export const TERMINAL = {
  x: 200,
  y: 120,
  width: 800,
  height: 380,
};

export const GATES: GateConfig[] = [
  // Top-edge gates (C-series + D1)
  { id: "C1", label: "Gate C1", x: 250, y: 60, width: 70, height: 60, edge: "top", centerX: 285, centerY: 80 },
  { id: "C2", label: "Gate C2", x: 370, y: 60, width: 70, height: 60, edge: "top", centerX: 405, centerY: 80 },
  { id: "C4", label: "Gate C4", x: 490, y: 60, width: 70, height: 60, edge: "top", centerX: 525, centerY: 80 },
  { id: "C6", label: "Gate C6", x: 610, y: 60, width: 70, height: 60, edge: "top", centerX: 645, centerY: 80 },
  { id: "D1", label: "Gate D1", x: 730, y: 60, width: 70, height: 60, edge: "top", centerX: 765, centerY: 80 },
  { id: "D3", label: "Gate D3", x: 850, y: 60, width: 70, height: 60, edge: "top", centerX: 885, centerY: 80 },
  // Right-edge gates (D-series)
  { id: "D4/D5", label: "D4/D5", x: 1000, y: 140, width: 70, height: 55, edge: "right", centerX: 1035, centerY: 168 },
  { id: "D6/D7", label: "D6/D7", x: 1000, y: 225, width: 70, height: 55, edge: "right", centerX: 1035, centerY: 253 },
  { id: "D8/D9", label: "D8/D9", x: 1000, y: 340, width: 70, height: 55, edge: "right", centerX: 1035, centerY: 368 },
  { id: "D10/D11", label: "D10/D11", x: 1000, y: 430, width: 70, height: 55, edge: "right", centerX: 1035, centerY: 458 },
];

export const LOUNGES: LoungeConfig[] = [
  { id: "lounge-domestic", label: "Domestic Lounge", x: 230, y: 160, width: 300, height: 130 },
  { id: "lounge-intl", label: "Int'l Lounge", x: 580, y: 160, width: 200, height: 130 },
  { id: "lounge-south", label: "Lounge Area", x: 280, y: 350, width: 200, height: 100 },
];

export const APRON = {
  x: 200,
  y: 540,
  width: 600,
  height: 160,
  label: "KIAL South Apron (U/C)",
};

export const ROADS = {
  entryRoad: {
    path: "M 40,180 C 80,180 140,160 200,160",
    label: "T2 Entry Road",
    labelX: 60,
    labelY: 165,
  },
  exitRoad: {
    path: "M 40,440 C 80,440 140,460 200,460",
    label: "T2 Exit Road",
    labelX: 60,
    labelY: 455,
  },
};

export const TERMINAL_LABELS = [
  { text: "Terminal 2", x: 400, y: 310 },
  { text: "Terminal 2", x: 700, y: 310 },
];

export const TRAFFIC_COLORS = {
  terminal: "#1e293b",
  terminalStroke: "#475569",
  gate: "#334155",
  gateStroke: "#64748b",
  gateActive: "#3b82f6",
  gateActiveGlow: "rgba(59, 130, 246, 0.25)",
  lounge: "rgba(34, 197, 94, 0.10)",
  loungeStroke: "rgba(34, 197, 94, 0.25)",
  apron: "rgba(34, 197, 94, 0.08)",
  apronStroke: "#475569",
  particle: "#60a5fa",
  particleGlow: "rgba(96, 165, 250, 0.4)",
  road: "#475569",
  roadLabel: "#94a3b8",
  terminalLabel: "#64748b",
  heatLow: "rgba(34, 197, 94, 0.15)",
  heatMed: "rgba(234, 179, 8, 0.25)",
  heatHigh: "rgba(239, 68, 68, 0.35)",
};

// Heatmap grid configuration (overlaid on terminal area)
export const HEATMAP_GRID = {
  cols: 10,
  rows: 6,
  cellWidth: TERMINAL.width / 10,
  cellHeight: TERMINAL.height / 6,
  startX: TERMINAL.x,
  startY: TERMINAL.y,
};
