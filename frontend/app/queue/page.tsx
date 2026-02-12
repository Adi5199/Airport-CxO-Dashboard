"use client";
import { useState } from "react";
import { useApi } from "@/hooks/use-api";
import { KpiCard } from "@/components/dashboard/kpi-card";
import { ComplianceGauge } from "@/components/dashboard/compliance-gauge";
import { SeverityBadge } from "@/components/dashboard/severity-badge";
import { LineChartCard } from "@/components/charts/line-chart";
import { HeatmapChart } from "@/components/charts/heatmap-chart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { DEFAULT_REPORT_DATE } from "@/lib/constants";
import { fetchApi } from "@/lib/api";
import type { QueueStatus, ZoneDetail, HeatmapData, RootCause, ComplianceTableRow } from "@/lib/types";
import { Search, CheckCircle, AlertTriangle, Lightbulb } from "lucide-react";

export default function QueuePage() {
  const date = DEFAULT_REPORT_DATE;
  const [selectedZone, setSelectedZone] = useState("Check-in 34-86");
  const [rootCause, setRootCause] = useState<RootCause | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  const { data: status, isLoading } = useApi<QueueStatus>("/api/queue/status", { date });
  const { data: zones } = useApi<{ zones: string[] }>("/api/queue/zones", { date });
  const { data: zoneDetail } = useApi<ZoneDetail>("/api/queue/zone-detail", { date, zone: selectedZone });
  const { data: heatmap } = useApi<HeatmapData>("/api/queue/heatmap", { date });
  const { data: tableData } = useApi<{ data: ComplianceTableRow[] }>("/api/queue/table", { date });

  async function analyzeRootCause() {
    setAnalyzing(true);
    try {
      const result = await fetchApi<RootCause>("/api/queue/root-cause", { date, zone: "Check-in 34-86", time_window: "1400-1600" });
      setRootCause(result);
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Queue Time Compliance</h1>
        <p className="text-muted-foreground">Live monitoring & AI-powered root cause analysis</p>
      </div>

      {/* Status KPIs */}
      {isLoading ? (
        <div className="grid grid-cols-4 gap-4">{Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-24" />)}</div>
      ) : status ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiCard title="Overall Compliance" value={status.overall_compliance} suffix="%" delta={status.overall_compliance - 95} deltaLabel="vs target" accentColor={status.overall_compliance >= 95 ? "green" : "red"} />
          <KpiCard title="Zones Below Target" value={`${status.zones_below_target}/${status.total_zones}`} accentColor={status.zones_below_target > 0 ? "red" : "green"} />
          <KpiCard title="PAX Affected" value={status.pax_affected} accentColor="orange" />
          <KpiCard title="Target Achievement" value={status.target_achievement_pct} suffix="%" accentColor={status.target_achievement_pct >= 75 ? "green" : "red"} />
        </div>
      ) : null}

      {/* Root Cause Analysis */}
      <Card className="border-blue-500/30">
        <CardHeader>
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Search className="h-4 w-4" /> AI-Powered Root Cause Analysis
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Analyzing queue compliance drop on January 24, 2026. Click below to trigger AI-powered drill-down analysis.
          </p>
          <Button onClick={analyzeRootCause} disabled={analyzing} className="w-full" size="lg">
            {analyzing ? "Analyzing..." : "Analyze Root Cause"}
          </Button>

          {rootCause && (
            <div className="mt-4 space-y-4">
              <div className="flex items-start justify-between">
                <div className="space-y-3 flex-1">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-red-500" />
                    <span className="font-semibold">Primary Issue:</span>
                    <span className="text-sm">{rootCause.primary_issue}</span>
                  </div>
                  <div>
                    <p className="font-semibold text-sm mb-2">Contributing Factors:</p>
                    <ol className="list-decimal list-inside space-y-1 text-sm text-muted-foreground">
                      {rootCause.factors.map((f, i) => <li key={i}>{f}</li>)}
                    </ol>
                  </div>
                  <p className="text-sm"><span className="font-semibold">Impact:</span> {rootCause.impact}</p>
                </div>
                <div className="ml-4 flex flex-col items-center gap-2 p-4 rounded-lg bg-red-500/10 border border-red-500/30">
                  <span className="text-xs font-medium text-muted-foreground uppercase">Severity</span>
                  <SeverityBadge severity={rootCause.severity} className="text-lg px-4 py-1" />
                </div>
              </div>

              <div className="border-t border-border pt-4">
                <div className="flex items-center gap-2 mb-3">
                  <Lightbulb className="h-4 w-4 text-emerald-500" />
                  <span className="font-semibold text-sm">Recommended Actions (Deploy Today)</span>
                </div>
                <div className="grid gap-2">
                  {rootCause.recommendations.map((r, i) => (
                    <div key={i} className="flex items-start gap-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-3">
                      <CheckCircle className="h-4 w-4 text-emerald-500 mt-0.5 shrink-0" />
                      <span className="text-sm">{r}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Zone Detail */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="space-y-4">
          {zones && (
            <Select value={selectedZone} onValueChange={setSelectedZone}>
              <SelectTrigger><SelectValue placeholder="Select zone" /></SelectTrigger>
              <SelectContent>
                {zones.zones.map((z) => <SelectItem key={z} value={z}>{z}</SelectItem>)}
              </SelectContent>
            </Select>
          )}
          {zoneDetail && (
            <>
              <ComplianceGauge value={zoneDetail.avg_compliance} title={selectedZone} />
              <div className="space-y-2">
                <KpiCard title="Threshold" value={`${zoneDetail.threshold_minutes} min`} accentColor="blue" />
                <KpiCard title="Total PAX" value={zoneDetail.total_pax} accentColor="blue" />
                <KpiCard title="Avg Wait Time" value={`${zoneDetail.avg_wait_time} min`} accentColor={zoneDetail.avg_wait_time > zoneDetail.threshold_minutes ? "red" : "green"} />
              </div>
            </>
          )}
        </div>
        <div className="lg:col-span-2">
          {zoneDetail && (
            <LineChartCard
              data={zoneDetail.time_series}
              xKey="time_window"
              lines={[{ key: "actual_compliance_pct", name: "Compliance %", color: "#3b82f6" }]}
              title={`${selectedZone} - Compliance by Time Window`}
              targetLine={{ value: 95, label: "Target: 95%" }}
              height={350}
            />
          )}
        </div>
      </div>

      {/* Heatmap */}
      {heatmap && (
        <HeatmapChart zones={heatmap.zones} timeWindows={heatmap.time_windows} values={heatmap.values} title="Compliance Heatmap - All Zones x Time Windows" />
      )}

      {/* Data Table */}
      {tableData && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Detailed Compliance Data</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="max-h-[400px] overflow-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Zone</TableHead>
                    <TableHead>Time Window</TableHead>
                    <TableHead className="text-right">Compliance</TableHead>
                    <TableHead className="text-right">Target</TableHead>
                    <TableHead className="text-right">Variance</TableHead>
                    <TableHead className="text-right">PAX</TableHead>
                    <TableHead className="text-right">Avg Wait</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {tableData.data.map((row, i) => (
                    <TableRow key={i} className={row.actual_compliance_pct < 95 ? "bg-red-500/5" : ""}>
                      <TableCell className="text-xs">{row.zone}</TableCell>
                      <TableCell className="text-xs">{row.time_window}</TableCell>
                      <TableCell className={`text-right text-xs font-medium ${row.actual_compliance_pct < 95 ? "text-red-400" : "text-emerald-400"}`}>{row.actual_compliance_pct}%</TableCell>
                      <TableCell className="text-right text-xs">{row.target_compliance_pct}%</TableCell>
                      <TableCell className={`text-right text-xs ${row.variance_from_target < 0 ? "text-red-400" : ""}`}>{row.variance_from_target}%</TableCell>
                      <TableCell className="text-right text-xs">{row.pax_total.toLocaleString()}</TableCell>
                      <TableCell className="text-right text-xs">{row.avg_wait_time_min} min</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
