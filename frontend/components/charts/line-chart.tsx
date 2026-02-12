"use client";
import { LineChart as RechartsLine, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Legend } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CHART_COLORS, CHART_THEME } from "@/lib/constants";

interface LineChartProps {
  data: any[];
  xKey: string;
  lines: { key: string; color?: string; name: string }[];
  title: string;
  height?: number;
  targetLine?: { value: number; label: string };
  yAxisLabel?: string;
}

export function LineChartCard({ data, xKey, lines, title, height = 300, targetLine, yAxisLabel }: LineChartProps) {
  const colors = [CHART_COLORS.primary, CHART_COLORS.secondary, CHART_COLORS.success, CHART_COLORS.purple];

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={height}>
          <RechartsLine data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke={CHART_THEME.grid} />
            <XAxis dataKey={xKey} tick={{ fontSize: 11, fill: CHART_THEME.axis }} tickFormatter={(v: string) => v?.slice(5) || v} />
            <YAxis tick={{ fontSize: 11, fill: CHART_THEME.axis }} label={yAxisLabel ? { value: yAxisLabel, angle: -90, position: "insideLeft", fill: CHART_THEME.axis, fontSize: 11 } : undefined} />
            <Tooltip contentStyle={{ background: CHART_THEME.tooltipBg, border: `1px solid ${CHART_THEME.tooltipBorder}`, borderRadius: "8px", fontSize: 12, color: CHART_THEME.tooltipText }} labelStyle={{ color: CHART_THEME.tooltipLabel }} itemStyle={{ color: CHART_THEME.tooltipText }} />
            {lines.length > 1 && <Legend wrapperStyle={{ color: CHART_THEME.legendText }} />}
            {targetLine && <ReferenceLine y={targetLine.value} stroke="#ef4444" strokeDasharray="5 5" label={{ value: targetLine.label, fill: "#ef4444", fontSize: 11 }} />}
            {lines.map((line, i) => (
              <Line key={line.key} type="monotone" dataKey={line.key} stroke={line.color || colors[i % colors.length]} strokeWidth={2} dot={{ r: 3 }} name={line.name} />
            ))}
          </RechartsLine>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
