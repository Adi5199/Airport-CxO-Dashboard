from fastapi import APIRouter, Request, Query
from datetime import datetime, timedelta
import pandas as pd

router = APIRouter(prefix="/api/overview", tags=["overview"])


@router.get("/kpis")
def get_kpis(request: Request, date: str = Query(default=None), terminals: str = Query(default="T1,T2")):
    dl = request.app.state.data_loader
    engine = request.app.state.reasoning_engine
    config = request.app.state.config

    report_date = pd.to_datetime(date) if date else pd.to_datetime(config["data"]["report_date"])
    terminal_list = terminals.split(",")

    pax_data = dl.load_passenger_data()
    daily_pax = pax_data["daily"]
    report_pax = daily_pax[(daily_pax["date"] == report_date) & (daily_pax["terminal"].isin(terminal_list))]

    total_pax = int(report_pax["pax_count"].sum())
    domestic_pax = int(report_pax[report_pax["passenger_type"] == "Domestic"]["pax_count"].sum())
    intl_pax = int(report_pax[report_pax["passenger_type"] == "International"]["pax_count"].sum())
    pax_vs_7day = round(float(report_pax["pax_count_vs_7day_pct"].mean()), 1) if "pax_count_vs_7day_pct" in report_pax.columns and len(report_pax) > 0 else 0.0

    queue_data = dl.load_queue_data()
    zone_compliance = queue_data["zone_compliance"]
    report_compliance = zone_compliance[(zone_compliance["date"] == report_date) & (zone_compliance["terminal"].isin(terminal_list))]
    avg_compliance = round(float(report_compliance["actual_compliance_pct"].mean()), 1) if len(report_compliance) > 0 else 0

    security_data = dl.load_security_data()
    security_daily = security_data["daily"]
    report_security = security_daily[(security_daily["date"] == report_date) & (security_daily["terminal"].isin(terminal_list))]
    avg_reject = round(float(report_security["reject_rate_pct"].mean()), 1) if len(report_security) > 0 else 0

    voc_data = dl.load_voc_data()
    voc_feedback = voc_data["feedback"]
    report_voc = voc_feedback[(voc_feedback["date"] == report_date) & (voc_feedback["terminal"].isin(terminal_list))]
    total_complaints = int(report_voc["complaints"].sum()) if len(report_voc) > 0 else 0
    total_compliments = int(report_voc["compliments"].sum()) if len(report_voc) > 0 else 0
    voc_ratio = round(total_compliments / total_complaints, 2) if total_complaints > 0 else 0

    biometric_data = dl.load_biometric_data()
    report_bio = biometric_data[(biometric_data["date"] == report_date) & (biometric_data["terminal"].isin(terminal_list))]
    bio_adoption = 0.0
    if len(report_bio) > 0 and "total_eligible_pax" in report_bio.columns:
        total_eligible = report_bio["total_eligible_pax"].sum()
        total_registered = report_bio["biometric_registrations"].sum()
        bio_adoption = round(float(total_registered / total_eligible * 100), 1) if total_eligible > 0 else 0.0

    return {
        "total_pax": total_pax,
        "domestic_pax": domestic_pax,
        "international_pax": intl_pax,
        "pax_vs_7day_pct": pax_vs_7day,
        "queue_compliance_pct": avg_compliance,
        "compliance_delta": round(avg_compliance - 95.0, 1),
        "avg_reject_rate": avg_reject,
        "voc_ratio": voc_ratio,
        "total_complaints": total_complaints,
        "total_compliments": total_compliments,
        "biometric_adoption_pct": bio_adoption,
    }


@router.get("/executive-summary")
def get_executive_summary(request: Request, date: str = Query(default=None)):
    engine = request.app.state.reasoning_engine
    config = request.app.state.config
    report_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.strptime(config["data"]["report_date"], "%Y-%m-%d")

    queue = engine.analyze_queue_compliance(report_date)
    security = engine.analyze_security_lanes(report_date)
    pax = engine.analyze_passenger_volumes(report_date)
    voc = engine.analyze_voc_sentiment(report_date)

    # Determine overall status
    if queue["overall_compliance"] >= 95:
        status = "on_track"
        status_label = "On Track"
        status_detail = "All major KPIs meeting targets"
    elif queue["overall_compliance"] >= 90:
        status = "attention"
        status_label = "Attention Needed"
        status_detail = "Some zones below target"
    else:
        status = "critical"
        status_label = "Action Required"
        status_detail = "Multiple zones significantly below target"

    peak_hours = []
    if pax.get("peak_hours"):
        peak_hours = [f"{int(h['hour']):02d}:00" for h in pax["peak_hours"][:3]]

    actions = []
    if queue["zones_below_target"] > 0:
        worst_zone = queue["worst_zones"][0]["zone"]
        actions.append({"priority": "Immediate", "action": f"Address queue delays at {worst_zone}"})
    if security["high_reject_lanes"]:
        top_lane = security["high_reject_lanes"][0]
        actions.append({"priority": "Today", "action": f"Review {top_lane['lane']} ({round(top_lane['reject_rate_pct'], 1)}% reject rate)"})
    actions.append({"priority": "This Week", "action": "Review staffing allocation during peak hours"})

    return {
        "date": report_date.strftime("%B %d, %Y"),
        "status": status,
        "status_label": status_label,
        "status_detail": status_detail,
        "total_pax": pax["total_pax"],
        "domestic_pax": pax["domestic_pax"],
        "international_pax": pax["international_pax"],
        "pax_vs_7day_pct": pax["vs_7day_pct"],
        "queue_compliance": round(queue["overall_compliance"], 1),
        "zones_below_target": queue["zones_below_target"],
        "avg_reject_rate": security["avg_reject_rate"],
        "high_reject_lanes": len(security["high_reject_lanes"]),
        "voc_ratio": round(voc["ratio"], 2),
        "voc_sentiment": voc["sentiment"],
        "total_complaints": voc["total_complaints"],
        "total_compliments": voc["total_compliments"],
        "peak_hours": peak_hours,
        "actions": actions,
    }


@router.get("/pax-trend")
def get_pax_trend(request: Request, days: int = 15, end_date: str = Query(default=None)):
    dl = request.app.state.data_loader
    config = request.app.state.config
    end = pd.to_datetime(end_date) if end_date else pd.to_datetime(config["data"]["report_date"])
    start = end - timedelta(days=days - 1)

    daily_pax = dl.load_passenger_data()["daily"]
    trend = daily_pax[(daily_pax["date"] >= start) & (daily_pax["date"] <= end)]
    trend_agg = trend.groupby("date")["pax_count"].sum().reset_index()

    return {"data": [{"date": row["date"].strftime("%Y-%m-%d"), "pax_count": int(row["pax_count"])} for _, row in trend_agg.iterrows()]}


@router.get("/atm-trend")
def get_atm_trend(request: Request, days: int = 15, end_date: str = Query(default=None)):
    dl = request.app.state.data_loader
    config = request.app.state.config
    end = pd.to_datetime(end_date) if end_date else pd.to_datetime(config["data"]["report_date"])
    start = end - timedelta(days=days - 1)

    atm_data = dl.load_atm_data()
    trend = atm_data[(atm_data["date"] >= start) & (atm_data["date"] <= end)]
    trend_agg = trend.groupby("date")["atm_count"].sum().reset_index()

    return {"data": [{"date": row["date"].strftime("%Y-%m-%d"), "atm_count": int(row["atm_count"])} for _, row in trend_agg.iterrows()]}


@router.get("/terminal-breakdown")
def get_terminal_breakdown(request: Request, date: str = Query(default=None)):
    dl = request.app.state.data_loader
    config = request.app.state.config
    report_date = pd.to_datetime(date) if date else pd.to_datetime(config["data"]["report_date"])

    daily_pax = dl.load_passenger_data()["daily"]
    report_pax = daily_pax[daily_pax["date"] == report_date]
    breakdown = report_pax.groupby(["terminal", "flow"])["pax_count"].sum().reset_index()

    return {"data": [{"terminal": row["terminal"], "flow": row["flow"], "pax_count": int(row["pax_count"])} for _, row in breakdown.iterrows()]}


@router.get("/zone-compliance-summary")
def get_zone_compliance_summary(request: Request, date: str = Query(default=None)):
    dl = request.app.state.data_loader
    config = request.app.state.config
    report_date = pd.to_datetime(date) if date else pd.to_datetime(config["data"]["report_date"])

    zone_compliance = dl.load_queue_data()["zone_compliance"]
    report = zone_compliance[zone_compliance["date"] == report_date]
    summary = report.groupby("zone")["actual_compliance_pct"].mean().reset_index()
    summary = summary.sort_values("actual_compliance_pct")

    return {"data": [{"zone": row["zone"], "actual_compliance_pct": round(float(row["actual_compliance_pct"]), 1)} for _, row in summary.iterrows()]}


@router.get("/alerts")
def get_alerts(request: Request, date: str = Query(default=None)):
    dl = request.app.state.data_loader
    config = request.app.state.config
    report_date = pd.to_datetime(date) if date else pd.to_datetime(config["data"]["report_date"])

    zone_compliance = dl.load_queue_data()["zone_compliance"]
    report = zone_compliance[zone_compliance["date"] == report_date]
    below_target = report[report["actual_compliance_pct"] < 95].sort_values("actual_compliance_pct").head(5)

    queue_alerts = []
    for _, row in below_target.iterrows():
        queue_alerts.append({
            "zone": row["zone"],
            "time_window": row["time_window"],
            "compliance": round(float(row["actual_compliance_pct"]), 1),
            "pax_affected": int(row["pax_total"]),
            "variance": round(float(row["variance_from_target"]), 1),
        })

    security_daily = dl.load_security_data()["daily"]
    report_security = security_daily[security_daily["date"] == report_date]
    high_reject = report_security[report_security["reject_rate_pct"] > 8].sort_values("reject_rate_pct", ascending=False)

    security_alerts = []
    for _, row in high_reject.iterrows():
        security_alerts.append({
            "lane": row["lane"],
            "terminal": row["terminal"],
            "reject_rate": round(float(row["reject_rate_pct"]), 1),
            "reject_count": int(row["reject_count"]),
        })

    return {"queue_alerts": queue_alerts, "security_alerts": security_alerts}
