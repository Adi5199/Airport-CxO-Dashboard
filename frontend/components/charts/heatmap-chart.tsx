"use client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface HeatmapChartProps {
  zones: string[];
  timeWindows: string[];
  values: number[][];
  title: string;
}

function getColor(value: number): string {
  if (value >= 97) return "bg-emerald-500/80";
  if (value >= 95) return "bg-emerald-500/50";
  if (value >= 92) return "bg-yellow-500/50";
  if (value >= 88) return "bg-orange-500/50";
  return "bg-red-500/60";
}

function getTextColor(value: number): string {
  if (value >= 95) return "text-emerald-100";
  if (value >= 92) return "text-yellow-100";
  return "text-red-100";
}

export function HeatmapChart({ zones, timeWindows, values, title }: HeatmapChartProps) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent className="overflow-x-auto">
        <div className="min-w-[600px]">
          {/* Header row */}
          <div className="grid gap-1 mb-1" style={{ gridTemplateColumns: `160px repeat(${timeWindows.length}, 1fr)` }}>
            <div className="text-xs font-medium text-muted-foreground p-2">Zone</div>
            {timeWindows.map((tw) => (
              <div key={tw} className="text-xs font-medium text-muted-foreground text-center p-2">{tw}</div>
            ))}
          </div>
          {/* Data rows */}
          {zones.map((zone, zi) => (
            <div key={zone} className="grid gap-1 mb-1" style={{ gridTemplateColumns: `160px repeat(${timeWindows.length}, 1fr)` }}>
              <div className="text-xs text-muted-foreground p-2 truncate" title={zone}>{zone}</div>
              {values[zi]?.map((val, ti) => (
                <div key={ti} className={`rounded text-center p-2 text-xs font-semibold ${getColor(val)} ${getTextColor(val)}`}>
                  {val?.toFixed(1)}%
                </div>
              ))}
            </div>
          ))}
        </div>
        {/* Legend */}
        <div className="flex items-center gap-4 mt-4 text-xs text-muted-foreground justify-center">
          <div className="flex items-center gap-1"><div className="w-3 h-3 rounded bg-red-500/60" /> &lt;88%</div>
          <div className="flex items-center gap-1"><div className="w-3 h-3 rounded bg-orange-500/50" /> 88-92%</div>
          <div className="flex items-center gap-1"><div className="w-3 h-3 rounded bg-yellow-500/50" /> 92-95%</div>
          <div className="flex items-center gap-1"><div className="w-3 h-3 rounded bg-emerald-500/50" /> 95-97%</div>
          <div className="flex items-center gap-1"><div className="w-3 h-3 rounded bg-emerald-500/80" /> &gt;97%</div>
        </div>
      </CardContent>
    </Card>
  );
}
