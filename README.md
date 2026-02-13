# BIAL Brain & Advisor

**GenAI-Powered CxO Dashboard for Bangalore International Airport**

A comprehensive, interactive dashboard designed for BIAL top management, featuring AI-powered insights, operational monitoring across terminals, and conversational analytics. Built with Next.js 16 and FastAPI.

---

## Overview

The dashboard provides executive-level visibility into critical airport KPIs, proactively highlights anomalies, and delivers actionable insights through an embedded GenAI chatbot. It integrates data from multiple operational sources (AODB, XOVIES, E-Gate, Passenger Feedback, Daily E-logs) to present a unified view of:

- **Passenger Volumes** (PAX) - Domestic/International, bifurcated trends
- **Air Traffic Movements** (ATM) - Domestic/International breakdown
- **Queue Performance** - Departure Entry, Check-in, Security zones
- **On-Time Performance** (OTP) - Flight departure & arrival punctuality
- **Baggage Delivery** - First bag/last bag delivery times
- **Safety Issues** - Incident tracking by terminal
- **Slot Adherence** - Schedule compliance
- **Voice of Customer** (VOC) - Sentiment analysis & feedback
- **Security Lane Performance** - Throughput and reject rates

### Key Features

- **AI-Powered Reasoning Engine** - Automated root cause analysis and insights generation
- **Conversational Chatbot** - Natural language queries with streaming responses (Gemini 2.5 Flash)
- **Terminal Filtering** - Dynamic data for Overall / Terminal 1 / Terminal 2 across all pages
- **Traffic Monitoring** - Interactive SVG map of Terminal 2 with boarding call simulation and AI insights
- **Compliance Advisor** - Regulatory, operational, and legal compliance tracking
- **Anomaly Detection** - Proactive alerts for issues requiring leadership attention
- **Share Functionality** - Copy or email AI responses and dashboard cards
- **Dynamic Data Sources** - Sidebar shows relevant data sources per active tab
- **Dark Theme** - oklch-based dark UI with Tailwind CSS 4

---

## Architecture

```
Frontend:  Next.js 16 + shadcn/ui + Tailwind CSS 4 + Recharts   (port 3000)
Backend:   FastAPI + Python (data layer + AI chat)                (port 8000)
AI Chat:   Google Gemini 2.5 Flash (free tier)
Data:      Parquet files (Pandas + PyArrow)
```

---

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm

### Step 1: Install Dependencies

**Backend:**
```bash
cd "Airport CxO Dash"
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
cd ..
```

### Step 2: Generate Mock Data (if not already present)

```bash
cd data/generators
python3 generate_all_data.py
python3 operational_kpi_data.py
cd ../..
```

This generates 17 parquet files with realistic airport operations data for January-March 2026.

### Step 3: Configure AI Chat (Optional)

For full GenAI chatbot functionality:

1. Go to **https://aistudio.google.com/apikey**
2. Create an API key (free, no credit card needed)
3. Add to `backend/.env`:
   ```
   GEMINI_API_KEY=AIzaSy...your-key-here
   ```

The dashboard works without API keys using rule-based fallback analysis.

### Step 4: Run the Dashboard

```bash
./run.sh
```

Opens at **http://localhost:3000**. To stop: `Ctrl+C` or `lsof -ti:8000 -ti:3000 | xargs kill`

---

## Dashboard Pages

### 1. Operations Overview (`/overview`)
- AI-generated executive summary with status indicator (On Track / Attention / Critical)
- Terminal filter: Overall / Terminal 1 / Terminal 2
- Key KPIs: Total PAX, ATM, On-Time Performance, Baggage Delivery, Safety Issues, Queue Performance, Slot Adherence, VOC Ratio, First Bag Delivery
- Priority actions dynamically filtered by terminal
- 15-day bifurcated trend lines (Total / Domestic / International) for PAX and ATM
- Queue performance by zone (bar chart)
- Collapsible Alerts & Anomalies section

### 2. Queue Performance (`/queue`)
- Terminal filter: Overall / Terminal 1 / Terminal 2
- Sub-tabs: Departure Entry, Check-in, Security
- Queue KPIs: Overall Performance, Zones Below Target, PAX Affected, Target Achievement
- Security KPIs: Total Cleared, Avg Reject Rate, High Reject Lanes
- **AI-Powered Root Cause Analysis** - analyzes contributing factors, severity, and recommendations for the selected zone and terminal
- Zone detail with performance gauge, time-series chart, and zone selector
- Security lane charts (cleared volume, reject rate by lane) on Security sub-tab
- Performance heatmap (all zones x time windows)
- Detailed performance data table

### 3. Traffic Monitor (`/traffic`)
- Interactive SVG map of BIAL Terminal 2
- Boarding call simulation with particle animation (passengers flowing from lounge to gate)
- Gate selector, speed control (1x/2x/4x), simulate/reset controls
- Real-time status panel: gate status, passenger progress, congestion level, time elapsed
- **AI Operational Insights** panel below the map with context-aware recommendations
- All Gates legend
- Data source: XOVIES

### 4. Compliance Advisor (`/compliance`)
- 4 compliance categories: Operational, Regulatory, Legal, Internal SOPs
- Issue counts with severity indicators (Critical, High, Medium, Low)
- Upcoming compliance tasks & deadlines with priority badges and countdown
- Status tracking (Pending, In Progress, Under Review)

### 5. AI Insights Chat (`/chat`)
- Streaming chat interface powered by Gemini 2.5 Flash
- Demo scenario prompts and quick queries in sidebar
- Share individual AI responses (Copy / Email)
- Conversation history with clear option
- Contextual responses grounded in airport operational data

### 6. Trends & Analytics (`/trends`)
- 30-day passenger volume trends
- Voice of Customer sentiment analysis
- Feedback by terminal, channel, and department

---

## Data Sources by Tab

| Tab | Sources |
|-----|---------|
| Operations Overview | AODB, XOVIES, 3.1 E-Gate, Passenger Feedback, Daily E-logs & Comments |
| Queue Performance | XOVIES, E-Gates, Compliance Advisor, Compliance Management System, Daily E-logs & Comments |
| Traffic Monitor | XOVIES |
| Compliance Advisor | Compliance Management System, AODB, XOVIES, Daily E-logs & Comments |
| AI Insights Chat | AODB, XOVIES, Passenger Feedback |
| Trends & Analytics | AODB, XOVIES, Passenger Feedback |

---

## Project Structure

```
Airport CxO Dash/
  config.yaml                    # Shared configuration (targets, thresholds)
  run.sh                         # Single launcher (both services)

  data/
    generators/                  # Mock data generation scripts
      generate_all_data.py       # Master data generator (13 files)
      operational_kpi_data.py    # OTP, baggage delivery, slot adherence, safety (4 files)
    generated/                   # 17 Parquet data files

  backend/
    main.py                      # FastAPI app entry point
    .env                         # API keys (GEMINI_API_KEY)
    core/
      config.py                  # Configuration loader
      data_loader.py             # Data loading with caching
      calculations.py            # Metrics & anomaly detection
    ai/
      reasoning_engine.py        # AI-powered analysis (terminal-aware)
      chatbot.py                 # Gemini streaming chatbot
      prompts.py                 # System prompts & templates
    routers/
      overview.py                # /api/overview/* (KPIs, exec summary, trends, alerts)
      queue.py                   # /api/queue/* (status, zones, root-cause, heatmap)
      security.py                # /api/security/* (lanes, reject rates, baggage, gates)
      compliance.py              # /api/compliance/* (summary, upcoming tasks)
      trends.py                  # /api/trends/*
      chat.py                    # /api/chat/* (streaming, demo prompts)

  frontend/
    app/
      overview/page.tsx          # Operations Overview
      queue/page.tsx             # Queue Performance
      traffic/page.tsx           # Traffic Monitor (simulation)
      compliance/page.tsx        # Compliance Advisor
      chat/page.tsx              # AI Insights Chat
      trends/page.tsx            # Trends & Analytics
    components/
      layout/
        sidebar.tsx              # Navigation + dynamic data sources
        header.tsx               # App header
      dashboard/
        kpi-card.tsx             # KPI card component
        alert-card.tsx           # Alert card (warning/error/success/info)
        compliance-gauge.tsx     # Circular gauge
        share-button.tsx         # Share via clipboard/email
      charts/
        line-chart.tsx           # Multi-line chart (bifurcated support)
        bar-chart.tsx            # Horizontal/vertical bar chart
        heatmap-chart.tsx        # Zone x time window heatmap
      traffic/
        terminal-map.tsx         # SVG terminal map with particles & heatmap overlay
        terminal-map-data.ts     # Gate coordinates, lounges, map constants
        particle-engine.ts       # Bezier-path particle animation engine
        status-panel.tsx         # Simulation status cards + gates legend
    hooks/
      use-api.ts                 # SWR data fetching hook
      use-streaming.ts           # SSE streaming hook for chat
    lib/
      types.ts                   # TypeScript interfaces
      constants.ts               # Navigation items, report date
      api.ts                     # API helper (fetchApi)
```

---

## Data Model

### Generated Datasets (17 files)

| File | Description |
|------|-------------|
| `pax_daily_volumes.parquet` | Daily passenger counts by terminal & type |
| `pax_hourly_showup.parquet` | Hourly show-up profiles |
| `pax_by_airline.parquet` | Airline distribution |
| `queue_zone_compliance.parquet` | Queue performance by zone & time window |
| `queue_hourly_compliance.parquet` | Hourly queue performance detail |
| `security_lanes_daily.parquet` | Daily security lane performance |
| `security_lanes_hourly.parquet` | Hourly security lane metrics |
| `atm_daily.parquet` | Air traffic movements |
| `baggage_utilization.parquet` | Baggage belt metrics |
| `gate_utilization.parquet` | Gate/stand usage & boarding modes |
| `biometric_adoption.parquet` | Biometric registration data |
| `voc_feedback.parquet` | Complaints/compliments aggregated |
| `voc_messages.parquet` | Individual customer messages |
| `otp_daily.parquet` | On-time performance by terminal |
| `baggage_delivery.parquet` | First/last bag delivery times |
| `slot_adherence.parquet` | Schedule slot adherence rates |
| `safety_issues.parquet` | Safety incidents by terminal & category |

### Demo Date: January 24, 2026

Intentionally injected anomalies:
- Queue performance drop at T2 Check-in 34-86 (14:00-16:00)
- High reject rates at security lanes L6, L3 (12-14%)
- Passenger volume spike +45% during afternoon
- VOC sentiment deterioration (complaints +60%)

---

## Configuration

### Targets & Thresholds (`config.yaml`)

```yaml
targets:
  queue_time:
    departure_entry:
      threshold_minutes: 5
      target_compliance_pct: 95
    checkin:
      threshold_minutes: 10
      target_compliance_pct: 95
    security:
      threshold_minutes_tier1: 15
      threshold_minutes_tier2: 20
      target_compliance_pct: 95
```

### AI Provider

Default: **Gemini 2.5 Flash** (free tier, ~1,500 requests/day)

Alternative: OpenAI GPT-4 - edit `config.yaml`:
```yaml
ai:
  default_provider: "openai"
```
And set `OPENAI_API_KEY` in `backend/.env`.

---

## Technical Stack

- **Frontend:** Next.js 16 (App Router), React 19, TypeScript
- **UI:** shadcn/ui, Tailwind CSS 4 (oklch dark theme)
- **Charts:** Recharts 3.7
- **Data Fetching:** SWR (REST), Server-Sent Events (chat streaming)
- **Backend:** FastAPI, Uvicorn
- **Data Processing:** Pandas 2.2, NumPy 1.26, PyArrow
- **AI:** Google Gemini 2.5 Flash (default), OpenAI GPT-4 (optional)
- **Data Storage:** Parquet files

---

## Troubleshooting

**Port already in use?**
```bash
lsof -ti:8000 | xargs kill
lsof -ti:3000 | xargs kill
./run.sh
```

**Backend won't start?**
```bash
source .venv/bin/activate
pip install -r backend/requirements.txt
```

**Frontend build errors?**
```bash
cd frontend && npm install && cd ..
```

**Chat not responding with AI?**
- Check that `GEMINI_API_KEY` is set in `backend/.env`
- Verify the key at https://aistudio.google.com/apikey
- The dashboard still works with rule-based fallback responses

---

Built for Bangalore International Airport Limited (BIAL) - Airport Operations Excellence