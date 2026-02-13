"use client";
import { CalendarDays } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { DEFAULT_REPORT_DATE } from "@/lib/constants";

export function Header() {
  const d = new Date(DEFAULT_REPORT_DATE + "T00:00:00");
  const formatted = d.toLocaleDateString("en-IN", { weekday: "long", year: "numeric", month: "long", day: "numeric" });

  return (
    <header className="sticky top-0 z-30 border-b border-border bg-background/80 backdrop-blur-sm">
      <div className="flex items-center justify-between px-6 py-3">
        <div>
          <h2 className="text-lg font-semibold">BIAL Brain & Advisor</h2>
          <p className="text-sm text-muted-foreground">GenAI-Powered Intelligent Operations</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <CalendarDays className="h-4 w-4" />
            <span>{formatted}</span>
          </div>
          <Badge variant="outline" className="text-xs">BLR</Badge>
        </div>
      </div>
    </header>
  );
}
