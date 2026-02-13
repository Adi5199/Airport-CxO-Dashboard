from fastapi import APIRouter, Request, Query
from datetime import datetime
import pandas as pd
import numpy as np

router = APIRouter(prefix="/api/queue", tags=["queue"])


@router.get("/status")
def get_queue_status(request: Request, date: str = Query(default=None), terminals: str = Query(default="T1,T2")):
    dl = request.app.state.data_loader
    config = request.app.state.config
    report_date = pd.to_datetime(date) if date else pd.to_datetime(config["data"]["report_date"])
    terminal_list = terminals.split(",")

    zone_compliance = dl.load_queue_data()["zone_compliance"]
    report = zone_compliance[(zone_compliance["date"] == report_date) & (zone_compliance["terminal"].isin(terminal_list))]

    overall = round(float(report["actual_compliance_pct"].mean()), 1) if len(report) > 0 else 0
    total_zones = int(report["zone"].nunique())
    zones_below = int(len(report.groupby("zone")["actual_compliance_pct"].mean().reset_index().query("actual_compliance_pct < 95")))
    pax_affected = int(report[report["actual_compliance_pct"] < 95]["pax_total"].sum())
    target_achievement = round((total_zones - zones_below) / total_zones * 100, 0) if total_zones > 0 else 100

    return {
        "overall_compliance": overall,
        "zones_below_target": zones_below,
        "total_zones": total_zones,
        "pax_affected": pax_affected,
        "target_achievement_pct": target_achievement,
    }


@router.get("/zones")
def get_zones(request: Request, date: str = Query(default=None), terminals: str = Query(default="T1,T2")):
    dl = request.app.state.data_loader
    config = request.app.state.config
    report_date = pd.to_datetime(date) if date else pd.to_datetime(config["data"]["report_date"])
    terminal_list = terminals.split(",")

    zone_compliance = dl.load_queue_data()["zone_compliance"]
    report = zone_compliance[(zone_compliance["date"] == report_date) & (zone_compliance["terminal"].isin(terminal_list))]
    zones = sorted(report["zone"].unique().tolist())
    return {"zones": zones}


@router.get("/root-cause")
def get_root_cause(request: Request, date: str = Query(default=None), zone: str = "Check-in 34-86", time_window: str = "1400-1600", terminals: str = Query(default="T1,T2")):
    engine = request.app.state.reasoning_engine
    config = request.app.state.config
    report_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.strptime(config["data"]["report_date"], "%Y-%m-%d")
    terminal_list = terminals.split(",")

    result = engine.generate_root_cause_analysis(report_date, zone, time_window, terminal_list)
    return result


@router.get("/zone-detail")
def get_zone_detail(request: Request, date: str = Query(default=None), zone: str = Query(default="Check-in 34-86"), terminals: str = Query(default="T1,T2")):
    dl = request.app.state.data_loader
    config = request.app.state.config
    report_date = pd.to_datetime(date) if date else pd.to_datetime(config["data"]["report_date"])
    terminal_list = terminals.split(",")

    zone_compliance = dl.load_queue_data()["zone_compliance"]
    report = zone_compliance[(zone_compliance["date"] == report_date) & (zone_compliance["zone"] == zone) & (zone_compliance["terminal"].isin(terminal_list))]

    if len(report) == 0:
        return {"zone": zone, "avg_compliance": 0, "threshold_minutes": 0, "total_pax": 0, "avg_wait_time": 0, "time_series": []}

    avg_compliance = round(float(report["actual_compliance_pct"].mean()), 1)
    threshold = int(report.iloc[0]["threshold_minutes"])
    total_pax = int(report["pax_total"].sum())
    avg_wait = round(float(report["avg_wait_time_min"].mean()), 1)

    time_series = []
    for _, row in report.iterrows():
        time_series.append({
            "time_window": row["time_window"],
            "actual_compliance_pct": round(float(row["actual_compliance_pct"]), 1),
            "pax_total": int(row["pax_total"]),
            "avg_wait_time_min": round(float(row["avg_wait_time_min"]), 1),
        })

    return {
        "zone": zone,
        "avg_compliance": avg_compliance,
        "threshold_minutes": threshold,
        "total_pax": total_pax,
        "avg_wait_time": avg_wait,
        "time_series": time_series,
    }


@router.get("/heatmap")
def get_heatmap(request: Request, date: str = Query(default=None), terminals: str = Query(default="T1,T2")):
    dl = request.app.state.data_loader
    config = request.app.state.config
    report_date = pd.to_datetime(date) if date else pd.to_datetime(config["data"]["report_date"])
    terminal_list = terminals.split(",")

    zone_compliance = dl.load_queue_data()["zone_compliance"]
    report = zone_compliance[(zone_compliance["date"] == report_date) & (zone_compliance["terminal"].isin(terminal_list))]

    pivot = report.pivot_table(index="zone", columns="time_window", values="actual_compliance_pct", aggfunc="mean")

    zones = pivot.index.tolist()
    time_windows = pivot.columns.tolist()
    values = np.round(pivot.values, 1).tolist()

    return {"zones": zones, "time_windows": time_windows, "values": values}


@router.get("/table")
def get_table(request: Request, date: str = Query(default=None), terminals: str = Query(default="T1,T2"), violations_only: bool = False):
    dl = request.app.state.data_loader
    config = request.app.state.config
    report_date = pd.to_datetime(date) if date else pd.to_datetime(config["data"]["report_date"])
    terminal_list = terminals.split(",")

    zone_compliance = dl.load_queue_data()["zone_compliance"]
    report = zone_compliance[(zone_compliance["date"] == report_date) & (zone_compliance["terminal"].isin(terminal_list))]

    if violations_only:
        report = report[report["actual_compliance_pct"] < 95]

    report = report.sort_values("actual_compliance_pct")

    data = []
    for _, row in report.iterrows():
        data.append({
            "zone": row["zone"],
            "terminal": row["terminal"],
            "time_window": row["time_window"],
            "actual_compliance_pct": round(float(row["actual_compliance_pct"]), 1),
            "target_compliance_pct": round(float(row["target_compliance_pct"]), 1),
            "variance_from_target": round(float(row["variance_from_target"]), 1),
            "pax_total": int(row["pax_total"]),
            "avg_wait_time_min": round(float(row["avg_wait_time_min"]), 1),
        })

    return {"data": data}
