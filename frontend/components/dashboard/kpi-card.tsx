"use client";
import { Card, CardContent } from "@/components/ui/card";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

interface KpiCardProps {
  title: string;
  value: string | number;
  suffix?: string;
  delta?: number;
  deltaLabel?: string;
  accentColor?: "blue" | "green" | "red" | "orange" | "purple";
}

const accentColors = {
  blue: "border-l-blue-500",
  green: "border-l-emerald-500",
  red: "border-l-red-500",
  orange: "border-l-orange-500",
  purple: "border-l-purple-500",
};

export function KpiCard({ title, value, suffix = "", delta, deltaLabel, accentColor = "blue" }: KpiCardProps) {
  const formatted = typeof value === "number"
    ? value >= 1000
      ? `${(value / 1000).toFixed(1)}k`
      : value % 1 === 0 ? value.toLocaleString() : value.toFixed(1)
    : value;

  return (
    <Card className={cn("border-l-4", accentColors[accentColor])}>
      <CardContent className="p-4">
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{title}</p>
        <p className="text-2xl font-bold mt-1">
          {formatted}{suffix}
        </p>
        {delta !== undefined && (
          <div className="flex items-center gap-1 mt-1">
            {delta > 0 ? (
              <TrendingUp className="h-3 w-3 text-emerald-500" />
            ) : delta < 0 ? (
              <TrendingDown className="h-3 w-3 text-red-500" />
            ) : (
              <Minus className="h-3 w-3 text-muted-foreground" />
            )}
            <span className={cn("text-xs", delta > 0 ? "text-emerald-500" : delta < 0 ? "text-red-500" : "text-muted-foreground")}>
              {delta > 0 ? "+" : ""}{delta.toFixed(1)}% {deltaLabel || ""}
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
