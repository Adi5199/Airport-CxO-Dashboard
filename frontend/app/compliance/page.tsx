"use client";
import { useApi } from "@/hooks/use-api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { DEFAULT_REPORT_DATE } from "@/lib/constants";
import { ShareButton } from "@/components/dashboard/share-button";
import { Settings, Scale, Gavel, BookOpen, CalendarClock, AlertTriangle, CheckCircle2, Clock } from "lucide-react";

interface ComplianceCategory {
  category: string;
  icon: string;
  issues: number;
  description: string;
  severity: string;
}

interface ComplianceTask {
  id: number;
  title: string;
  category: string;
  deadline: string;
  days_remaining: number;
  priority: string;
  status: string;
  assigned_to: string;
}

const iconMap: Record<string, React.ElementType> = {
  Settings: Settings,
  Scale: Scale,
  Gavel: Gavel,
  BookOpen: BookOpen,
};

const severityColors: Record<string, string> = {
  high: "bg-red-500/15 border-red-500/30 text-red-400",
  medium: "bg-amber-500/15 border-amber-500/30 text-amber-400",
  low: "bg-emerald-500/15 border-emerald-500/30 text-emerald-400",
};

const priorityColors: Record<string, string> = {
  high: "bg-red-500/20 text-red-400",
  medium: "bg-amber-500/20 text-amber-400",
  low: "bg-blue-500/20 text-blue-400",
};

const statusColors: Record<string, string> = {
  in_progress: "bg-blue-500/20 text-blue-400",
  pending: "bg-muted text-muted-foreground",
  scheduled: "bg-purple-500/20 text-purple-400",
  confirmed: "bg-emerald-500/20 text-emerald-400",
};

export default function ComplianceAdvisorPage() {
  const date = DEFAULT_REPORT_DATE;
  const { data: summary, isLoading } = useApi<{ total_issues: number; categories: ComplianceCategory[] }>("/api/compliance/summary", { date });
  const { data: tasksData } = useApi<{ tasks: ComplianceTask[] }>("/api/compliance/upcoming-tasks", { date });

  const d = new Date(date + "T00:00:00");
  const formattedDate = d.toLocaleDateString("en-IN", { year: "numeric", month: "long", day: "numeric" });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Compliance Advisor</h1>
          <p className="text-muted-foreground">Compliance monitoring & upcoming regulatory tasks for {formattedDate}</p>
        </div>
        <ShareButton title="Compliance Advisor Report" />
      </div>

      {/* Total Issues Banner */}
      {summary && (
        <Card className="border-amber-500/30 bg-amber-500/5">
          <CardContent className="p-4 flex items-center gap-4">
            <div className="rounded-lg bg-amber-500/15 p-3">
              <AlertTriangle className="h-6 w-6 text-amber-400" />
            </div>
            <div>
              <p className="text-2xl font-bold">{summary.total_issues} Active Compliance Events</p>
              <p className="text-sm text-muted-foreground">Detected across all categories on {formattedDate}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Compliance Categories */}
      {isLoading ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-40" />)}
        </div>
      ) : summary ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {summary.categories.map((cat) => {
            const Icon = iconMap[cat.icon] || Settings;
            return (
              <Card key={cat.category} className={`border ${severityColors[cat.severity]}`}>
                <CardContent className="p-5">
                  <div className="flex items-center gap-3 mb-3">
                    <div className={`rounded-lg p-2 ${cat.severity === "high" ? "bg-red-500/15" : cat.severity === "medium" ? "bg-amber-500/15" : "bg-emerald-500/15"}`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold">{cat.category}</p>
                      <Badge variant="outline" className={`text-xs mt-1 ${severityColors[cat.severity]}`}>
                        {cat.severity}
                      </Badge>
                    </div>
                  </div>
                  <p className="text-3xl font-bold mb-2">{cat.issues}</p>
                  <p className="text-xs text-muted-foreground leading-relaxed">{cat.description}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      ) : null}

      {/* Upcoming Compliance Tasks */}
      <div>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <CalendarClock className="h-5 w-5" />
          Upcoming Compliance Tasks & Deadlines
        </h3>
        {tasksData ? (
          <div className="space-y-3">
            {tasksData.tasks.map((task) => (
              <Card key={task.id} className={task.days_remaining <= 3 ? "border-red-500/30" : task.days_remaining <= 7 ? "border-amber-500/20" : ""}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-medium text-sm">{task.title}</p>
                        <Badge variant="outline" className={`text-xs ${priorityColors[task.priority]}`}>
                          {task.priority}
                        </Badge>
                        <Badge variant="outline" className={`text-xs ${statusColors[task.status] || statusColors.pending}`}>
                          {task.status.replace("_", " ")}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <BookOpen className="h-3 w-3" /> {task.category}
                        </span>
                        <span className="flex items-center gap-1">
                          <Settings className="h-3 w-3" /> {task.assigned_to}
                        </span>
                      </div>
                    </div>
                    <div className="text-right ml-4 shrink-0">
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3 text-muted-foreground" />
                        <span className={`text-sm font-semibold ${task.days_remaining <= 3 ? "text-red-400" : task.days_remaining <= 7 ? "text-amber-400" : "text-muted-foreground"}`}>
                          {task.days_remaining}d remaining
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">{task.deadline}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-20" />)}
          </div>
        )}
      </div>
    </div>
  );
}
