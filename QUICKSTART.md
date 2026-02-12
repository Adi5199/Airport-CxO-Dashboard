# Quick Start Guide

Get the BIAL Airport Operations Dashboard running in 3 simple steps.

## Architecture

```
Frontend:  Next.js + shadcn/ui + Tailwind + Recharts   (port 3000)
Backend:   FastAPI + Python (data layer + AI chat)      (port 8000)
AI Chat:   Google Gemini 2.5 Flash (free tier)
```

---

## Fast Setup (3 Steps)

### Step 1: Install Dependencies

**Backend:**
```bash
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
cd ../..
```

### Step 3: Run Dashboard
```bash
./run.sh
```

The dashboard will open at **http://localhost:3000**

To stop: press `Ctrl+C` or run `lsof -ti:8000 -ti:3000 | xargs kill`

---

## Enable AI Chat (Free)

The dashboard works without an API key using rule-based analysis. To enable full GenAI chat:

1. Go to **https://aistudio.google.com/apikey**
2. Sign in with Google and click "Create API Key"
3. Add your key to `backend/.env`:
   ```
   GEMINI_API_KEY=AIzaSy...your-key-here
   ```
4. Restart the dashboard

Uses **Gemini 2.5 Flash** (free tier: ~1,500 requests/day). No credit card needed.

### Alternative: OpenAI

To use OpenAI instead, edit `config.yaml`:
```yaml
ai:
  default_provider: "openai"
```
And set `OPENAI_API_KEY` in `backend/.env`. Requires an OpenAI account with billing.

---

## Quick Demo (5 Minutes)

### 1. Executive Overview (1 min)
- View AI-generated executive summary
- Check key KPIs: PAX volume, queue compliance, reject rates, VOC ratio

### 2. Queue Compliance Analysis (2 min) - KEY DEMO
- Navigate to **Queue Compliance** in the sidebar
- Click **"Analyze Root Cause"** on any zone
- Review AI-generated severity, contributing factors, and recommendations

### 3. AI Chat (2 min)
- Navigate to **AI Insights Chat**
- Click any **Demo Scenario** button in the sidebar
- Ask follow-up questions in natural language

---

## Demo Scenario Focus

**Date:** January 24, 2026
**Issue:** Queue compliance concerns at T2, security lane reject rates

**What to Look For:**
- Check-in 34-86 compliance at ~94% (Target: 95%)
- T1-Left-L3: 13.7% reject rate (295 rejections)
- T2-Left-L6: 12.8% reject rate (198 rejections)
- AI identifies actionable recommendations per zone

---

## Pages

| Page | URL | Description |
|------|-----|-------------|
| Executive Overview | `/overview` | KPIs, AI summary, trends, alerts |
| Queue Compliance | `/queue` | Zone status, root cause, heatmap, drill-down |
| Security Operations | `/security` | Lane performance, baggage, gates |
| Trends & Analytics | `/trends` | 30-day PAX, biometric, VOC trends |
| AI Insights Chat | `/chat` | Streaming chat with demo scenarios |

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

## Project Structure

```
Airport CxO Dash/
  config.yaml              # Shared configuration
  run.sh                   # Single launcher (both services)
  data/generated/          # 13 Parquet data files
  backend/
    main.py                # FastAPI app
    .env                   # API keys (GEMINI_API_KEY)
    core/                  # Data loader, calculations
    ai/                    # Chatbot, reasoning engine, prompts
    routers/               # API endpoints (overview, queue, security, trends, chat)
  frontend/
    app/                   # Next.js pages (overview, queue, security, trends, chat)
    components/            # shadcn/ui + chart components
    hooks/                 # useApi (SWR), useStreaming (SSE)
    lib/                   # Types, constants, API helpers
```
