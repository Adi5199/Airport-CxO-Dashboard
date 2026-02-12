"use client";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, ReferenceLine } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CHART_THEME } from "@/lib/constants";

interface GroupedBarChartProps {
  data: any[];
  xKey: string;
  bars: { key: string; color: string; name: string }[];
  title: string;
  height?: number;
  targetLine?: { value: number; label: string };
}

export function GroupedBarChart({ data, xKey, bars, title, height = 350, targetLine }: GroupedBarChartProps) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={height}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke={CHART_THEME.grid} />
            <XAxis dataKey={xKey} tick={{ fontSize: 11, fill: CHART_THEME.axis }} tickFormatter={(v: string) => v?.slice(5) || v} />
            <YAxis tick={{ fontSize: 11, fill: CHART_THEME.axis }} />
            <Tooltip contentStyle={{ background: CHART_THEME.tooltipBg, border: `1px solid ${CHART_THEME.tooltipBorder}`, borderRadius: "8px", fontSize: 12, color: CHART_THEME.tooltipText }} labelStyle={{ color: CHART_THEME.tooltipLabel }} itemStyle={{ color: CHART_THEME.tooltipText }} />
            <Legend wrapperStyle={{ color: CHART_THEME.legendText }} />
            {targetLine && <ReferenceLine y={targetLine.value} stroke="#ef4444" strokeDasharray="5 5" label={{ value: targetLine.label, fill: "#ef4444", fontSize: 11 }} />}
            {bars.map((bar) => (
              <Bar key={bar.key} dataKey={bar.key} fill={bar.color} name={bar.name} radius={[4, 4, 0, 0]} />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
