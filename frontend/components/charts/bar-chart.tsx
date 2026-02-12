"use client";
import { BarChart as RechartsBar, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Cell } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CHART_THEME } from "@/lib/constants";

interface BarChartProps {
  data: any[];
  categoryKey: string;
  valueKey: string;
  title: string;
  color?: string;
  height?: number;
  layout?: "horizontal" | "vertical";
  threshold?: number;
  thresholdLabel?: string;
}

export function BarChartCard({ data, categoryKey, valueKey, title, color = "#3b82f6", height = 350, layout = "vertical", threshold, thresholdLabel }: BarChartProps) {
  const isHorizontal = layout === "horizontal";

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={height}>
          <RechartsBar data={data} layout={isHorizontal ? "vertical" : "horizontal"}>
            <CartesianGrid strokeDasharray="3 3" stroke={CHART_THEME.grid} />
            {isHorizontal ? (
              <>
                <XAxis type="number" tick={{ fontSize: 11, fill: CHART_THEME.axis }} />
                <YAxis dataKey={categoryKey} type="category" tick={{ fontSize: 11, fill: CHART_THEME.axis }} width={100} />
              </>
            ) : (
              <>
                <XAxis dataKey={categoryKey} tick={{ fontSize: 11, fill: CHART_THEME.axis }} />
                <YAxis tick={{ fontSize: 11, fill: CHART_THEME.axis }} />
              </>
            )}
            <Tooltip contentStyle={{ background: CHART_THEME.tooltipBg, border: `1px solid ${CHART_THEME.tooltipBorder}`, borderRadius: "8px", fontSize: 12, color: CHART_THEME.tooltipText }} labelStyle={{ color: CHART_THEME.tooltipLabel }} itemStyle={{ color: CHART_THEME.tooltipText }} />
            {threshold !== undefined && (
              isHorizontal
                ? <ReferenceLine x={threshold} stroke="#ef4444" strokeDasharray="5 5" label={{ value: thresholdLabel || `${threshold}`, fill: "#ef4444", fontSize: 11 }} />
                : <ReferenceLine y={threshold} stroke="#ef4444" strokeDasharray="5 5" label={{ value: thresholdLabel || `${threshold}`, fill: "#ef4444", fontSize: 11 }} />
            )}
            <Bar dataKey={valueKey} radius={[4, 4, 0, 0]}>
              {data.map((entry, i) => (
                <Cell
                  key={i}
                  fill={threshold !== undefined ? ((entry[valueKey] as number) > threshold ? "#ef4444" : "#22c55e") : color}
                />
              ))}
            </Bar>
          </RechartsBar>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
