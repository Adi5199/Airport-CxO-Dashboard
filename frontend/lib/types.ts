export interface OverviewKPIs {
  total_pax: number;
  domestic_pax: number;
  international_pax: number;
  pax_vs_7day_pct: number;
  total_atm: number;
  queue_compliance_pct: number;
  compliance_delta: number;
  voc_ratio: number;
  total_complaints: number;
  total_compliments: number;
  otp_pct: number;
  baggage_delivery_pct: number;
  first_bag_minutes: number;
  last_bag_minutes: number;
  safety_issues: number;
  slot_adherence_pct: number;
}

export interface TrendPoint {
  date: string;
  pax_count?: number;
  atm_count?: number;
}

export interface TerminalBreakdown {
  terminal: string;
  flow: string;
  pax_count: number;
}

export interface ZoneCompliance {
  zone: string;
  actual_compliance_pct: number;
}

export interface QueueAlert {
  zone: string;
  time_window: string;
  compliance: number;
  pax_affected: number;
  variance: number;
}

export interface SecurityAlert {
  lane: string;
  terminal: string;
  reject_rate: number;
  reject_count: number;
}

export interface QueueStatus {
  overall_compliance: number;
  zones_below_target: number;
  total_zones: number;
  pax_affected: number;
  target_achievement_pct: number;
}

export interface RootCause {
  zone: string;
  time_window: string;
  primary_issue: string;
  factors: string[];
  impact: string;
  recommendations: string[];
  severity: string;
}

export interface ZoneDetail {
  zone: string;
  avg_compliance: number;
  threshold_minutes: number;
  total_pax: number;
  avg_wait_time: number;
  time_series: {
    time_window: string;
    actual_compliance_pct: number;
    pax_total: number;
    avg_wait_time_min: number;
  }[];
}

export interface HeatmapData {
  zones: string[];
  time_windows: string[];
  values: number[][];
}

export interface SecuritySummary {
  total_cleared: number;
  avg_reject_rate: number;
  high_reject_lanes_count: number;
}

export interface LaneData {
  lane: string;
  terminal: string;
  lane_group: string;
  cleared_volume: number;
  reject_count: number;
  reject_rate_pct: number;
  total_scanned: number;
  avg_throughput_per_hour: number;
}

export interface BeltData {
  belt: string;
  belt_type: string;
  utilization_pct: number;
  flights: number;
  pax: number;
}

export interface GateData {
  gate: string;
  terminal: string;
  boarding_mode: string;
  flights: number;
  pax: number;
  pax_per_flight: number;
}

export interface BoardingMixEntry {
  boarding_mode: string;
  flights: number;
  pax: number;
  pax_pct: number;
}

export interface DemoPrompt {
  key: string;
  label: string;
  prompt: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface VocDaily {
  date: string;
  complaints: number;
  compliments: number;
  ratio: number;
}

export interface BiometricDaily {
  date: string;
  terminal: string;
  adoption_pct: number;
  success_rate: number;
  total_eligible: number;
  registrations: number;
}

export interface BiometricChannel {
  channel: string;
  registrations: number;
}

export interface VocMessage {
  terminal: string;
  department: string;
  media: string;
  message: string;
  sentiment: string;
}

export interface ComplianceTableRow {
  zone: string;
  terminal: string;
  time_window: string;
  actual_compliance_pct: number;
  target_compliance_pct: number;
  variance_from_target: number;
  pax_total: number;
  avg_wait_time_min: number;
}

export interface TrafficParticle {
  id: number;
  x: number;
  y: number;
  progress: number;
  opacity: number;
  size: number;
}

export interface TrafficSimState {
  particles: TrafficParticle[];
  heatmapGrid: number[][];
  passengersArrived: number;
  totalPassengers: number;
  elapsedMs: number;
  isComplete: boolean;
  congestionLevel: "low" | "medium" | "high";
}
