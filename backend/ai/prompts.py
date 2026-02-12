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

DEMO_PROMPTS = {
    "queue_compliance_analysis": {
        "label": "Queue Compliance Drop",
        "prompt": "Show me where and why queue-time target compliance dropped yesterday across the departure processing path (Departure Entry -> Check-in -> Domestic Security). Call out the worst hour, affected terminal/zone, and top three drivers.",
    },
    "drill_terminal_zone": {
        "label": "Drill to Terminal/Zone",
        "prompt": "Drill down to the specific terminal and zone with the worst performance. Compare upstream show-up profiles, check-in performance, and security lane metrics.",
    },
    "airline_concentration": {
        "label": "Airline Concentration",
        "prompt": "Split the worst hour by airline and check-in banks to identify load concentration points.",
    },
    "security_lane_analysis": {
        "label": "Security Lane Issues",
        "prompt": "Correlate with security lane performance. Identify lanes with high reject % or low cleared counts that contributed to the bottleneck.",
    },
    "boarding_mode_correlation": {
        "label": "Boarding Mode Impact",
        "prompt": "Check if boarding mode mix (Aerobridge vs Bus) or baggage reclaim congestion played a role in schedule shifts feeding into this hour.",
    },
    "customer_experience": {
        "label": "Customer Sentiment",
        "prompt": "Did passenger complaints vs compliments shift during the same period? Which channels showed increased negative feedback?",
    },
    "recommendations": {
        "label": "Get Recommendations",
        "prompt": "Based on all the analysis, provide specific, actionable recommendations we can deploy today to prevent this issue.",
    },
}

INSIGHT_TEMPLATES = {
    "executive_summary": """## Executive Summary - {date}

### Key Findings:
{findings}

### Priority Actions:
{actions}

### Overall Status:
{status}
""",
}

DATA_CONTEXT = """
Available data sources:

1. **Passenger Volumes (PAX)** - Daily volumes by terminal, flow, type; hourly show-up profiles; airline distribution
2. **Queue Time Compliance** - Zone-level compliance across Departure Entry, Check-in, Security; time-windowed and hourly granularity
3. **Security Lanes** - Cleared volumes, reject rates, hourly throughput, lane rankings
4. **Aircraft Movements (ATM)** - Daily movements by terminal and type
5. **Baggage & Gates** - Belt utilization, gate/stand utilization, boarding mode mix
6. **Biometric Adoption** - Adoption rates by terminal and channel
7. **Voice of Customer (VOC)** - Complaints vs compliments ratio, feedback by department

All data includes anomalies on the report date (Jan 24, 2026):
- Queue compliance drop at T2 Check-in and Security (1400-1600 hrs)
- High reject rates at specific security lanes (L6, L3)
- Increased bus boarding at T2
- Spike in T2 complaints
"""

QUICK_QUERIES = [
    "What were our worst performing zones yesterday?",
    "Show me security lane reject rates for the past week",
    "Analyze peak hour patterns for T2 departures",
    "Compare compliance across all checkpoints today",
    "What's driving complaints in T2?",
    "Show me biometric adoption trends",
    "Which airlines had the most passengers yesterday?",
    "Identify operational bottlenecks in the afternoon peak",
]
