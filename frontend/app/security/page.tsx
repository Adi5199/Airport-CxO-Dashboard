"use client";
import { useApi } from "@/hooks/use-api";
import { KpiCard } from "@/components/dashboard/kpi-card";
import { AlertCard } from "@/components/dashboard/alert-card";
import { BarChartCard } from "@/components/charts/bar-chart";
import { PieChartCard } from "@/components/charts/pie-chart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { DEFAULT_REPORT_DATE } from "@/lib/constants";
import type { SecuritySummary, LaneData, BeltData, GateData, BoardingMixEntry } from "@/lib/types";

export default function SecurityPage() {
  const date = DEFAULT_REPORT_DATE;
  const { data: summary, isLoading } = useApi<SecuritySummary>("/api/security/summary", { date });
  const { data: lanesData } = useApi<{ data: LaneData[] }>("/api/security/lanes", { date });
  const { data: highReject } = useApi<{ lanes: { lane: string; terminal: string; reject_rate_pct: number; reject_count: number; cleared_volume: number }[] }>("/api/security/high-reject", { date });
  const { data: baggageData } = useApi<{ summary: { total_flights: number; total_pax: number; avg_pax_per_flight: number }; belts: BeltData[] }>("/api/security/baggage", { date });
  const { data: gatesData } = useApi<{ boarding_mix: Record<string, BoardingMixEntry[]>; gates: GateData[] }>("/api/security/gates", { date });

  const clearedData = lanesData?.data.map((l) => ({ lane: l.lane, cleared_volume: l.cleared_volume })).sort((a, b) => b.cleared_volume - a.cleared_volume) || [];
  const rejectData = lanesData?.data.map((l) => ({ lane: l.lane, reject_rate_pct: l.reject_rate_pct })).sort((a, b) => a.reject_rate_pct - b.reject_rate_pct) || [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Security & Operations</h1>
        <p className="text-muted-foreground">Lane performance, baggage, and gate utilization</p>
      </div>

      {/* Security Summary */}
      <h3 className="text-lg font-semibold">Security Lane Performance</h3>
      {isLoading ? (
        <div className="grid grid-cols-3 gap-4">{Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-24" />)}</div>
      ) : summary ? (
        <div className="grid grid-cols-3 gap-4">
          <KpiCard title="Total Cleared" value={summary.total_cleared} accentColor="blue" />
          <KpiCard title="Avg Reject Rate" value={summary.avg_reject_rate} suffix="%" accentColor={summary.avg_reject_rate > 8 ? "red" : "green"} />
          <KpiCard title="High Reject Lanes" value={summary.high_reject_lanes_count} accentColor={summary.high_reject_lanes_count > 0 ? "red" : "green"} />
        </div>
      ) : null}

      {/* Lane Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <BarChartCard data={clearedData} categoryKey="lane" valueKey="cleared_volume" title="Cleared Volume by Lane" layout="horizontal" color="#3b82f6" height={400} />
        <BarChartCard data={rejectData} categoryKey="lane" valueKey="reject_rate_pct" title="Reject Rate by Lane (%)" layout="horizontal" threshold={8} thresholdLabel="Alert: 8%" height={400} />
      </div>

      {/* High Reject Alerts */}
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

      {/* Baggage */}
      {baggageData && (
        <>
          <h3 className="text-lg font-semibold">Baggage Reclaim Utilization</h3>
          <div className="grid grid-cols-3 gap-4">
            <KpiCard title="Total Flights" value={baggageData.summary.total_flights} accentColor="blue" />
            <KpiCard title="Total PAX" value={baggageData.summary.total_pax} accentColor="blue" />
            <KpiCard title="Avg PAX/Flight" value={baggageData.summary.avg_pax_per_flight} accentColor="blue" />
          </div>
          <BarChartCard
            data={baggageData.belts.map((b) => ({ belt: b.belt, utilization_pct: b.utilization_pct }))}
            categoryKey="belt"
            valueKey="utilization_pct"
            title="Belt Utilization (%)"
            threshold={85}
            thresholdLabel="Optimal: 85%"
            color="#3b82f6"
          />
        </>
      )}

      {/* Gates & Boarding Mode */}
      {gatesData && (
        <>
          <h3 className="text-lg font-semibold">Gate Utilization & Boarding Mode</h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {gatesData.boarding_mix.T1 && (
              <PieChartCard
                data={gatesData.boarding_mix.T1.map((e) => ({ name: e.boarding_mode, value: e.pax }))}
                title="T1 Boarding Mode Mix"
              />
            )}
            {gatesData.boarding_mix.T2 && (
              <PieChartCard
                data={gatesData.boarding_mix.T2.map((e) => ({ name: e.boarding_mode, value: e.pax }))}
                title="T2 Boarding Mode Mix"
              />
            )}
          </div>

          <Card>
            <CardHeader><CardTitle className="text-sm font-medium">Gate-Level Utilization</CardTitle></CardHeader>
            <CardContent>
              <div className="max-h-[300px] overflow-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Gate</TableHead>
                      <TableHead>Terminal</TableHead>
                      <TableHead>Mode</TableHead>
                      <TableHead className="text-right">Flights</TableHead>
                      <TableHead className="text-right">PAX</TableHead>
                      <TableHead className="text-right">PAX/Flight</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {gatesData.gates.slice(0, 20).map((g, i) => (
                      <TableRow key={i}>
                        <TableCell className="text-xs font-medium">{g.gate}</TableCell>
                        <TableCell className="text-xs">{g.terminal}</TableCell>
                        <TableCell className="text-xs">{g.boarding_mode}</TableCell>
                        <TableCell className="text-right text-xs">{g.flights}</TableCell>
                        <TableCell className="text-right text-xs">{g.pax}</TableCell>
                        <TableCell className="text-right text-xs">{g.pax_per_flight}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
