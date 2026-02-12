"use client";
import { PieChart as RechartsPie, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CHART_COLORS, CHART_THEME } from "@/lib/constants";

interface PieChartProps {
  data: { name: string; value: number }[];
  title: string;
  height?: number;
}

const COLORS = [CHART_COLORS.primary, CHART_COLORS.secondary, CHART_COLORS.success, CHART_COLORS.purple, CHART_COLORS.warning, CHART_COLORS.info];

export function PieChartCard({ data, title, height = 300 }: PieChartProps) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={height}>
          <RechartsPie>
            <Pie
              data={data}
              cx="50%" cy="50%"
              innerRadius={60} outerRadius={90}
              dataKey="value"
              nameKey="name"
              label={({ name, percent }: any) => `${name} ${(percent * 100).toFixed(0)}%`}
              labelLine={false}
              fontSize={11}
              fill={CHART_THEME.legendText}
            >
              {data.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip contentStyle={{ background: CHART_THEME.tooltipBg, border: `1px solid ${CHART_THEME.tooltipBorder}`, borderRadius: "8px", fontSize: 12, color: CHART_THEME.tooltipText }} itemStyle={{ color: CHART_THEME.tooltipText }} />
            <Legend wrapperStyle={{ color: CHART_THEME.legendText }} />
          </RechartsPie>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
