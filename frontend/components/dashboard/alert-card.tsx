"use client";
import { AlertTriangle, CheckCircle, XCircle, Info } from "lucide-react";
import { cn } from "@/lib/utils";

interface AlertCardProps {
  variant: "warning" | "success" | "error" | "info";
  title: string;
  children: React.ReactNode;
}

const variants = {
  warning: { bg: "bg-yellow-500/10 border-yellow-500/30", icon: AlertTriangle, iconColor: "text-yellow-500" },
  success: { bg: "bg-emerald-500/10 border-emerald-500/30", icon: CheckCircle, iconColor: "text-emerald-500" },
  error: { bg: "bg-red-500/10 border-red-500/30", icon: XCircle, iconColor: "text-red-500" },
  info: { bg: "bg-blue-500/10 border-blue-500/30", icon: Info, iconColor: "text-blue-500" },
};

export function AlertCard({ variant, title, children }: AlertCardProps) {
  const v = variants[variant];
  const Icon = v.icon;
  return (
    <div className={cn("rounded-lg border p-4", v.bg)}>
      <div className="flex items-start gap-3">
        <Icon className={cn("h-5 w-5 mt-0.5 shrink-0", v.iconColor)} />
        <div className="min-w-0">
          <p className="text-sm font-semibold">{title}</p>
          <div className="text-sm text-muted-foreground mt-1">{children}</div>
        </div>
      </div>
    </div>
  );
}
