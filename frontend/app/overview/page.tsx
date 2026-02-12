"use client";
import { useApi } from "@/hooks/use-api";
import { KpiCard } from "@/components/dashboard/kpi-card";
import { AlertCard } from "@/components/dashboard/alert-card";
import { AreaChartCard } from "@/components/charts/area-chart";
import { BarChartCard } from "@/components/charts/bar-chart";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DEFAULT_REPORT_DATE } from "@/lib/constants";
import { CheckCircle2, AlertTriangle, XCircle, Users, Plane, Shield, MessageSquare, TrendingUp, TrendingDown, Clock, ArrowRight } from "lucide-react";
import type { OverviewKPIs, TrendPoint, ZoneCompliance, QueueAlert, SecurityAlert } from "@/lib/types";

interface ExecSummary {
  date: string;
  status: string;
  status_label: string;
  status_detail: string;
  total_pax: number;
  domestic_pax: number;
  international_pax: number;
  pax_vs_7day_pct: number;
  queue_compliance: number;
  zones_below_target: number;
  avg_reject_rate: number;
  high_reject_lanes: number;
  voc_ratio: number;
  voc_sentiment: string;
  total_complaints: number;
  total_compliments: number;
  peak_hours: string[];
  actions: { priority: string; action: string }[];
}

const statusConfig = {
  on_track: { icon: CheckCircle2, color: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/30", badge: "bg-emerald-500/20 text-emerald-400" },
  attention: { icon: AlertTriangle, color: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/30", badge: "bg-amber-500/20 text-amber-400" },
  critical: { icon: XCircle, color: "text-red-400", bg: "bg-red-500/10", border: "border-red-500/30", badge: "bg-red-500/20 text-red-400" },
};

const priorityColors: Record<string, string> = {
  Immediate: "bg-red-500/20 text-red-400 border-red-500/30",
  Today: "bg-amber-500/20 text-amber-400 border-amber-500/30",
  "This Week": "bg-blue-500/20 text-blue-400 border-blue-500/30",
};

export default function OverviewPage() {
  const date = DEFAULT_REPORT_DATE;
  const { data: kpis, isLoading: kpiLoading } = useApi<OverviewKPIs>("/api/overview/kpis", { date });
  const { data: summary } = useApi<ExecSummary>("/api/overview/executive-summary", { date });
  const { data: paxTrend } = useApi<{ data: TrendPoint[] }>("/api/overview/pax-trend", { days: 15, end_date: date });
  const { data: atmTrend } = useApi<{ data: TrendPoint[] }>("/api/overview/atm-trend", { days: 15, end_date: date });
  const { data: zoneCompliance } = useApi<{ data: ZoneCompliance[] }>("/api/overview/zone-compliance-summary", { date });
  const { data: alerts } = useApi<{ queue_alerts: QueueAlert[]; security_alerts: SecurityAlert[] }>("/api/overview/alerts", { date });

  const sc = summary ? statusConfig[summary.status as keyof typeof statusConfig] || statusConfig.on_track : null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Executive Overview</h1>
        <p className="text-muted-foreground">Real-time operational intelligence for January 24, 2026</p>
      </div>

      {/* Executive Summary - CxO Card */}
      {summary && sc && (
        <Card className={`${sc.border} ${sc.bg} border`}>
          <CardContent className="p-6">
            {/* Header row: status + date */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <sc.icon className={`h-6 w-6 ${sc.color}`} />
                <div>
                  <h2 className="text-lg font-semibold">Executive Summary</h2>
                  <p className="text-sm text-muted-foreground">{summary.date}</p>
                </div>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium border ${sc.badge}`}>
                {summary.status_label}
              </span>
            </div>

            {/* Key metrics grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="rounded-lg bg-background/50 p-4">
                <div className="flex items-center gap-2 mb-1">
                  <Users className="h-4 w-4 text-blue-400" />
                  <span className="text-xs text-muted-foreground uppercase tracking-wider">Total PAX</span>
                </div>
                <p className="text-2xl font-bold">{summary.total_pax.toLocaleString()}</p>
                <div className="flex items-center gap-1 mt-1">
                  {summary.pax_vs_7day_pct >= 0 ? (
                    <TrendingUp className="h-3 w-3 text-emerald-400" />
                  ) : (
                    <TrendingDown className="h-3 w-3 text-red-400" />
                  )}
                  <span className={`text-xs ${summary.pax_vs_7day_pct >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                    {summary.pax_vs_7day_pct >= 0 ? "+" : ""}{summary.pax_vs_7day_pct}% vs 7-day avg
                  </span>
                </div>
              </div>

              <div className="rounded-lg bg-background/50 p-4">
                <div className="flex items-center gap-2 mb-1">
                  <Clock className="h-4 w-4 text-emerald-400" />
                  <span className="text-xs text-muted-foreground uppercase tracking-wider">Queue Compliance</span>
                </div>
                <p className="text-2xl font-bold">{summary.queue_compliance}%</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {summary.zones_below_target === 0
                    ? "All zones on target"
                    : `${summary.zones_below_target} zone${summary.zones_below_target > 1 ? "s" : ""} below 95% target`}
                </p>
              </div>

              <div className="rounded-lg bg-background/50 p-4">
                <div className="flex items-center gap-2 mb-1">
                  <Shield className="h-4 w-4 text-amber-400" />
                  <span className="text-xs text-muted-foreground uppercase tracking-wider">Security</span>
                </div>
                <p className="text-2xl font-bold">{summary.avg_reject_rate}%</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Avg reject rate{summary.high_reject_lanes > 0 ? ` | ${summary.high_reject_lanes} lane${summary.high_reject_lanes > 1 ? "s" : ""} flagged` : ""}
                </p>
              </div>

              <div className="rounded-lg bg-background/50 p-4">
                <div className="flex items-center gap-2 mb-1">
                  <MessageSquare className="h-4 w-4 text-purple-400" />
                  <span className="text-xs text-muted-foreground uppercase tracking-wider">Customer Voice</span>
                </div>
                <p className="text-2xl font-bold">{summary.voc_ratio}:1</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {summary.total_compliments} compliments / {summary.total_complaints} complaints
                </p>
              </div>
            </div>

            {/* Bottom row: peak hours + priority actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Peak hours */}
              <div className="rounded-lg bg-background/50 p-4">
                <p className="text-xs text-muted-foreground uppercase tracking-wider mb-2">Peak Hours</p>
                <div className="flex gap-2">
                  {summary.peak_hours.map((h) => (
                    <span key={h} className="px-2 py-1 rounded bg-blue-500/15 text-blue-400 text-sm font-mono font-medium">
                      {h}
                    </span>
                  ))}
                </div>
              </div>

              {/* Priority actions */}
              <div className="md:col-span-2 rounded-lg bg-background/50 p-4">
                <p className="text-xs text-muted-foreground uppercase tracking-wider mb-2">Priority Actions</p>
                <div className="space-y-2">
                  {summary.actions.map((a, i) => (
                    <div key={i} className="flex items-center gap-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium border ${priorityColors[a.priority] || "bg-muted text-muted-foreground"}`}>
                        {a.priority}
                      </span>
                      <span className="text-sm">{a.action}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* KPI Cards */}
      {kpiLoading ? (
        <div className="grid grid-cols-5 gap-4">
          {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-24" />)}
        </div>
      ) : kpis ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <KpiCard title="Total PAX" value={kpis.total_pax} delta={kpis.pax_vs_7day_pct} deltaLabel="vs 7-day avg" accentColor="blue" />
          <KpiCard title="Domestic PAX" value={kpis.domestic_pax} accentColor="green" />
          <KpiCard title="International PAX" value={kpis.international_pax} accentColor="orange" />
          <KpiCard title="Queue Compliance" value={kpis.queue_compliance_pct} suffix="%" delta={kpis.compliance_delta} deltaLabel="vs target" accentColor={kpis.queue_compliance_pct >= 95 ? "green" : "red"} />
          <KpiCard title="VOC Ratio" value={`${kpis.voc_ratio}:1`} accentColor={kpis.voc_ratio >= 2 ? "green" : "red"} />
        </div>
      ) : null}

      {/* Additional KPIs */}
      {kpis && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <KpiCard title="Avg Reject Rate" value={kpis.avg_reject_rate} suffix="%" accentColor={kpis.avg_reject_rate > 8 ? "red" : "green"} />
          <KpiCard title="Biometric Adoption" value={kpis.biometric_adoption_pct} suffix="%" accentColor="purple" />
          <KpiCard title="Complaints" value={kpis.total_complaints} accentColor="red" />
        </div>
      )}

      {/* Trends */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {paxTrend && <AreaChartCard data={paxTrend.data} xKey="date" yKey="pax_count" title="Daily Passenger Volume (15-Day Trend)" color="#3b82f6" />}
        {atmTrend && <AreaChartCard data={atmTrend.data} xKey="date" yKey="atm_count" title="Daily Aircraft Movements (15-Day Trend)" color="#f97316" />}
      </div>

      {/* Zone Compliance */}
      {zoneCompliance && (
        <BarChartCard
          data={zoneCompliance.data}
          categoryKey="zone"
          valueKey="actual_compliance_pct"
          title="Queue Compliance by Zone"
          layout="horizontal"
          threshold={95}
          thresholdLabel="Target: 95%"
          height={350}
        />
      )}

      {/* Alerts */}
      {alerts && (alerts.queue_alerts.length > 0 || alerts.security_alerts.length > 0) && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold">Alerts & Anomalies</h3>
          {alerts.queue_alerts.slice(0, 3).map((a, i) => (
            <AlertCard key={i} variant="warning" title={`${a.zone} - ${a.time_window}`}>
              <p>Compliance: {a.compliance}% (Target: 95%) | Passengers Affected: {a.pax_affected.toLocaleString()} | Variance: {a.variance}%</p>
            </AlertCard>
          ))}
          {alerts.security_alerts.map((a, i) => (
            <AlertCard key={`sec-${i}`} variant="error" title={`${a.lane} (${a.terminal})`}>
              <p>Reject Rate: {a.reject_rate}% | {a.reject_count} rejections</p>
            </AlertCard>
          ))}
        </div>
      )}
    </div>
  );
}
