import pandas as pd
import numpy as np
from typing import Dict
from datetime import datetime

from backend.core.calculations import MetricsCalculator, AnomalyDetector
from backend.ai.prompts import INSIGHT_TEMPLATES, DATA_CONTEXT


class OperationsReasoningEngine:
    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.calculator = MetricsCalculator()
        self.anomaly_detector = AnomalyDetector()

    def analyze_queue_compliance(self, date: datetime) -> Dict:
        queue_data = self.data_loader.load_queue_data()
        zone_compliance = queue_data["zone_compliance"]

        date_data = zone_compliance[zone_compliance["date"] == pd.to_datetime(date)]

        zone_performance = (
            date_data.groupby("zone")
            .agg({"actual_compliance_pct": "mean", "variance_from_target": "mean", "pax_total": "sum"})
            .reset_index()
        )
        zone_performance = zone_performance.sort_values("actual_compliance_pct")

        anomalies = self.anomaly_detector.detect_queue_anomalies(date_data)

        return {
            "overall_compliance": float(date_data["actual_compliance_pct"].mean()),
            "target": 95.0,
            "zones_below_target": int(len(zone_performance[zone_performance["actual_compliance_pct"] < 95])),
            "worst_zones": zone_performance.head(3).to_dict("records"),
            "worst_time_windows": date_data[date_data["actual_compliance_pct"] < 90]
            .sort_values("actual_compliance_pct")
            .head(5)
            .to_dict("records"),
            "anomalies": anomalies.to_dict("records") if len(anomalies) > 0 else [],
            "total_pax_affected": int(date_data[date_data["actual_compliance_pct"] < 95]["pax_total"].sum()),
        }

    def analyze_security_lanes(self, date: datetime) -> Dict:
        security_data = self.data_loader.load_security_data()
        daily_lanes = security_data["daily"]

        date_data = daily_lanes[daily_lanes["date"] == pd.to_datetime(date)]
        ranked_lanes = date_data.sort_values("cleared_volume", ascending=False)
        anomalies = self.anomaly_detector.detect_security_lane_anomalies(date_data)
        high_reject = date_data[date_data["reject_rate_pct"] > 8.0].sort_values("reject_rate_pct", ascending=False)

        return {
            "total_cleared": int(date_data["cleared_volume"].sum()),
            "avg_reject_rate": round(float(date_data["reject_rate_pct"].mean()), 2),
            "top_performing_lanes": ranked_lanes.head(5).to_dict("records"),
            "high_reject_lanes": high_reject.to_dict("records"),
            "anomalies": anomalies.to_dict("records") if len(anomalies) > 0 else [],
        }

    def analyze_passenger_volumes(self, date: datetime) -> Dict:
        pax_data = self.data_loader.load_passenger_data()
        daily_pax = pax_data["daily"]
        hourly_showup = pax_data["hourly_showup"]

        date_daily = daily_pax[daily_pax["date"] == pd.to_datetime(date)]
        date_hourly = hourly_showup[hourly_showup["date"] == pd.to_datetime(date)]

        hourly_by_hour = date_hourly.groupby("hour")["volume"].sum().reset_index()
        peak_hours = hourly_by_hour.nlargest(3, "volume")

        total_pax = int(date_daily["pax_count"].sum())
        domestic_pax = int(date_daily[date_daily["passenger_type"] == "Domestic"]["pax_count"].sum())
        intl_pax = int(date_daily[date_daily["passenger_type"] == "International"]["pax_count"].sum())

        vs_7day = round(float(date_daily["pax_count_vs_7day_pct"].mean()), 2) if "pax_count_vs_7day_pct" in date_daily.columns else 0.0

        return {
            "total_pax": total_pax,
            "domestic_pax": domestic_pax,
            "international_pax": intl_pax,
            "vs_7day_pct": vs_7day,
            "peak_hours": peak_hours.to_dict("records"),
            "hourly_distribution": hourly_by_hour.to_dict("records"),
        }

    def analyze_voc_sentiment(self, date: datetime) -> Dict:
        voc_data = self.data_loader.load_voc_data()
        feedback = voc_data["feedback"]
        messages = voc_data["messages"]

        date_feedback = feedback[feedback["date"] == pd.to_datetime(date)]
        date_messages = messages[messages["date"] == pd.to_datetime(date)]

        total_complaints = int(date_feedback["complaints"].sum())
        total_compliments = int(date_feedback["compliments"].sum())
        ratio = round(total_compliments / total_complaints, 2) if total_complaints > 0 else 0

        negative_msgs = date_messages[date_messages["sentiment"] == "negative"]

        terminal_feedback = date_feedback.groupby("terminal").agg({"complaints": "sum", "compliments": "sum"}).reset_index()
        terminal_feedback["ratio"] = terminal_feedback["compliments"] / terminal_feedback["complaints"].replace(0, 1)

        return {
            "total_complaints": total_complaints,
            "total_compliments": total_compliments,
            "ratio": ratio,
            "sentiment": "Good" if ratio >= 2.0 else "Needs Attention",
            "terminal_breakdown": terminal_feedback.to_dict("records"),
            "negative_messages": negative_msgs.head(10).to_dict("records"),
        }

    def generate_root_cause_analysis(self, date: datetime, zone: str, time_window: str) -> Dict:
        queue_analysis = self.analyze_queue_compliance(date)
        security_analysis = self.analyze_security_lanes(date)
        pax_analysis = self.analyze_passenger_volumes(date)

        factors = []

        peak_volumes = pax_analysis["hourly_distribution"]
        relevant_hours = [h for h in peak_volumes if 14 <= h["hour"] <= 16]
        if relevant_hours:
            avg_peak_vol = sum(h["volume"] for h in relevant_hours) / len(relevant_hours)
            factors.append(f"High passenger volumes during {time_window}: ~{int(avg_peak_vol):,} pax/hour")

        if security_analysis["high_reject_lanes"]:
            high_reject_lanes = [lane["lane"] for lane in security_analysis["high_reject_lanes"][:3]]
            factors.append(f"High reject rates at security lanes: {', '.join(high_reject_lanes)}")

        worst_zones = [z["zone"] for z in queue_analysis["worst_zones"]]
        if zone in worst_zones:
            factors.append(f"Check-in processing delays at {zone}")

        recommendations = [
            "Open additional security lanes (minimum 2) during 1400-1800 window",
            "Assign senior screeners to lanes with high reject rates (L6, L3)",
            "Implement queue marshaling at T2 check-in banks during peak hours",
            "Promote biometric fast-track lanes via digital signage",
        ]

        worst_compliance = queue_analysis["worst_zones"][0]["actual_compliance_pct"] if queue_analysis["worst_zones"] else 0

        return {
            "zone": zone,
            "time_window": time_window,
            "primary_issue": f"Queue compliance dropped to {worst_compliance:.1f}% (Target: 95%)",
            "factors": factors,
            "impact": f"{queue_analysis['total_pax_affected']:,} passengers experienced extended wait times",
            "recommendations": recommendations,
            "severity": "High" if queue_analysis["overall_compliance"] < 90 else "Medium",
        }

    def generate_executive_summary(self, date: datetime) -> str:
        queue = self.analyze_queue_compliance(date)
        security = self.analyze_security_lanes(date)
        pax = self.analyze_passenger_volumes(date)
        voc = self.analyze_voc_sentiment(date)

        findings = []
        findings.append(f"**Total Passengers:** {pax['total_pax']:,} ({pax['domestic_pax']:,} Domestic, {pax['international_pax']:,} International)")
        findings.append(f"**Overall Queue Compliance:** {queue['overall_compliance']:.1f}% (Target: 95%)")
        findings.append(f"**Zones Below Target:** {queue['zones_below_target']} zones")

        if pax["peak_hours"]:
            peak_hrs = [f"{int(h['hour']):02d}:00" for h in pax["peak_hours"][:3]]
            findings.append(f"**Peak Hours:** {', '.join(peak_hrs)}")

        findings.append(f"**Security Reject Rate:** {security['avg_reject_rate']}%")
        findings.append(f"**VOC Sentiment:** {voc['sentiment']} (Ratio: {voc['ratio']:.2f})")

        actions = []
        if queue["zones_below_target"] > 0:
            worst_zone = queue["worst_zones"][0]["zone"]
            actions.append(f"1. **Immediate:** Address queue delays at {worst_zone}")

        if security["high_reject_lanes"]:
            actions.append("2. **Today:** Retrain staff on lanes with high rejects")

        actions.append("3. **This Week:** Review staffing allocation during peak hours")

        if queue["overall_compliance"] >= 95:
            status = "**On Track** - All major KPIs meeting targets"
        elif queue["overall_compliance"] >= 90:
            status = "**Attention Needed** - Some zones below target"
        else:
            status = "**Action Required** - Multiple zones significantly below target"

        summary = INSIGHT_TEMPLATES["executive_summary"].format(
            date=date.strftime("%B %d, %Y"),
            findings="\n".join(f"- {f}" for f in findings),
            actions="\n".join(actions),
            status=status,
        )

        return summary
