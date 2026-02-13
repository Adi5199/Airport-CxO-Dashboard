import type { TrafficParticle, TrafficSimState } from "@/lib/types";
import { GATES, LOUNGES, HEATMAP_GRID, TERMINAL, type GateConfig } from "./terminal-map-data";

interface InternalParticle {
  id: number;
  startX: number;
  startY: number;
  targetX: number;
  targetY: number;
  controlX: number;
  controlY: number;
  progress: number;
  speed: number;
  spawnTime: number;
  size: number;
  arrived: boolean;
}

export class ParticleEngine {
  private particles: InternalParticle[] = [];
  private nextId = 0;
  private startTime = 0;
  private lastFrameTime = 0;
  private totalPassengers: number;
  private simulationDurationMs: number;
  private speedMultiplier: number;
  private targetGate: GateConfig;
  private running = false;
  private complete = false;
  private passengersArrived = 0;

  constructor(config: {
    gateId: string;
    totalPassengers?: number;
    simulationDurationMs?: number;
    speedMultiplier?: number;
  }) {
    this.totalPassengers = config.totalPassengers ?? 140;
    this.simulationDurationMs = config.simulationDurationMs ?? 18000;
    this.speedMultiplier = config.speedMultiplier ?? 1;
    this.targetGate = GATES.find((g) => g.id === config.gateId) ?? GATES[0];
  }

  start(timestamp: number) {
    this.startTime = timestamp;
    this.lastFrameTime = timestamp;
    this.running = true;
    this.complete = false;
    this.passengersArrived = 0;
    this.particles = [];
    this.nextId = 0;
    this.precomputeParticles();
  }

  private precomputeParticles() {
    const spawnWindowMs = this.simulationDurationMs * 0.55;

    for (let i = 0; i < this.totalPassengers; i++) {
      const lounge = LOUNGES[Math.floor(Math.random() * LOUNGES.length)];
      const startX = lounge.x + Math.random() * lounge.width;
      const startY = lounge.y + Math.random() * lounge.height;

      const targetX = this.targetGate.centerX + (Math.random() - 0.5) * 30;
      const targetY = this.targetGate.centerY + (Math.random() - 0.5) * 20;

      // Control point for bezier curve — offset laterally for organic paths
      const midX = (startX + targetX) / 2;
      const midY = (startY + targetY) / 2;
      const offset = (Math.random() - 0.5) * 160;
      const controlX = midX + offset;
      const controlY = midY + (Math.random() - 0.5) * 80;

      this.particles.push({
        id: this.nextId++,
        startX,
        startY,
        targetX,
        targetY,
        controlX,
        controlY,
        progress: 0,
        speed: 0.6 + Math.random() * 0.8, // varied speed per particle
        spawnTime: Math.random() * spawnWindowMs,
        size: 2 + Math.random() * 2.5,
        arrived: false,
      });
    }

    // Sort by spawn time for efficient processing
    this.particles.sort((a, b) => a.spawnTime - b.spawnTime);
  }

  setSpeedMultiplier(multiplier: number) {
    this.speedMultiplier = multiplier;
  }

  update(timestamp: number): TrafficSimState {
    if (!this.running) return this.getIdleState();

    const elapsedMs = (timestamp - this.startTime) * this.speedMultiplier;
    const deltaMs = (timestamp - this.lastFrameTime) * this.speedMultiplier;
    this.lastFrameTime = timestamp;

    const visibleParticles: TrafficParticle[] = [];
    let arrivedCount = 0;
    let allDone = true;

    for (const p of this.particles) {
      if (elapsedMs < p.spawnTime) {
        allDone = false;
        continue;
      }

      if (p.arrived) {
        arrivedCount++;
        continue;
      }

      allDone = false;

      // Advance progress based on speed and deltaTime
      const progressIncrement = (deltaMs * p.speed) / (this.simulationDurationMs * 0.45);
      p.progress = Math.min(1, p.progress + progressIncrement);

      if (p.progress >= 1) {
        p.arrived = true;
        arrivedCount++;
        continue;
      }

      // Quadratic bezier interpolation
      const t = p.progress;
      const mt = 1 - t;
      const x = mt * mt * p.startX + 2 * mt * t * p.controlX + t * t * p.targetX;
      const y = mt * mt * p.startY + 2 * mt * t * p.controlY + t * t * p.targetY;

      // Fade in at start, fade out near end
      let opacity = 1;
      if (t < 0.08) opacity = t / 0.08;
      else if (t > 0.92) opacity = (1 - t) / 0.08;

      visibleParticles.push({
        id: p.id,
        x,
        y,
        progress: t,
        opacity,
        size: p.size,
      });
    }

    this.passengersArrived = arrivedCount;

    if (allDone && arrivedCount === this.totalPassengers) {
      this.complete = true;
      this.running = false;
    }

    // Compute heatmap grid
    const heatmapGrid = this.computeHeatmap(visibleParticles);

    // Determine congestion level
    const maxDensity = Math.max(...heatmapGrid.flat(), 0);
    let congestionLevel: "low" | "medium" | "high" = "low";
    if (maxDensity >= 6) congestionLevel = "high";
    else if (maxDensity >= 3) congestionLevel = "medium";

    return {
      particles: visibleParticles,
      heatmapGrid,
      passengersArrived: arrivedCount,
      totalPassengers: this.totalPassengers,
      elapsedMs,
      isComplete: this.complete,
      congestionLevel,
    };
  }

  private computeHeatmap(particles: TrafficParticle[]): number[][] {
    const grid: number[][] = Array.from({ length: HEATMAP_GRID.rows }, () =>
      Array(HEATMAP_GRID.cols).fill(0)
    );

    for (const p of particles) {
      const col = Math.floor((p.x - HEATMAP_GRID.startX) / HEATMAP_GRID.cellWidth);
      const row = Math.floor((p.y - HEATMAP_GRID.startY) / HEATMAP_GRID.cellHeight);

      if (col >= 0 && col < HEATMAP_GRID.cols && row >= 0 && row < HEATMAP_GRID.rows) {
        grid[row][col]++;
      }
    }

    return grid;
  }

  isRunning() {
    return this.running;
  }

  isComplete() {
    return this.complete;
  }

  reset() {
    this.particles = [];
    this.running = false;
    this.complete = false;
    this.passengersArrived = 0;
    this.startTime = 0;
    this.lastFrameTime = 0;
  }

  private getIdleState(): TrafficSimState {
    return {
      particles: [],
      heatmapGrid: Array.from({ length: HEATMAP_GRID.rows }, () =>
        Array(HEATMAP_GRID.cols).fill(0)
      ),
      passengersArrived: this.passengersArrived,
      totalPassengers: this.totalPassengers,
      elapsedMs: 0,
      isComplete: this.complete,
      congestionLevel: "low",
    };
  }
}
