"use client";
import { useState } from "react";
import { useApi } from "@/hooks/use-api";
import { KpiCard } from "@/components/dashboard/kpi-card";
import { AlertCard } from "@/components/dashboard/alert-card";
import { LineChartCard } from "@/components/charts/line-chart";
import { BarChartCard } from "@/components/charts/bar-chart";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DEFAULT_REPORT_DATE } from "@/lib/constants";
import { CheckCircle2, AlertTriangle, XCircle, Users, Clock, MessageSquare, TrendingUp, TrendingDown, ChevronDown, ChevronUp, Timer } from "lucide-react";
import type { ZoneCompliance, QueueAlert } from "@/lib/types";
import { ShareButton } from "@/components/dashboard/share-button";

interface OverviewKPIs {
  total_pax: number;
  domestic_pax: number;
  international_pax: number;
  pax_vs_7day_pct: number;
  total_atm: number;
  queue_compliance_pct: number;
  compliance_delta: number;
  voc_ratio: number;
  total_complaints: number;
  total_compliments: number;
  otp_pct: number;
  baggage_delivery_pct: number;
  first_bag_minutes: number;
  last_bag_minutes: number;
  safety_issues: number;
  slot_adherence_pct: number;
}

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
  otp_pct: number;
  baggage_delivery_pct: number;
  voc_ratio: number;
  voc_sentiment: string;
  total_complaints: number;
  total_compliments: number;
  actions: { priority: string; action: string }[];
}

interface BifurcatedTrend {
  date: string;
  total: number;
  domestic: number;
  international: number;
}

interface SafetyAlert {
  category: string;
  terminal: string;
  severity: string;
  resolved: boolean;
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
  const [terminalFilter, setTerminalFilter] = useState<string>("T1,T2");
  const [alertsExpanded, setAlertsExpanded] = useState(false);

  const filterLabel = terminalFilter === "T1,T2" ? "Overall" : terminalFilter === "T1" ? "Terminal 1" : "Terminal 2";

  const { data: kpis, isLoading: kpiLoading } = useApi<OverviewKPIs>("/api/overview/kpis", { date, terminals: terminalFilter });
  const { data: summary } = useApi<ExecSummary>("/api/overview/executive-summary", { date, terminals: terminalFilter });
  const { data: paxTrend } = useApi<{ data: BifurcatedTrend[] }>("/api/overview/pax-trend", { days: 15, end_date: date, terminals: terminalFilter });
  const { data: atmTrend } = useApi<{ data: BifurcatedTrend[] }>("/api/overview/atm-trend", { days: 15, end_date: date, terminals: terminalFilter });
  const { data: zoneCompliance } = useApi<{ data: ZoneCompliance[] }>("/api/overview/zone-compliance-summary", { date, terminals: terminalFilter });
  const { data: alerts } = useApi<{ queue_alerts: QueueAlert[]; safety_alerts: SafetyAlert[] }>("/api/overview/alerts", { date, terminals: terminalFilter });

  const sc = summary ? statusConfig[summary.status as keyof typeof statusConfig] || statusConfig.on_track : null;

  const d = new Date(date + "T00:00:00");
  const formattedDate = d.toLocaleDateString("en-IN", { weekday: "long", year: "numeric", month: "long", day: "numeric" });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">BIAL Brain & Advisor</h1>
          <p className="text-muted-foreground">Intelligent operational overview for {formattedDate}</p>
        </div>
        <ShareButton title="BIAL Brain & Advisor Overview" />
      </div>

      {/* Terminal Filter */}
      <div className="flex items-center gap-2">
        {[
          { label: "Overall", value: "T1,T2" },
          { label: "Terminal 1", value: "T1" },
          { label: "Terminal 2", value: "T2" },
        ].map((f) => (
          <Button
            key={f.value}
            variant={terminalFilter === f.value ? "default" : "outline"}
            size="sm"
            onClick={() => setTerminalFilter(f.value)}
          >
            {f.label}
          </Button>
        ))}
      </div>

      {/* Executive Summary */}
      {summary && sc && (
        <Card className={`${sc.border} ${sc.bg} border`}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <sc.icon className={`h-6 w-6 ${sc.color}`} />
                <div>
                  <h2 className="text-lg font-semibold">Executive Summary</h2>
                  <p className="text-sm text-muted-foreground">{summary.date} — {filterLabel}</p>
                </div>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium border ${sc.badge}`}>
                {summary.status_label}
              </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="rounded-lg bg-background/50 p-4">
                <div className="flex items-center gap-2 mb-1">
                  <Users className="h-4 w-4 text-blue-400" />
                  <span className="text-xs text-muted-foreground uppercase tracking-wider">Total PAX</span>
                </div>
                <p className="text-2xl font-bold">{summary.total_pax.toLocaleString()}</p>
                <div className="flex items-center gap-1 mt-1">
                  {summary.pax_vs_7day_pct >= 0 ? <TrendingUp className="h-3 w-3 text-emerald-400" /> : <TrendingDown className="h-3 w-3 text-red-400" />}
                  <span className={`text-xs ${summary.pax_vs_7day_pct >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                    {summary.pax_vs_7day_pct >= 0 ? "+" : ""}{summary.pax_vs_7day_pct}% vs 7-day avg
                  </span>
                </div>
              </div>

              <div className="rounded-lg bg-background/50 p-4">
                <div className="flex items-center gap-2 mb-1">
                  <Clock className="h-4 w-4 text-emerald-400" />
                  <span className="text-xs text-muted-foreground uppercase tracking-wider">Queue Performance</span>
                </div>
                <p className="text-2xl font-bold">{summary.queue_compliance}%</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {summary.zones_below_target === 0 ? "All zones on target" : `${summary.zones_below_target} zone${summary.zones_below_target > 1 ? "s" : ""} below target`}
                </p>
              </div>

              <div className="rounded-lg bg-background/50 p-4">
                <div className="flex items-center gap-2 mb-1">
                  <Timer className="h-4 w-4 text-cyan-400" />
                  <span className="text-xs text-muted-foreground uppercase tracking-wider">On-Time Perf.</span>
                </div>
                <p className="text-2xl font-bold">{summary.otp_pct}%</p>
                <p className="text-xs text-muted-foreground mt-1">Flight departure & arrival punctuality</p>
              </div>

              <div className="rounded-lg bg-background/50 p-4">
                <div className="flex items-center gap-2 mb-1">
                  <MessageSquare className="h-4 w-4 text-purple-400" />
                  <span className="text-xs text-muted-foreground uppercase tracking-wider">Customer Voice</span>
                </div>
                <p className="text-2xl font-bold">{summary.voc_ratio}:1</p>
                <p className="text-xs text-muted-foreground mt-1">{summary.total_compliments} compliments / {summary.total_complaints} complaints</p>
              </div>
            </div>

            <div className="rounded-lg bg-background/50 p-4">
              <p className="text-xs text-muted-foreground uppercase tracking-wider mb-2">Priority Actions</p>
              <div className="space-y-2">
                {summary.actions.map((a, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium border ${priorityColors[a.priority] || "bg-muted text-muted-foreground"}`}>{a.priority}</span>
                    <span className="text-sm">{a.action}</span>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* KPI Cards */}
      {kpiLoading ? (
        <div className="grid grid-cols-5 gap-4">{Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-24" />)}</div>
      ) : kpis ? (
        <>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            <KpiCard title="Total PAX" value={kpis.total_pax} delta={kpis.pax_vs_7day_pct} deltaLabel="vs 7-day avg" accentColor="blue" />
            <KpiCard title="ATM" value={kpis.total_atm} accentColor="blue" />
            <KpiCard title="On-Time Performance" value={kpis.otp_pct} suffix="%" accentColor={kpis.otp_pct >= 85 ? "green" : "red"} />
            <KpiCard title="Baggage Delivery" value={kpis.baggage_delivery_pct} suffix="%" accentColor={kpis.baggage_delivery_pct >= 90 ? "green" : "orange"} />
            <KpiCard title="Safety Issues" value={kpis.safety_issues} accentColor={kpis.safety_issues > 3 ? "red" : kpis.safety_issues > 0 ? "orange" : "green"} />
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            <KpiCard title="Queue Performance" value={kpis.queue_compliance_pct} suffix="%" delta={kpis.compliance_delta} deltaLabel="vs target" accentColor={kpis.queue_compliance_pct >= 95 ? "green" : "red"} />
            <KpiCard title="Slot Adherence" value={kpis.slot_adherence_pct} suffix="%" accentColor={kpis.slot_adherence_pct >= 85 ? "green" : "orange"} />
            <KpiCard title="VOC Ratio" value={`${kpis.voc_ratio}:1`} accentColor={kpis.voc_ratio >= 2 ? "green" : "red"} />
            <KpiCard title="First Bag Delivery" value={`${kpis.first_bag_minutes} min`} accentColor={kpis.first_bag_minutes <= 15 ? "green" : "orange"} />
          </div>
        </>
      ) : null}

      {/* Alerts & Anomalies - Collapsed */}
      {alerts && (alerts.queue_alerts.length > 0 || alerts.safety_alerts.length > 0) && (
        <Card>
          <CardHeader className="cursor-pointer" onClick={() => setAlertsExpanded(!alertsExpanded)}>
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-400" />
                Alerts & Anomalies
                <Badge variant="outline" className="ml-2 text-xs">{alerts.queue_alerts.length + alerts.safety_alerts.length}</Badge>
              </CardTitle>
              {alertsExpanded ? <ChevronUp className="h-4 w-4 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
            </div>
          </CardHeader>
          {alertsExpanded && (
            <CardContent className="space-y-3 pt-0">
              {alerts.queue_alerts.map((a, i) => (
                <AlertCard key={i} variant="warning" title={`${a.zone} - ${a.time_window}`}>
                  <p>Performance: {a.compliance}% (Target: 95%) | PAX Affected: {a.pax_affected.toLocaleString()} | Variance: {a.variance}%</p>
                </AlertCard>
              ))}
              {alerts.safety_alerts.map((a, i) => (
                <AlertCard key={`safety-${i}`} variant={a.resolved ? "info" : "error"} title={`${a.category} (${a.terminal})`}>
                  <p>Severity: {a.severity} | Status: {a.resolved ? "Resolved" : "Open"}</p>
                </AlertCard>
              ))}
            </CardContent>
          )}
        </Card>
      )}

      {/* Trends - Bifurcated Dom/Int */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {paxTrend && (
          <LineChartCard
            data={paxTrend.data}
            xKey="date"
            lines={[
              { key: "total", name: "Total", color: "#3b82f6" },
              { key: "domestic", name: "Domestic", color: "#22c55e" },
              { key: "international", name: "International", color: "#f97316" },
            ]}
            title="Daily Passenger Volume (15-Day — Dom/Int)"
            height={300}
          />
        )}
        {atmTrend && (
          <LineChartCard
            data={atmTrend.data}
            xKey="date"
            lines={[
              { key: "total", name: "Total", color: "#8b5cf6" },
              { key: "domestic", name: "Domestic", color: "#22c55e" },
              { key: "international", name: "International", color: "#f97316" },
            ]}
            title="Daily ATM (15-Day — Dom/Int)"
            height={300}
          />
        )}
      </div>

      {/* Zone Compliance */}
      {zoneCompliance && (
        <BarChartCard
          data={zoneCompliance.data}
          categoryKey="zone"
          valueKey="actual_compliance_pct"
          title="Queue Performance by Zone"
          layout="horizontal"
          threshold={95}
          thresholdLabel="Target: 95%"
          height={350}
        />
      )}
    </div>
  );
}
