# ✈️ BIAL Airport Operations Dashboard

**GenAI-Powered Executive Dashboard for Airport Top Management**

A comprehensive, interactive dashboard designed for Bangalore International Airport (BIAL) top management, featuring AI-powered insights, real-time operational monitoring, and conversational analytics.

---

## 🎯 Overview

This dashboard provides executive-level visibility into critical airport KPIs, proactively highlights anomalies, and delivers actionable insights through an embedded GenAI chatbot. It integrates data from multiple operational sources to present a clear view of:

- **Passenger Volumes** (PAX) - Domestic/International, Arrivals/Departures
- **Queue Time Compliance** - Entry, Check-in, Security zones
- **Security Lane Performance** - Throughput and reject rates
- **Aircraft Movements** (ATM)
- **Baggage & Gate Utilization**
- **Biometric Adoption**
- **Voice of Customer** (VOC) sentiment analysis

### Key Features

✅ **AI-Powered Reasoning Engine** - Automated root cause analysis and insights generation
✅ **Conversational Chatbot** - Natural language queries with contextual responses
✅ **Interactive Dashboards** - Power BI-like cross-filtering and drill-down capabilities
✅ **Anomaly Detection** - Proactive alerts for issues requiring leadership attention
✅ **Demo Scenario** - Pre-configured use case demonstrating queue compliance analysis
✅ **Mock Data** - Realistic airport operations data with injected anomalies

---

## 🏗️ Architecture

```
Airport-CxO-Dashboard/
├── app.py                      # Main Streamlit application
├── config.yaml                 # Configuration (targets, thresholds, AI settings)
├── requirements.txt            # Python dependencies
│
├── data/
│   ├── generators/             # Mock data generation scripts
│   │   ├── generate_all_data.py     # Master data generation script
│   │   ├── passenger_data.py        # PAX volumes & show-up profiles
│   │   ├── queue_time_data.py       # Queue compliance metrics
│   │   ├── security_data.py         # Security lane performance
│   │   ├── atm_data.py              # Aircraft movements
│   │   ├── baggage_gate_data.py     # Baggage & gate utilization
│   │   └── biometric_voc_data.py    # Biometric & VOC data
│   │
│   └── generated/              # Generated parquet files (created after data gen)
│
├── src/
│   ├── dashboard/
│   │   ├── components/
│   │   │   ├── kpi_cards.py         # Reusable KPI components
│   │   │   ├── charts.py            # Chart components
│   │   │   └── filters.py           # Global filter components
│   │   │
│   │   └── pages/
│   │       ├── executive_overview.py    # Executive summary page
│   │       ├── queue_compliance.py      # Queue compliance (demo focus)
│   │       ├── security_operations.py   # Security & operations
│   │       ├── ai_chat.py               # AI chatbot interface
│   │       └── trends_analytics.py      # Trends & VOC analysis
│   │
│   ├── ai/
│   │   ├── reasoning_engine.py      # AI-powered analysis engine
│   │   ├── chatbot.py               # Conversational AI interface
│   │   └── prompts.py               # System prompts & templates
│   │
│   └── utils/
│       ├── data_loader.py           # Data loading with caching
│       └── calculations.py          # Metrics & anomaly detection
│
└── .env.template                # Template for API keys
```

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Step 1: Install Dependencies

```bash
cd "Airport CxO Dash"
pip3 install -r requirements.txt
```

### Step 2: Generate Mock Data

```bash
cd data/generators
python3 generate_all_data.py
```

This will generate ~14 parquet files with realistic airport operations data for January 2026.

### Step 3: Configure API Keys (Optional)

For full GenAI chatbot functionality, configure your OpenAI API key:

```bash
cp .env.template .env
# Edit .env and add your OPENAI_API_KEY
```

**Note:** The dashboard works without API keys using rule-based fallback analysis.

### Step 4: Run the Dashboard

```bash
cd ../..  # Return to project root
python3 -m streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

---

## 📊 Dashboard Pages

### 1. 🏠 Executive Overview
- AI-generated executive summary
- Key KPIs: Total PAX, Domestic/International split, Queue Compliance, VOC Ratio
- 15-day trend lines for passengers and ATMs
- Today's performance breakdown by terminal and zone
- Proactive alerts for anomalies

### 2. ⏱️ Queue Compliance (Demo)
**⭐ Main Demo Page**
- Overall compliance status across all zones
- **AI-Powered Root Cause Analysis** button (key demo feature)
- Zone-by-zone detailed performance
- Time-windowed compliance heatmap
- Interactive drill-down capabilities
- Export to CSV

### 3. 🔒 Security & Operations
- Security lane performance (cleared volumes, reject rates)
- Lane-by-lane comparisons with alerting
- Baggage belt utilization
- Gate utilization & boarding mode mix (Aerobridge vs. Bus)

### 4. 💬 AI Insights Chat
**⭐ Conversational Interface**
- Natural language query interface
- Demo scenario prompts (sidebar)
- Contextual responses with data analysis
- Conversation history & export
- Quick query suggestions

### 5. 📈 Trends & Analytics
- 30-day passenger volume trends
- Biometric adoption progression
- Voice of Customer sentiment analysis
- Feedback by terminal, channel, and department
- Recent customer messages

---

## 🎬 Demo Scenario Guide

### Use Case: Queue Compliance Root Cause Analysis

**Scenario:** On January 24, 2026, queue compliance dropped below target during the afternoon. Leadership needs to understand why and get actionable recommendations.

### Step-by-Step Demo Flow

#### Step 1: Executive Overview
1. Navigate to **🏠 Executive Overview**
2. Note the overall metrics and AI-generated summary
3. Observe the alert about zones below target

#### Step 2: Queue Compliance Deep Dive
1. Navigate to **⏱️ Queue Compliance (Demo)**
2. Observe:
   - Overall compliance ~89% (below 95% target)
   - 3+ zones below target
   - Thousands of passengers affected

3. **Click "🔍 Analyze Root Cause"** ⭐ **KEY DEMO MOMENT**

The AI will:
- Identify worst zones: "Check-in 34-86", "T2 Security Left/Right"
- Pinpoint time window: 14:00-16:00
- Analyze contributing factors:
  - Passenger volume spike
  - High reject rates at security lanes (L6, L3)
  - Check-in processing delays
- Generate **4 actionable recommendations**

#### Step 3: Security Lane Correlation
1. Navigate to **🔒 Security & Operations**
2. Verify security lane issues:
   - Lane L6 and L3 show reject rates >12% (target: <8%)
   - Lower cleared volumes during peak hours
3. Note the boarding mode anomaly (increased bus boarding at T2)

#### Step 4: AI Chatbot Interaction
1. Navigate to **💬 AI Insights Chat**
2. Use the **Demo Scenario Prompts** in the sidebar:

   **Prompt 1:** "Show me where and why queue-time target compliance dropped yesterday..."
   - AI provides comprehensive analysis with specific numbers

   **Prompt 2:** "Split the worst hour by airline and check-in banks..."
   - AI identifies airline concentration patterns

   **Prompt 3:** "Did passenger complaints vs compliments shift during the same period?"
   - AI correlates with VOC data, showing increased negative feedback at T2

3. Ask custom follow-up questions:
   - "What specific actions should we take today?"
   - "Show me historical patterns for T2 security"

#### Step 5: Trends Validation
1. Navigate to **📈 Trends & Analytics**
2. Verify VOC sentiment drop on Jan 24
3. Check biometric adoption trends
4. Review recent negative feedback messages mentioning queues

### Expected Insights from Demo

The AI reasoning engine will identify:

**Primary Issue:**
- Queue compliance at Check-in 34-86 dropped to ~80% during 14:00-16:00 (Target: 95%)

**Root Causes:**
1. 45% spike in passenger volumes during afternoon peak
2. Security lanes L6 & L3 with 12-14% reject rates (causing re-scans and delays)
3. Check-in bank processing slower than normal
4. 40%+ bus boarding at T2 causing irregular passenger arrival patterns

**Recommendations:**
1. ✅ Open 2 additional security lanes during 14:00-18:00 window
2. ✅ Assign senior screeners to high-reject lanes (L6, L3)
3. ✅ Implement queue marshaling at T2 check-in banks during peaks
4. ✅ Promote biometric fast-track via digital signage

**Impact:**
- ~4,500 passengers experienced extended wait times
- Customer complaints spiked 60% at T2
- Compliments:Complaints ratio dropped from 2.5:1 to 1.4:1

---

## ⚙️ Configuration

### Targets & Thresholds (config.yaml)

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

### AI Provider Configuration

Support for multiple AI providers:
- **OpenAI GPT-4** (default, requires API key)
- **Anthropic Claude** (requires API key)
- **Rule-based fallback** (no API key needed)

Set in `config.yaml`:
```yaml
ai:
  default_provider: "openai"  # or "anthropic"
  temperature: 0.3
  max_tokens: 2000
```

---

## 📈 Data Model

### Generated Datasets

1. **pax_daily_volumes.parquet** - Daily passenger counts
2. **pax_hourly_showup.parquet** - Hourly show-up profiles
3. **pax_by_airline.parquet** - Airline distribution
4. **queue_zone_compliance.parquet** - Compliance by zone & time window
5. **queue_hourly_compliance.parquet** - Hourly compliance detail
6. **security_lanes_daily.parquet** - Daily lane performance
7. **security_lanes_hourly.parquet** - Hourly lane metrics
8. **atm_daily.parquet** - Aircraft movements
9. **baggage_utilization.parquet** - Baggage belt metrics
10. **gate_utilization.parquet** - Gate/stand usage & boarding modes
11. **biometric_adoption.parquet** - Biometric registration & adoption
12. **voc_feedback.parquet** - Complaints/compliments aggregated
13. **voc_messages.parquet** - Individual customer messages

### Anomalies (Demo Date: Jan 24, 2026)

Intentionally injected for demo:
- Queue compliance drop at T2 Check-in 34-86 (14:00-16:00)
- High reject rates at security lanes L6, L3 (12-14%)
- Passenger volume spike +45% during afternoon
- Increased bus boarding at T2 (40%+)
- VOC sentiment deterioration (complaints +60%)

---

## 🔧 Customization

### Adding New KPIs

1. Create data generator in `data/generators/`
2. Add data loader method in `src/utils/data_loader.py`
3. Create calculation logic in `src/utils/calculations.py`
4. Add visualization in dashboard pages

### Modifying AI Prompts

Edit `src/ai/prompts.py`:
- `SYSTEM_PROMPT` - AI assistant personality and context
- `DEMO_PROMPTS` - Pre-defined scenario prompts
- `INSIGHT_TEMPLATES` - Output formatting templates

### Custom Filters

Modify `src/dashboard/components/filters.py` to add:
- New filter dimensions
- Custom date ranges
- Additional drill-down options

---

## 🐛 Troubleshooting

### Data Generation Issues

**Error:** `ModuleNotFoundError: No module named 'yaml'`
**Fix:** `pip3 install pyyaml pandas numpy pyarrow`

**Error:** `FileNotFoundError: config.yaml`
**Fix:** Ensure you're running from project root directory

### Dashboard Issues

**Issue:** Streamlit won't start
**Fix:** Check that port 8501 is available, or specify alternative:
```bash
streamlit run app.py --server.port 8502
```

**Issue:** Charts not rendering
**Fix:** Clear Streamlit cache: `streamlit cache clear`

### AI Chatbot Issues

**Issue:** "API key not configured" warnings
**Solution:** This is expected if you haven't set up OpenAI API key. The dashboard will use rule-based fallback analysis which still provides valuable insights.

**To enable full AI:** Get OpenAI API key from https://platform.openai.com/ and add to `.env` file

---

## 📝 Technical Stack

- **Frontend:** Streamlit 1.32
- **Visualization:** Plotly 5.18
- **Data Processing:** Pandas 2.2, NumPy 1.26
- **AI/ML:** OpenAI GPT-4, Anthropic Claude, LangChain
- **Data Storage:** Parquet (via PyArrow)
- **Configuration:** YAML

---

## 🎓 Key Learnings & Best Practices

1. **Mock Data Realism:** Data generators include:
   - Realistic daily/hourly patterns
   - Weekend effects
   - Intentional anomalies for demo
   - 7-day rolling averages

2. **AI Integration:**
   - Context-aware prompts with operational data
   - Fallback to rule-based when API unavailable
   - Structured output templates

3. **Interactive Design:**
   - Cross-filtering ready (Streamlit session state)
   - Drill-down capabilities
   - Export functionality

4. **Executive Focus:**
   - KPI-first design
   - Anomaly highlighting
   - Actionable recommendations

---

## 🚀 Future Enhancements

- [ ] Real-time data integration
- [ ] Predictive analytics (forecasting)
- [ ] Mobile-responsive design
- [ ] Role-based access control
- [ ] Email/SMS alerting
- [ ] Integration with airport operational systems
- [ ] Multi-airport support
- [ ] Advanced ML models for anomaly detection

---

## 📧 Support & Feedback

For questions, issues, or suggestions, please open an issue in the repository or contact the development team.

---

## 📄 License

© 2026 Bangalore International Airport Limited (BIAL)
All rights reserved.

---

**Built with ❤️ for Airport Operations Excellence**
