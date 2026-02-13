"use client";
import { useState } from "react";
import { useApi } from "@/hooks/use-api";
import { KpiCard } from "@/components/dashboard/kpi-card";
import { ComplianceGauge } from "@/components/dashboard/compliance-gauge";
import { SeverityBadge } from "@/components/dashboard/severity-badge";
import { LineChartCard } from "@/components/charts/line-chart";
import { BarChartCard } from "@/components/charts/bar-chart";
import { HeatmapChart } from "@/components/charts/heatmap-chart";
import { AlertCard } from "@/components/dashboard/alert-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { DEFAULT_REPORT_DATE } from "@/lib/constants";
import { fetchApi } from "@/lib/api";
import { ShareButton } from "@/components/dashboard/share-button";
import type { QueueStatus, ZoneDetail, HeatmapData, RootCause, ComplianceTableRow, SecuritySummary, LaneData } from "@/lib/types";
import { Search, CheckCircle, AlertTriangle, Lightbulb } from "lucide-react";

type SubTab = "departure-entry" | "checkin" | "security";

export default function QueuePerformancePage() {
  const date = DEFAULT_REPORT_DATE;
  const [terminalFilter, setTerminalFilter] = useState<string>("T1,T2");
  const [subTab, setSubTab] = useState<SubTab>("checkin");
  const [selectedZone, setSelectedZone] = useState("Check-in 34-86");
  const [rootCause, setRootCause] = useState<RootCause | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  const { data: status, isLoading } = useApi<QueueStatus>("/api/queue/status", { date, terminals: terminalFilter });
  const { data: zones } = useApi<{ zones: string[] }>("/api/queue/zones", { date, terminals: terminalFilter });
  const { data: zoneDetail } = useApi<ZoneDetail>("/api/queue/zone-detail", { date, zone: selectedZone, terminals: terminalFilter });
  const { data: heatmap } = useApi<HeatmapData>("/api/queue/heatmap", { date, terminals: terminalFilter });
  const { data: tableData } = useApi<{ data: ComplianceTableRow[] }>("/api/queue/table", { date, terminals: terminalFilter });

  const { data: secSummary } = useApi<SecuritySummary>("/api/security/summary", { date, terminals: terminalFilter });
  const { data: lanesData } = useApi<{ data: LaneData[] }>("/api/security/lanes", { date, terminals: terminalFilter });
  const { data: highReject } = useApi<{ lanes: { lane: string; terminal: string; reject_rate_pct: number; reject_count: number; cleared_volume: number }[] }>("/api/security/high-reject", { date, terminals: terminalFilter });

  const clearedData = lanesData?.data.map((l) => ({ lane: l.lane, cleared_volume: l.cleared_volume })).sort((a, b) => b.cleared_volume - a.cleared_volume) || [];
  const rejectData = lanesData?.data.map((l) => ({ lane: l.lane, reject_rate_pct: l.reject_rate_pct })).sort((a, b) => a.reject_rate_pct - b.reject_rate_pct) || [];

  function getFilteredZones(tab: SubTab) {
    return zones?.zones.filter((z) => {
      const lower = z.toLowerCase();
      if (tab === "departure-entry") return lower.includes("departure") || lower.includes("entry") || lower.includes("de-");
      if (tab === "checkin") return lower.includes("check-in") || lower.includes("checkin");
      if (tab === "security") return lower.includes("security");
      return true;
    }) || zones?.zones || [];
  }

  const filteredZones = getFilteredZones(subTab);

  function handleTerminalChange(value: string) {
    setTerminalFilter(value);
    setRootCause(null);
  }

  function handleTabChange(tab: SubTab) {
    setSubTab(tab);
    setRootCause(null);
    const newZones = getFilteredZones(tab);
    if (newZones.length > 0) setSelectedZone(newZones[0]);
  }

  async function analyzeRootCause() {
    setAnalyzing(true);
    try {
      const result = await fetchApi<RootCause>("/api/queue/root-cause", { date, zone: selectedZone, time_window: "1400-1600", terminals: terminalFilter });
      setRootCause(result);
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Queue Performance</h1>
          <p className="text-muted-foreground">Queue monitoring, security operations & AI-powered analysis</p>
        </div>
        <ShareButton title="Queue Performance Report" />
      </div>

      {/* Terminal Filter + Sub-tabs */}
      <div className="flex items-center gap-2 flex-wrap">
        <div className="flex items-center gap-2">
          {[
            { label: "Overall", value: "T1,T2" },
            { label: "Terminal 1", value: "T1" },
            { label: "Terminal 2", value: "T2" },
          ].map((f) => (
            <Button key={f.value} variant={terminalFilter === f.value ? "default" : "outline"} size="sm" onClick={() => handleTerminalChange(f.value)}>
              {f.label}
            </Button>
          ))}
        </div>
        <div className="h-6 w-px bg-border mx-2" />
        <div className="flex items-center gap-2">
          {[
            { label: "Departure Entry", value: "departure-entry" as SubTab },
            { label: "Check-in", value: "checkin" as SubTab },
            { label: "Security", value: "security" as SubTab },
          ].map((t) => (
            <Button key={t.value} variant={subTab === t.value ? "secondary" : "ghost"} size="sm" onClick={() => handleTabChange(t.value)}>
              {t.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Queue KPIs */}
      {isLoading ? (
        <div className="grid grid-cols-4 gap-4">{Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-24" />)}</div>
      ) : status ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiCard title="Overall Performance" value={status.overall_compliance} suffix="%" delta={status.overall_compliance - 95} deltaLabel="vs target" accentColor={status.overall_compliance >= 95 ? "green" : "red"} />
          <KpiCard title="Zones Below Target" value={`${status.zones_below_target}/${status.total_zones}`} accentColor={status.zones_below_target > 0 ? "red" : "green"} />
          <KpiCard title="PAX Affected" value={status.pax_affected} accentColor="orange" />
          <KpiCard title="Target Achievement" value={status.target_achievement_pct} suffix="%" accentColor={status.target_achievement_pct >= 75 ? "green" : "red"} />
        </div>
      ) : null}

      {/* Security KPIs (merged) */}
      {secSummary && (
        <div className="grid grid-cols-3 gap-4">
          <KpiCard title="Security - Total Cleared" value={secSummary.total_cleared} accentColor="blue" />
          <KpiCard title="Avg Reject Rate" value={secSummary.avg_reject_rate} suffix="%" accentColor={secSummary.avg_reject_rate > 8 ? "red" : "green"} />
          <KpiCard title="High Reject Lanes" value={secSummary.high_reject_lanes_count} accentColor={secSummary.high_reject_lanes_count > 0 ? "red" : "green"} />
        </div>
      )}

      {/* Root Cause Analysis */}
      <Card className="border-blue-500/30">
        <CardHeader>
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Search className="h-4 w-4" /> AI-Powered Root Cause Analysis
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">Analyze queue performance issues with AI drill-down.</p>
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
                  <span className="font-semibold text-sm">Recommended Actions</span>
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
          {filteredZones.length > 0 && (
            <Select value={selectedZone} onValueChange={setSelectedZone}>
              <SelectTrigger><SelectValue placeholder="Select zone" /></SelectTrigger>
              <SelectContent>
                {filteredZones.map((z) => <SelectItem key={z} value={z}>{z}</SelectItem>)}
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
              lines={[{ key: "actual_compliance_pct", name: "Performance %", color: "#3b82f6" }]}
              title={`${selectedZone} - Performance by Time Window`}
              targetLine={{ value: 95, label: "Target: 95%" }}
              height={350}
            />
          )}
        </div>
      </div>

      {/* Security Lane Charts - shown when Security tab is active */}
      {subTab === "security" && (
        <>
          <h3 className="text-lg font-semibold">Security Lane Performance</h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <BarChartCard data={clearedData} categoryKey="lane" valueKey="cleared_volume" title="Cleared Volume by Lane" layout="horizontal" color="#3b82f6" height={400} />
            <BarChartCard data={rejectData} categoryKey="lane" valueKey="reject_rate_pct" title="Reject Rate by Lane (%)" layout="horizontal" threshold={8} thresholdLabel="Alert: 8%" height={400} />
          </div>
          {highReject && highReject.lanes.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-lg font-semibold">High Reject Rate Lanes (&gt;8%)</h3>
              {highReject.lanes.map((lane, i) => (
                <AlertCard key={i} variant="error" title={`${lane.lane} (${lane.terminal})`}>
                  <p>{lane.reject_rate_pct}% reject rate | {lane.reject_count} rejections | {lane.cleared_volume.toLocaleString()} cleared</p>
                </AlertCard>
              ))}
            </div>
          )}
        </>
      )}

      {/* Heatmap */}
      {heatmap && <HeatmapChart zones={heatmap.zones} timeWindows={heatmap.time_windows} values={heatmap.values} title="Performance Heatmap - All Zones x Time Windows" />}

      {/* Data Table */}
      {tableData && (
        <Card>
          <CardHeader><CardTitle className="text-sm font-medium">Detailed Performance Data</CardTitle></CardHeader>
          <CardContent>
            <div className="max-h-[400px] overflow-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Zone</TableHead>
                    <TableHead>Terminal</TableHead>
                    <TableHead>Time Window</TableHead>
                    <TableHead className="text-right">Performance</TableHead>
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
                      <TableCell className="text-xs">{row.terminal}</TableCell>
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
