"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Clock, Shield, MessageSquare, TrendingUp, Plane } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { label: "Executive Overview", href: "/overview", icon: LayoutDashboard },
  { label: "Queue Compliance", href: "/queue", icon: Clock },
  { label: "Security & Ops", href: "/security", icon: Shield },
  { label: "AI Insights Chat", href: "/chat", icon: MessageSquare },
  { label: "Trends & Analytics", href: "/trends", icon: TrendingUp },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-border bg-card flex flex-col">
      <div className="p-6 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-primary p-2">
            <Plane className="h-5 w-5 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tight">BIAL Operations</h1>
            <p className="text-xs text-muted-foreground">CxO Dashboard</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 px-3">Navigation</p>
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-border">
        <div className="text-center">
          <p className="text-xs text-muted-foreground">Bangalore International Airport</p>
          <p className="text-xs text-muted-foreground">Powered by GenAI</p>
        </div>
      </div>
    </aside>
  );
}
