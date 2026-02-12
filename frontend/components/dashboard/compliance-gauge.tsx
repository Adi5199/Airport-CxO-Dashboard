"use client";

interface ComplianceGaugeProps {
  value: number;
  target?: number;
  title: string;
  size?: number;
}

export function ComplianceGauge({ value, target = 95, title, size = 160 }: ComplianceGaugeProps) {
  const pct = Math.min(100, Math.max(0, value));
  const radius = (size - 20) / 2;
  const circumference = 2 * Math.PI * radius * 0.75; // 270 degree arc
  const offset = circumference - (pct / 100) * circumference;

  const color = value >= target ? "#22c55e" : value >= target - 5 ? "#eab308" : "#ef4444";

  return (
    <div className="flex flex-col items-center gap-2">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* Background arc */}
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke="currentColor" className="text-muted/30"
          strokeWidth={10} strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference * 0.25}
          transform={`rotate(135 ${size / 2} ${size / 2})`}
        />
        {/* Value arc */}
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke={color}
          strokeWidth={10} strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset + circumference * 0.25}
          transform={`rotate(135 ${size / 2} ${size / 2})`}
          className="transition-all duration-700"
        />
        {/* Value text */}
        <text x={size / 2} y={size / 2 - 5} textAnchor="middle" className="fill-foreground text-2xl font-bold" fontSize="24">
          {value.toFixed(1)}%
        </text>
        <text x={size / 2} y={size / 2 + 15} textAnchor="middle" className="fill-muted-foreground" fontSize="11">
          Target: {target}%
        </text>
      </svg>
      <p className="text-sm font-medium text-muted-foreground">{title}</p>
    </div>
  );
}
