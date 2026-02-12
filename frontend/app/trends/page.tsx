"use client";
import { useApi } from "@/hooks/use-api";
import { AreaChartCard } from "@/components/charts/area-chart";
import { LineChartCard } from "@/components/charts/line-chart";
import { PieChartCard } from "@/components/charts/pie-chart";
import { GroupedBarChart } from "@/components/charts/grouped-bar-chart";
import { BarChartCard } from "@/components/charts/bar-chart";
import { AlertCard } from "@/components/dashboard/alert-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DEFAULT_REPORT_DATE, CHART_COLORS } from "@/lib/constants";
import type { BiometricDaily, BiometricChannel, VocDaily, VocMessage } from "@/lib/types";

export default function TrendsPage() {
  const date = DEFAULT_REPORT_DATE;

  // PAX trends - by type
  const { data: paxByType } = useApi<{ data: { date: string; passenger_type: string; pax_count: number }[] }>("/api/trends/passenger", { days: 30, end_date: date, group_by: "passenger_type" });

  // PAX by terminal
  const { data: paxByTerminal } = useApi<{ data: { date: string; terminal: string; pax_count: number }[] }>("/api/trends/passenger", { days: 30, end_date: date, group_by: "terminal" });

  // Biometric
  const { data: bioData } = useApi<{ daily: BiometricDaily[]; channels: BiometricChannel[] }>("/api/trends/biometric", { days: 30, end_date: date });

  // VOC
  const { data: vocData } = useApi<{ daily: VocDaily[]; by_terminal: { terminal: string; complaints: number; compliments: number; ratio: number }[]; by_media: { media_type: string; total_feedback: number }[]; recent_messages: VocMessage[] }>("/api/trends/voc", { days: 30, end_date: date });

  // Transform PAX data for area chart - pivot by type
  const paxAreaData = (() => {
    if (!paxByType) return [];
    const grouped: Record<string, Record<string, number>> = {};
    for (const row of paxByType.data) {
      if (!grouped[row.date]) grouped[row.date] = { date: row.date } as any;
      grouped[row.date][row.passenger_type] = row.pax_count;
    }
    return Object.values(grouped);
  })();

  // Transform PAX by terminal
  const paxTerminalData = (() => {
    if (!paxByTerminal) return [];
    const grouped: Record<string, Record<string, number>> = {};
    for (const row of paxByTerminal.data) {
      if (!grouped[row.date]) grouped[row.date] = { date: row.date } as any;
      grouped[row.date][row.terminal] = row.pax_count;
    }
    return Object.values(grouped);
  })();

  // Biometric by terminal pivot
  const bioChartData = (() => {
    if (!bioData) return [];
    const grouped: Record<string, Record<string, number | string>> = {};
    for (const row of bioData.daily) {
      if (!grouped[row.date]) grouped[row.date] = { date: row.date };
      grouped[row.date][`${row.terminal}_adoption`] = row.adoption_pct;
      grouped[row.date][`${row.terminal}_success`] = row.success_rate;
    }
    return Object.values(grouped);
  })();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Trends & Analytics</h1>
        <p className="text-muted-foreground">30-day historical trends and analysis</p>
      </div>

      {/* PAX Trends */}
      <h3 className="text-lg font-semibold">Passenger Volume Trends</h3>
      {paxAreaData.length > 0 && (
        <LineChartCard
          data={paxAreaData}
          xKey="date"
          lines={[
            { key: "Domestic", name: "Domestic", color: CHART_COLORS.primary },
            { key: "International", name: "International", color: CHART_COLORS.secondary },
          ]}
          title="Daily Passenger Volumes - Domestic vs International (30 Days)"
          height={350}
        />
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {paxTerminalData.length > 0 && (
          <LineChartCard
            data={paxTerminalData}
            xKey="date"
            lines={[
              { key: "T1", name: "T1", color: CHART_COLORS.primary },
              { key: "T2", name: "T2", color: CHART_COLORS.secondary },
            ]}
            title="Passengers by Terminal"
          />
        )}
        {vocData && (
          <LineChartCard
            data={vocData.daily}
            xKey="date"
            lines={[{ key: "ratio", name: "Ratio", color: CHART_COLORS.primary }]}
            title="Compliments:Complaints Ratio Trend"
            targetLine={{ value: 2.0, label: "Target: 2:1" }}
          />
        )}
      </div>

      {/* Biometric Adoption */}
      <h3 className="text-lg font-semibold">Biometric Adoption & Digital Transformation</h3>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {bioChartData.length > 0 && (
          <LineChartCard
            data={bioChartData}
            xKey="date"
            lines={[
              { key: "T1_adoption", name: "T1 Adoption", color: CHART_COLORS.primary },
              { key: "T2_adoption", name: "T2 Adoption", color: CHART_COLORS.secondary },
            ]}
            title="Biometric Adoption Rate (%)"
            targetLine={{ value: 60, label: "Target: 60%" }}
          />
        )}
        {bioData?.channels && bioData.channels.length > 0 && (
          <PieChartCard
            data={bioData.channels.map((c) => ({ name: c.channel, value: c.registrations }))}
            title="Biometric Registrations by Channel (Today)"
          />
        )}
      </div>

      {/* VOC */}
      <h3 className="text-lg font-semibold">Voice of Customer Analysis</h3>
      {vocData && (
        <>
          <GroupedBarChart
            data={vocData.daily}
            xKey="date"
            bars={[
              { key: "complaints", color: CHART_COLORS.danger, name: "Complaints" },
              { key: "compliments", color: CHART_COLORS.success, name: "Compliments" },
            ]}
            title="Daily Complaints vs Compliments"
            height={350}
          />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <GroupedBarChart
              data={vocData.by_terminal}
              xKey="terminal"
              bars={[
                { key: "complaints", color: CHART_COLORS.danger, name: "Complaints" },
                { key: "compliments", color: CHART_COLORS.success, name: "Compliments" },
              ]}
              title="Feedback by Terminal (30-Day Total)"
              height={300}
            />
            {vocData.by_media.length > 0 && (
              <BarChartCard
                data={vocData.by_media}
                categoryKey="media_type"
                valueKey="total_feedback"
                title="Feedback by Channel"
                color={CHART_COLORS.primary}
                height={300}
              />
            )}
          </div>

          {/* Recent messages */}
          {vocData.recent_messages.length > 0 && (
            <Card>
              <CardHeader><CardTitle className="text-sm font-medium">Recent Customer Feedback</CardTitle></CardHeader>
              <CardContent>
                <Tabs defaultValue="negative">
                  <TabsList>
                    <TabsTrigger value="negative">Negative</TabsTrigger>
                    <TabsTrigger value="positive">Positive</TabsTrigger>
                  </TabsList>
                  <TabsContent value="negative" className="space-y-2 mt-3">
                    {vocData.recent_messages.filter((m) => m.sentiment === "negative").map((m, i) => (
                      <AlertCard key={i} variant="warning" title={`${m.terminal} - ${m.department} (${m.media})`}>
                        <p>{m.message}</p>
                      </AlertCard>
                    ))}
                  </TabsContent>
                  <TabsContent value="positive" className="space-y-2 mt-3">
                    {vocData.recent_messages.filter((m) => m.sentiment === "positive").map((m, i) => (
                      <AlertCard key={i} variant="success" title={`${m.terminal} - ${m.department} (${m.media})`}>
                        <p>{m.message}</p>
                      </AlertCard>
                    ))}
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
