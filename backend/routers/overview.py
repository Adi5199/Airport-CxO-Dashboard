from fastapi import APIRouter, Request, Query
from datetime import datetime, timedelta
import pandas as pd

router = APIRouter(prefix="/api/overview", tags=["overview"])


@router.get("/kpis")
def get_kpis(request: Request, date: str = Query(default=None), terminals: str = Query(default="T1,T2")):
    dl = request.app.state.data_loader
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

    # ATM data
    atm_data = dl.load_atm_data()
    report_atm = atm_data[(atm_data["date"] == report_date) & (atm_data["terminal"].isin(terminal_list))]
    total_atm = int(report_atm["atm_count"].sum())

    queue_data = dl.load_queue_data()
    zone_compliance = queue_data["zone_compliance"]
    report_compliance = zone_compliance[(zone_compliance["date"] == report_date) & (zone_compliance["terminal"].isin(terminal_list))]
    avg_compliance = round(float(report_compliance["actual_compliance_pct"].mean()), 1) if len(report_compliance) > 0 else 0

    voc_data = dl.load_voc_data()
    voc_feedback = voc_data["feedback"]
    report_voc = voc_feedback[(voc_feedback["date"] == report_date) & (voc_feedback["terminal"].isin(terminal_list))]
    total_complaints = int(report_voc["complaints"].sum()) if len(report_voc) > 0 else 0
    total_compliments = int(report_voc["compliments"].sum()) if len(report_voc) > 0 else 0
    voc_ratio = round(total_compliments / total_complaints, 2) if total_complaints > 0 else 0

    # OTP data
    otp_data = dl.load_otp_data()
    report_otp = otp_data[(otp_data["date"] == report_date) & (otp_data["terminal"].isin(terminal_list))]
    otp_pct = round(float(report_otp["otp_pct"].mean()), 1) if len(report_otp) > 0 else 0

    # Baggage delivery data
    bag_delivery = dl.load_baggage_delivery_data()
    report_bag = bag_delivery[(bag_delivery["date"] == report_date) & (bag_delivery["terminal"].isin(terminal_list))]
    bag_delivery_pct = round(float(report_bag["delivery_pct"].mean()), 1) if len(report_bag) > 0 else 0
    first_bag_min = round(float(report_bag["first_bag_minutes"].mean()), 1) if len(report_bag) > 0 else 0
    last_bag_min = round(float(report_bag["last_bag_minutes"].mean()), 1) if len(report_bag) > 0 else 0

    # Safety issues
    safety_data = dl.load_safety_data()
    report_safety = safety_data[(safety_data["date"] == report_date) & (safety_data["terminal"].isin(terminal_list))]
    safety_issues = len(report_safety)

    # Slot adherence
    slot_data = dl.load_slot_adherence_data()
    report_slot = slot_data[(slot_data["date"] == report_date) & (slot_data["terminal"].isin(terminal_list))]
    slot_adherence_pct = round(float(report_slot["adherence_pct"].mean()), 1) if len(report_slot) > 0 else 0

    return {
        "total_pax": total_pax,
        "domestic_pax": domestic_pax,
        "international_pax": intl_pax,
        "pax_vs_7day_pct": pax_vs_7day,
        "total_atm": total_atm,
        "queue_compliance_pct": avg_compliance,
        "compliance_delta": round(avg_compliance - 95.0, 1),
        "voc_ratio": voc_ratio,
        "total_complaints": total_complaints,
        "total_compliments": total_compliments,
        "otp_pct": otp_pct,
        "baggage_delivery_pct": bag_delivery_pct,
        "first_bag_minutes": first_bag_min,
        "last_bag_minutes": last_bag_min,
        "safety_issues": safety_issues,
        "slot_adherence_pct": slot_adherence_pct,
    }


@router.get("/executive-summary")
def get_executive_summary(request: Request, date: str = Query(default=None), terminals: str = Query(default="T1,T2")):
    engine = request.app.state.reasoning_engine
    dl = request.app.state.data_loader
    config = request.app.state.config
    report_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.strptime(config["data"]["report_date"], "%Y-%m-%d")
    terminal_list = terminals.split(",")

    queue = engine.analyze_queue_compliance(report_date, terminal_list)
    security = engine.analyze_security_lanes(report_date, terminal_list)
    pax = engine.analyze_passenger_volumes(report_date, terminal_list)
    voc = engine.analyze_voc_sentiment(report_date, terminal_list)

    # OTP
    otp_data = dl.load_otp_data()
    pd_date = pd.to_datetime(report_date)
    report_otp = otp_data[(otp_data["date"] == pd_date) & (otp_data["terminal"].isin(terminal_list))]
    otp_pct = round(float(report_otp["otp_pct"].mean()), 1) if len(report_otp) > 0 else 0

    # Baggage delivery
    bag_delivery = dl.load_baggage_delivery_data()
    report_bag = bag_delivery[(bag_delivery["date"] == pd_date) & (bag_delivery["terminal"].isin(terminal_list))]
    bag_delivery_pct = round(float(report_bag["delivery_pct"].mean()), 1) if len(report_bag) > 0 else 0

    # Determine overall status
    if queue["overall_compliance"] >= 95 and otp_pct >= 85:
        status = "on_track"
        status_label = "On Track"
        status_detail = "All major KPIs meeting targets"
    elif queue["overall_compliance"] >= 90:
        status = "attention"
        status_label = "Attention Needed"
        status_detail = "Some KPIs need monitoring"
    else:
        status = "critical"
        status_label = "Action Required"
        status_detail = "Multiple zones significantly below target"

    terminal_label = "Overall" if len(terminal_list) > 1 else terminal_list[0]

    actions = []
    if queue["zones_below_target"] > 0 and queue["worst_zones"]:
        worst_zone = queue["worst_zones"][0]["zone"]
        actions.append({"priority": "Immediate", "action": f"Address queue delays at {worst_zone} ({terminal_label})"})
    if otp_pct < 85:
        actions.append({"priority": "Today", "action": f"Review on-time performance ({otp_pct}%) — coordinate with ATC and airlines ({terminal_label})"})
    if bag_delivery_pct < 90:
        actions.append({"priority": "Today", "action": f"Baggage delivery at {bag_delivery_pct}% — review belt allocation ({terminal_label})"})
    if security["high_reject_lanes"]:
        top_lane = security["high_reject_lanes"][0]
        actions.append({"priority": "Today", "action": f"Review {top_lane['lane']} ({round(top_lane['reject_rate_pct'], 1)}% reject rate)"})
    if voc["ratio"] < 2.0:
        actions.append({"priority": "Today", "action": f"Customer sentiment needs attention — VOC ratio {voc['ratio']}:1 ({terminal_label})"})
    actions.append({"priority": "This Week", "action": f"Review staffing allocation during peak hours ({terminal_label})"})

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
        "otp_pct": otp_pct,
        "baggage_delivery_pct": bag_delivery_pct,
        "voc_ratio": round(voc["ratio"], 2),
        "voc_sentiment": voc["sentiment"],
        "total_complaints": voc["total_complaints"],
        "total_compliments": voc["total_compliments"],
        "actions": actions,
    }


@router.get("/pax-trend")
def get_pax_trend(request: Request, days: int = 15, end_date: str = Query(default=None), terminals: str = Query(default="T1,T2")):
    dl = request.app.state.data_loader
    config = request.app.state.config
    end = pd.to_datetime(end_date) if end_date else pd.to_datetime(config["data"]["report_date"])
    start = end - timedelta(days=days - 1)
    terminal_list = terminals.split(",")

    daily_pax = dl.load_passenger_data()["daily"]
    trend = daily_pax[(daily_pax["date"] >= start) & (daily_pax["date"] <= end) & (daily_pax["terminal"].isin(terminal_list))]

    # Bifurcated by Dom/Int
    dom_trend = trend[trend["passenger_type"] == "Domestic"].groupby("date")["pax_count"].sum().reset_index()
    intl_trend = trend[trend["passenger_type"] == "International"].groupby("date")["pax_count"].sum().reset_index()
    total_trend = trend.groupby("date")["pax_count"].sum().reset_index()

    # Merge
    merged = total_trend.rename(columns={"pax_count": "total"})
    dom_agg = dom_trend.rename(columns={"pax_count": "domestic"})
    intl_agg = intl_trend.rename(columns={"pax_count": "international"})
    merged = merged.merge(dom_agg, on="date", how="left").merge(intl_agg, on="date", how="left").fillna(0)

    return {"data": [
        {
            "date": row["date"].strftime("%Y-%m-%d"),
            "total": int(row["total"]),
            "domestic": int(row["domestic"]),
            "international": int(row["international"]),
        }
        for _, row in merged.iterrows()
    ]}


@router.get("/atm-trend")
def get_atm_trend(request: Request, days: int = 15, end_date: str = Query(default=None), terminals: str = Query(default="T1,T2")):
    dl = request.app.state.data_loader
    config = request.app.state.config
    end = pd.to_datetime(end_date) if end_date else pd.to_datetime(config["data"]["report_date"])
    start = end - timedelta(days=days - 1)
    terminal_list = terminals.split(",")

    atm_data = dl.load_atm_data()
    trend = atm_data[(atm_data["date"] >= start) & (atm_data["date"] <= end) & (atm_data["terminal"].isin(terminal_list))]

    dom_trend = trend[trend["type"] == "Domestic"].groupby("date")["atm_count"].sum().reset_index()
    intl_trend = trend[trend["type"] == "International"].groupby("date")["atm_count"].sum().reset_index()
    total_trend = trend.groupby("date")["atm_count"].sum().reset_index()

    merged = total_trend.rename(columns={"atm_count": "total"})
    dom_agg = dom_trend.rename(columns={"atm_count": "domestic"})
    intl_agg = intl_trend.rename(columns={"atm_count": "international"})
    merged = merged.merge(dom_agg, on="date", how="left").merge(intl_agg, on="date", how="left").fillna(0)

    return {"data": [
        {
            "date": row["date"].strftime("%Y-%m-%d"),
            "total": int(row["total"]),
            "domestic": int(row["domestic"]),
            "international": int(row["international"]),
        }
        for _, row in merged.iterrows()
    ]}


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
def get_zone_compliance_summary(request: Request, date: str = Query(default=None), terminals: str = Query(default="T1,T2")):
    dl = request.app.state.data_loader
    config = request.app.state.config
    report_date = pd.to_datetime(date) if date else pd.to_datetime(config["data"]["report_date"])
    terminal_list = terminals.split(",")

    zone_compliance = dl.load_queue_data()["zone_compliance"]
    report = zone_compliance[(zone_compliance["date"] == report_date) & (zone_compliance["terminal"].isin(terminal_list))]
    summary = report.groupby("zone")["actual_compliance_pct"].mean().reset_index()
    summary = summary.sort_values("actual_compliance_pct")

    return {"data": [{"zone": row["zone"], "actual_compliance_pct": round(float(row["actual_compliance_pct"]), 1)} for _, row in summary.iterrows()]}


@router.get("/alerts")
def get_alerts(request: Request, date: str = Query(default=None), terminals: str = Query(default="T1,T2")):
    dl = request.app.state.data_loader
    config = request.app.state.config
    report_date = pd.to_datetime(date) if date else pd.to_datetime(config["data"]["report_date"])
    terminal_list = terminals.split(",")

    zone_compliance = dl.load_queue_data()["zone_compliance"]
    report = zone_compliance[(zone_compliance["date"] == report_date) & (zone_compliance["terminal"].isin(terminal_list))]
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

    # Safety alerts
    safety_data = dl.load_safety_data()
    report_safety = safety_data[(safety_data["date"] == report_date) & (safety_data["terminal"].isin(terminal_list))]
    safety_alerts = []
    for _, row in report_safety.iterrows():
        safety_alerts.append({
            "category": row["category"],
            "terminal": row["terminal"],
            "severity": row["severity"],
            "resolved": bool(row["resolved"]),
        })

    return {"queue_alerts": queue_alerts, "safety_alerts": safety_alerts}
