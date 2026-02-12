"use client";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface SeverityBadgeProps {
  severity: string;
  className?: string;
}

export function SeverityBadge({ severity, className }: SeverityBadgeProps) {
  const colors: Record<string, string> = {
    High: "bg-red-500/20 text-red-400 border-red-500/30",
    Medium: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
    Low: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  };

  return (
    <Badge variant="outline" className={cn(colors[severity] || colors.Medium, className)}>
      {severity}
    </Badge>
  );
}
