"use client";
import { memo } from "react";
import type { TrafficParticle } from "@/lib/types";
import { GATES, LOUNGES, TERMINAL, APRON, ROADS, TERMINAL_LABELS, HEATMAP_GRID, TRAFFIC_COLORS } from "./terminal-map-data";

interface TerminalMapProps {
  selectedGate: string;
  particles: TrafficParticle[];
  heatmapGrid: number[][];
  simState: "idle" | "running" | "complete";
}

function getHeatColor(count: number): string {
  if (count <= 0) return "transparent";
  if (count <= 2) return TRAFFIC_COLORS.heatLow;
  if (count <= 5) return TRAFFIC_COLORS.heatMed;
  return TRAFFIC_COLORS.heatHigh;
}

function TerminalMapComponent({ selectedGate, particles, heatmapGrid, simState }: TerminalMapProps) {
  return (
    <svg viewBox="0 0 1150 750" width="100%" className="rounded-lg" preserveAspectRatio="xMidYMid meet">
      {/* Background */}
      <rect x="0" y="0" width="1150" height="750" fill="#0f172a" rx="8" />

      {/* Glow filter */}
      <defs>
        <filter id="glow">
          <feGaussianBlur stdDeviation="4" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <filter id="particle-glow">
          <feGaussianBlur stdDeviation="2" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {/* Entry/Exit Roads */}
      <path d={ROADS.entryRoad.path} fill="none" stroke={TRAFFIC_COLORS.road} strokeWidth="3" strokeDasharray="8 4" />
      <text x={ROADS.entryRoad.labelX} y={ROADS.entryRoad.labelY} fill={TRAFFIC_COLORS.roadLabel} fontSize="10" fontWeight="500" textAnchor="middle" transform={`rotate(-90, ${ROADS.entryRoad.labelX}, ${ROADS.entryRoad.labelY})`}>{ROADS.entryRoad.label}</text>
      <path d={ROADS.exitRoad.path} fill="none" stroke={TRAFFIC_COLORS.road} strokeWidth="3" strokeDasharray="8 4" />
      <text x={ROADS.exitRoad.labelX} y={ROADS.exitRoad.labelY} fill={TRAFFIC_COLORS.roadLabel} fontSize="10" fontWeight="500" textAnchor="middle" transform={`rotate(-90, ${ROADS.exitRoad.labelX}, ${ROADS.exitRoad.labelY})`}>{ROADS.exitRoad.label}</text>

      {/* Main Terminal Building */}
      <rect x={TERMINAL.x} y={TERMINAL.y} width={TERMINAL.width} height={TERMINAL.height} fill={TRAFFIC_COLORS.terminal} stroke={TRAFFIC_COLORS.terminalStroke} strokeWidth="2" rx="4" />

      {/* Terminal labels */}
      {TERMINAL_LABELS.map((lbl, i) => (
        <text key={i} x={lbl.x} y={lbl.y} fill={TRAFFIC_COLORS.terminalLabel} fontSize="16" fontWeight="600" textAnchor="middle" opacity="0.5">{lbl.text}</text>
      ))}

      {/* Lounge Areas */}
      {LOUNGES.map((lounge) => (
        <g key={lounge.id}>
          <rect x={lounge.x} y={lounge.y} width={lounge.width} height={lounge.height} fill={TRAFFIC_COLORS.lounge} stroke={TRAFFIC_COLORS.loungeStroke} strokeWidth="1" rx="4" />
          <text x={lounge.x + lounge.width / 2} y={lounge.y + lounge.height / 2 + 4} fill="rgba(34, 197, 94, 0.5)" fontSize="11" fontWeight="500" textAnchor="middle">{lounge.label}</text>
        </g>
      ))}

      {/* KIAL South Apron */}
      <rect x={APRON.x} y={APRON.y} width={APRON.width} height={APRON.height} fill={TRAFFIC_COLORS.apron} stroke={TRAFFIC_COLORS.apronStroke} strokeWidth="1.5" strokeDasharray="6 3" rx="4" />
      <text x={APRON.x + APRON.width / 2} y={APRON.y + APRON.height / 2 + 4} fill={TRAFFIC_COLORS.terminalLabel} fontSize="13" fontWeight="600" textAnchor="middle" opacity="0.6">{APRON.label}</text>

      {/* Heatmap Overlay */}
      {heatmapGrid.map((row, ri) =>
        row.map((count, ci) => (
          <rect
            key={`heat-${ri}-${ci}`}
            x={HEATMAP_GRID.startX + ci * HEATMAP_GRID.cellWidth}
            y={HEATMAP_GRID.startY + ri * HEATMAP_GRID.cellHeight}
            width={HEATMAP_GRID.cellWidth}
            height={HEATMAP_GRID.cellHeight}
            fill={getHeatColor(count)}
            rx="2"
          />
        ))
      )}

      {/* Gates */}
      {GATES.map((gate) => {
        const isActive = gate.id === selectedGate;
        return (
          <g key={gate.id}>
            {/* Active gate glow */}
            {isActive && simState !== "idle" && (
              <>
                <rect x={gate.x - 4} y={gate.y - 4} width={gate.width + 8} height={gate.height + 8} fill="none" stroke={TRAFFIC_COLORS.gateActive} strokeWidth="2" rx="6" opacity="0.4" filter="url(#glow)">
                  <animate attributeName="opacity" values="0.4;0.1;0.4" dur="2s" repeatCount="indefinite" />
                </rect>
              </>
            )}
            <rect
              x={gate.x}
              y={gate.y}
              width={gate.width}
              height={gate.height}
              fill={isActive ? TRAFFIC_COLORS.gateActive : TRAFFIC_COLORS.gate}
              stroke={isActive ? TRAFFIC_COLORS.gateActive : TRAFFIC_COLORS.gateStroke}
              strokeWidth={isActive ? 2 : 1}
              rx="4"
              opacity={isActive ? 1 : 0.8}
            />
            <text
              x={gate.x + gate.width / 2}
              y={gate.y + gate.height / 2 + 4}
              fill={isActive ? "#fff" : "#cbd5e1"}
              fontSize="11"
              fontWeight={isActive ? "700" : "500"}
              textAnchor="middle"
            >
              {gate.label}
            </text>
          </g>
        );
      })}

      {/* Particles */}
      {particles.map((p) => (
        <circle
          key={p.id}
          cx={p.x}
          cy={p.y}
          r={p.size}
          fill={TRAFFIC_COLORS.particle}
          opacity={p.opacity * 0.85}
          filter="url(#particle-glow)"
        />
      ))}

      {/* Legend */}
      <g transform="translate(20, 700)">
        <rect x="0" y="-4" width="8" height="8" fill={TRAFFIC_COLORS.heatLow} rx="2" />
        <text x="12" y="4" fill="#94a3b8" fontSize="9">Low</text>
        <rect x="45" y="-4" width="8" height="8" fill={TRAFFIC_COLORS.heatMed} rx="2" />
        <text x="57" y="4" fill="#94a3b8" fontSize="9">Medium</text>
        <rect x="100" y="-4" width="8" height="8" fill={TRAFFIC_COLORS.heatHigh} rx="2" />
        <text x="112" y="4" fill="#94a3b8" fontSize="9">High</text>
        <circle cx="155" cy="0" r="3" fill={TRAFFIC_COLORS.particle} />
        <text x="162" y="4" fill="#94a3b8" fontSize="9">Passenger</text>
      </g>
    </svg>
  );
}

export const TerminalMap = memo(TerminalMapComponent);
