"use client";
import { AreaChart as RechartsArea, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CHART_THEME } from "@/lib/constants";

interface AreaChartProps {
  data: any[];
  xKey: string;
  yKey: string;
  title: string;
  color?: string;
  height?: number;
  targetLine?: { value: number; label: string };
}

export function AreaChartCard({ data, xKey, yKey, title, color = "#3b82f6", height = 300, targetLine }: AreaChartProps) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={height}>
          <RechartsArea data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke={CHART_THEME.grid} />
            <XAxis dataKey={xKey} tick={{ fontSize: 11, fill: CHART_THEME.axis }} tickFormatter={(v: string) => v?.slice(5) || v} />
            <YAxis tick={{ fontSize: 11, fill: CHART_THEME.axis }} />
            <Tooltip contentStyle={{ background: CHART_THEME.tooltipBg, border: `1px solid ${CHART_THEME.tooltipBorder}`, borderRadius: "8px", fontSize: 12, color: CHART_THEME.tooltipText }} labelStyle={{ color: CHART_THEME.tooltipLabel }} itemStyle={{ color: CHART_THEME.tooltipText }} />
            {targetLine && <ReferenceLine y={targetLine.value} stroke="#ef4444" strokeDasharray="5 5" label={{ value: targetLine.label, fill: "#ef4444", fontSize: 11 }} />}
            <Area type="monotone" dataKey={yKey} stroke={color} fill={color} fillOpacity={0.15} strokeWidth={2} dot={{ r: 3 }} />
          </RechartsArea>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
