"use client";
import { useState, useRef, useCallback, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { TerminalMap } from "@/components/traffic/terminal-map";
import { StatusPanel, GatesLegend } from "@/components/traffic/status-panel";
import { ParticleEngine } from "@/components/traffic/particle-engine";
import { GATES } from "@/components/traffic/terminal-map-data";
import { ShareButton } from "@/components/dashboard/share-button";
import type { TrafficParticle, TrafficSimState } from "@/lib/types";
import { Play, RotateCcw, Zap, Sparkles } from "lucide-react";

const INITIAL_STATE: TrafficSimState = {
  particles: [],
  heatmapGrid: [],
  passengersArrived: 0,
  totalPassengers: 140,
  elapsedMs: 0,
  isComplete: false,
  congestionLevel: "low",
};

function generateInsights(gate: string, passengers: number, congestion: string): string[] {
  const insights: string[] = [];

  if (congestion === "high") {
    insights.push(`High congestion detected near ${gate}. Consider opening adjacent gates or deploying additional ground staff to manage passenger flow.`);
    insights.push(`Recommend activating overflow holding area for ${gate}. Current density exceeds comfortable threshold for smooth boarding.`);
  } else if (congestion === "medium") {
    insights.push(`Moderate foot traffic building toward ${gate}. Boarding is progressing at expected pace — monitor for potential bottlenecks.`);
  }

  if (passengers > 100) {
    insights.push(`${passengers} passengers have reached the gate area. Estimated boarding completion within 5 minutes at current rate.`);
  } else if (passengers > 50) {
    insights.push(`Boarding call is generating steady passenger flow. ${passengers} passengers in gate zone — approximately 60% through the boarding process.`);
  }

  insights.push(`AI Recommendation: For ${gate}, pre-position wheelchair assistance and priority boarding lane staff based on flight manifest data.`);

  if (congestion === "low" && passengers < 30) {
    insights.push(`Passenger flow is within normal parameters. No operational intervention required at this time.`);
  }

  return insights;
}

export default function TrafficMonitoringPage() {
  const [selectedGate, setSelectedGate] = useState("C4");
  const [simState, setSimState] = useState<"idle" | "running" | "complete">("idle");
  const [speedMultiplier, setSpeedMultiplier] = useState(1);
  const [renderState, setRenderState] = useState<TrafficSimState>(INITIAL_STATE);

  const engineRef = useRef<ParticleEngine | null>(null);
  const animFrameRef = useRef<number>(0);

  const animate = useCallback(() => {
    if (!engineRef.current) return;
    const state = engineRef.current.update(performance.now());
    setRenderState(state);
    if (state.isComplete) {
      setSimState("complete");
      return;
    }
    animFrameRef.current = requestAnimationFrame(animate);
  }, []);

  function handleStart() {
    if (simState === "running") return;
    const engine = new ParticleEngine({
      gateId: selectedGate,
      totalPassengers: 140,
      simulationDurationMs: 18000,
      speedMultiplier,
    });
    engineRef.current = engine;
    engine.start(performance.now());
    setSimState("running");
    animFrameRef.current = requestAnimationFrame(animate);
  }

  function handleReset() {
    if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    engineRef.current?.reset();
    engineRef.current = null;
    setSimState("idle");
    setRenderState(INITIAL_STATE);
  }

  function handleSpeedChange(speed: number) {
    setSpeedMultiplier(speed);
    engineRef.current?.setSpeedMultiplier(speed);
  }

  useEffect(() => {
    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      engineRef.current?.reset();
      engineRef.current = null;
    };
  }, []);

  const insights = generateInsights(selectedGate, renderState.passengersArrived, renderState.congestionLevel);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Traffic Monitoring</h1>
          <p className="text-muted-foreground">BIAL Terminal 2 — Boarding Call Simulation</p>
        </div>
        <ShareButton title="Traffic Monitoring" />
      </div>

      {/* Controls */}
      <Card>
        <CardContent className="p-4 flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-muted-foreground uppercase">Gate:</span>
            <Select value={selectedGate} onValueChange={(v) => { setSelectedGate(v); if (simState !== "idle") handleReset(); }} disabled={simState === "running"}>
              <SelectTrigger className="w-[130px]"><SelectValue /></SelectTrigger>
              <SelectContent>
                {GATES.map((g) => <SelectItem key={g.id} value={g.id}>{g.label}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center gap-2">
            {simState === "idle" || simState === "complete" ? (
              <Button onClick={handleStart} size="sm" className="gap-2">
                <Play className="h-4 w-4" /> Simulate Boarding
              </Button>
            ) : (
              <Button onClick={handleReset} variant="outline" size="sm" className="gap-2">
                <RotateCcw className="h-4 w-4" /> Reset
              </Button>
            )}
          </div>

          <div className="flex items-center gap-1">
            <span className="text-xs font-medium text-muted-foreground uppercase mr-1">Speed:</span>
            {[1, 2, 4].map((s) => (
              <Button
                key={s}
                variant={speedMultiplier === s ? "default" : "outline"}
                size="sm"
                className="px-3 h-8"
                onClick={() => handleSpeedChange(s)}
              >
                {s}x
              </Button>
            ))}
          </div>

          <div className="ml-auto">
            <Badge variant="outline" className={`text-sm ${simState === "running" ? "bg-blue-500/15 text-blue-400 border-blue-500/30" : simState === "complete" ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30" : ""}`}>
              <Zap className="h-3 w-3 mr-1" />
              {renderState.passengersArrived} / {renderState.totalPassengers} passengers
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Main grid: Map + Status Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <div className="lg:col-span-3">
          <Card>
            <CardContent className="p-2">
              <TerminalMap
                selectedGate={selectedGate}
                particles={renderState.particles}
                heatmapGrid={renderState.heatmapGrid}
                simState={simState}
              />
            </CardContent>
          </Card>
        </div>
        <div className="lg:col-span-1">
          <StatusPanel
            selectedGate={selectedGate}
            simState={simState}
            passengersArrived={renderState.passengersArrived}
            totalPassengers={renderState.totalPassengers}
            elapsedMs={renderState.elapsedMs}
            congestionLevel={renderState.congestionLevel}
            showGates={false}
          />
        </div>
      </div>

      {/* AI Insights + All Gates */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <div className="lg:col-span-3">
          {simState !== "idle" ? (
            <Card className="border-purple-500/30 h-full">
              <CardHeader>
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-purple-400" />
                  AI Operational Insights
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {insights.map((insight, i) => (
                  <div key={i} className="flex items-start gap-3 rounded-lg bg-purple-500/5 border border-purple-500/15 p-3">
                    <Sparkles className="h-4 w-4 text-purple-400 mt-0.5 shrink-0" />
                    <p className="text-sm text-muted-foreground">{insight}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          ) : (
            <Card className="border-purple-500/30 h-full">
              <CardHeader>
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-purple-400" />
                  AI Operational Insights
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">Start a boarding simulation to generate AI-powered operational insights.</p>
              </CardContent>
            </Card>
          )}
        </div>
        <div className="lg:col-span-1">
          <GatesLegend selectedGate={selectedGate} />
        </div>
      </div>
    </div>
  );
}
