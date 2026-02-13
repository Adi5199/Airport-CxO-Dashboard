"use client";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Users, Timer, Activity, MapPin } from "lucide-react";
import { GATES } from "./terminal-map-data";

export function GatesLegend({ selectedGate }: { selectedGate: string }) {
  return (
    <Card>
      <CardContent className="p-4">
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">All Gates</p>
        <div className="grid grid-cols-2 gap-1.5">
          {GATES.map((g) => (
            <div
              key={g.id}
              className={`px-2 py-1 rounded text-xs font-medium text-center ${
                g.id === selectedGate
                  ? "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                  : "bg-muted/50 text-muted-foreground"
              }`}
            >
              {g.id}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

interface StatusPanelProps {
  selectedGate: string;
  simState: "idle" | "running" | "complete";
  passengersArrived: number;
  totalPassengers: number;
  elapsedMs: number;
  congestionLevel: "low" | "medium" | "high";
  showGates?: boolean;
}

const congestionConfig = {
  low: { label: "Low", color: "bg-emerald-500", textColor: "text-emerald-400", width: "w-1/3" },
  medium: { label: "Medium", color: "bg-amber-500", textColor: "text-amber-400", width: "w-2/3" },
  high: { label: "High", color: "bg-red-500", textColor: "text-red-400", width: "w-full" },
};

export function StatusPanel({ selectedGate, simState, passengersArrived, totalPassengers, elapsedMs, congestionLevel, showGates = true }: StatusPanelProps) {
  const gate = GATES.find((g) => g.id === selectedGate);
  const elapsed = Math.floor(elapsedMs / 1000);
  const minutes = Math.floor(elapsed / 60);
  const seconds = elapsed % 60;
  const timeFormatted = `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
  const cong = congestionConfig[congestionLevel];

  return (
    <div className="space-y-3">
      {/* Gate Status */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-2 mb-2">
            <MapPin className="h-4 w-4 text-blue-400" />
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Gate Status</span>
          </div>
          <p className="text-lg font-bold">{gate?.label || selectedGate}</p>
          <Badge
            variant="outline"
            className={`mt-1 text-xs ${
              simState === "running"
                ? "bg-blue-500/20 text-blue-400 border-blue-500/30"
                : simState === "complete"
                ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                : "bg-muted text-muted-foreground"
            }`}
          >
            {simState === "running" ? "Boarding Active" : simState === "complete" ? "Boarding Complete" : "Idle"}
          </Badge>
        </CardContent>
      </Card>

      {/* Passengers in Transit */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-2 mb-2">
            <Users className="h-4 w-4 text-emerald-400" />
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Passengers</span>
          </div>
          <p className="text-2xl font-bold">{passengersArrived} <span className="text-sm font-normal text-muted-foreground">/ {totalPassengers}</span></p>
          <div className="w-full bg-muted rounded-full h-2 mt-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${totalPassengers > 0 ? (passengersArrived / totalPassengers) * 100 : 0}%` }}
            />
          </div>
        </CardContent>
      </Card>

      {/* Congestion Level */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="h-4 w-4 text-amber-400" />
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Congestion</span>
          </div>
          <p className={`text-lg font-bold ${cong.textColor}`}>{cong.label}</p>
          <div className="w-full bg-muted rounded-full h-2 mt-2">
            <div className={`${cong.color} h-2 rounded-full transition-all duration-500 ${cong.width}`} />
          </div>
        </CardContent>
      </Card>

      {/* Time Elapsed */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-2 mb-2">
            <Timer className="h-4 w-4 text-purple-400" />
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Time Elapsed</span>
          </div>
          <p className="text-2xl font-bold font-mono">{timeFormatted}</p>
        </CardContent>
      </Card>

      {/* Gate Legend */}
      {showGates && (
        <Card>
          <CardContent className="p-4">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">All Gates</p>
            <div className="grid grid-cols-2 gap-1.5">
              {GATES.map((g) => (
                <div
                  key={g.id}
                  className={`px-2 py-1 rounded text-xs font-medium text-center ${
                    g.id === selectedGate
                      ? "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                      : "bg-muted/50 text-muted-foreground"
                  }`}
                >
                  {g.id}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
