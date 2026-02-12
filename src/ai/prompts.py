"""
Predefined prompts and templates for the GenAI reasoning engine
"""

# System prompt for the AI assistant
SYSTEM_PROMPT = """You are an expert Airport Operations Analyst AI assistant for Bangalore International Airport (BIAL).

Your role is to:
1. Analyze operational data from multiple sources (passenger flows, security lanes, queue times, etc.)
2. Identify root causes of operational issues
3. Provide actionable recommendations for airport leadership
4. Explain insights in clear, executive-friendly language
5. Correlate data across different operational domains

When analyzing data:
- Focus on KPIs like queue time compliance (target: 95%), security lane performance, passenger volumes
- Look for anomalies, bottlenecks, and patterns
- Consider time-based correlations (e.g., upstream delays causing downstream issues)
- Provide specific, actionable recommendations

Format your responses with:
- Clear structure using markdown
- Bullet points for key findings
- **Bold** for important metrics and zones
- Specific numbers and time windows
- Prioritized action items

Current operational context:
- Report Date: January 24, 2026
- Terminals: T1 (Domestic), T2 (Mixed Domestic + International)
- Queue Time Targets: Entry <5min, Check-in <10min, Security <15/20min, all at 95% compliance
"""

# Demo scenario prompts
DEMO_PROMPTS = {
    "queue_compliance_analysis": {
        "prompt": "Show me where and why queue-time target compliance dropped yesterday across the departure processing path (Departure Entry → Check-in → Domestic Security). Call out the worst hour, affected terminal/zone, and top three drivers.",
        "context": "Analyzing queue time compliance across all zones"
    },

    "drill_terminal_zone": {
        "prompt": "Drill down to the specific terminal and zone with the worst performance. Compare upstream show-up profiles, check-in performance, and security lane metrics.",
        "context": "Detailed zone-level analysis"
    },

    "airline_concentration": {
        "prompt": "Split the worst hour by airline and check-in banks to identify load concentration points.",
        "context": "Airline and bank-level breakdown"
    },

    "security_lane_analysis": {
        "prompt": "Correlate with security lane performance. Identify lanes with high reject % or low cleared counts that contributed to the bottleneck.",
        "context": "Security lane performance analysis"
    },

    "boarding_mode_correlation": {
        "prompt": "Check if boarding mode mix (Aerobridge vs Bus) or baggage reclaim congestion played a role in schedule shifts feeding into this hour.",
        "context": "Upstream/downstream correlation analysis"
    },

    "customer_experience": {
        "prompt": "Did passenger complaints vs compliments shift during the same period? Which channels showed increased negative feedback?",
        "context": "Voice of Customer analysis"
    },

    "recommendations": {
        "prompt": "Based on all the analysis, provide specific, actionable recommendations we can deploy today to prevent this issue.",
        "context": "Generate actionable recommendations"
    }
}

# Templates for insights generation
INSIGHT_TEMPLATES = {
    "compliance_alert": """
🚨 **Compliance Alert - {zone}**

**Time Window:** {time_window}
**Actual Compliance:** {actual}% (Target: {target}%)
**Variance:** {variance}%
**Passengers Affected:** {pax_count:,}

**Status:** {status}
""",

    "lane_performance": """
📊 **Security Lane Performance**

**Lane:** {lane}
**Cleared Volume:** {cleared:,} passengers
**Reject Rate:** {reject_pct}% ({reject_count} rejections)
**Throughput:** {throughput} pax/hour

**Ranking:** #{rank} by cleared volume
""",

    "peak_hour_analysis": """
⏰ **Peak Hour Analysis**

**Peak Period:** {peak_hours}
**Peak Volume:** {peak_volume:,} passengers
**Compliance During Peak:** {compliance}%

**Contributing Factors:**
{factors}
""",

    "root_cause": """
🔍 **Root Cause Analysis**

**Primary Issue:** {issue}

**Contributing Factors:**
{factors}

**Impact:**
{impact}

**Recommended Actions:**
{actions}
""",

    "executive_summary": """
## Executive Summary - {date}

### Key Findings:
{findings}

### Priority Actions:
{actions}

### Overall Status:
{status}
"""
}

# Quick query suggestions for the chatbot
QUICK_QUERIES = [
    "What were our worst performing zones yesterday?",
    "Show me security lane reject rates for the past week",
    "Analyze peak hour patterns for T2 departures",
    "Compare compliance across all checkpoints today",
    "What's driving complaints in T2?",
    "Show me biometric adoption trends",
    "Which airlines had the most passengers yesterday?",
    "Identify operational bottlenecks in the afternoon peak"
]

# Contextual data descriptions for the AI
DATA_CONTEXT = """
Available data sources:

1. **Passenger Volumes (PAX)**
   - Daily volumes by terminal, flow (Arrival/Departure), and type (Domestic/International)
   - Hourly show-up profiles at departure entry and PESC checkpoints
   - Distribution by airline

2. **Queue Time Compliance**
   - Zone-level compliance (Departure Entry, Check-in, Security)
   - Time-windowed and hourly granularity
   - Actual vs. target compliance percentages
   - Wait times and passenger counts

3. **Security Lanes**
   - Cleared volumes by lane
   - Reject rates and counts
   - Hourly throughput
   - Lane rankings

4. **Aircraft Movements (ATM)**
   - Daily movements by terminal and type
   - 7-day averages and trends

5. **Baggage & Gates**
   - Belt utilization (flights, PAX, airlines)
   - Gate/stand utilization
   - Boarding mode mix (Aerobridge vs. Bus)

6. **Biometric Adoption**
   - Adoption rates by terminal and channel
   - Successful boarding counts
   - Trend over time

7. **Voice of Customer (VOC)**
   - Complaints vs. compliments ratio
   - Distribution by media type
   - Latest customer messages
   - Department-level feedback

All data includes anomalies intentionally injected on the report date (Jan 24, 2026) for demo purposes:
- Queue compliance drop at T2 Check-in and Security (1400-1600 hrs)
- High reject rates at specific security lanes (L6, L3)
- Increased bus boarding at T2
- Spike in T2 complaints
"""
