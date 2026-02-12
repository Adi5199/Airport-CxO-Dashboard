from fastapi import APIRouter, Request, Query
import pandas as pd

router = APIRouter(prefix="/api/security", tags=["security"])


@router.get("/summary")
def get_security_summary(request: Request, date: str = Query(default=None)):
    dl = request.app.state.data_loader
    config = request.app.state.config
    report_date = pd.to_datetime(date) if date else pd.to_datetime(config["data"]["report_date"])

    security_daily = dl.load_security_data()["daily"]
    report = security_daily[security_daily["date"] == report_date]

    return {
        "total_cleared": int(report["cleared_volume"].sum()),
        "avg_reject_rate": round(float(report["reject_rate_pct"].mean()), 1),
        "high_reject_lanes_count": int(len(report[report["reject_rate_pct"] > 8])),
    }


@router.get("/lanes")
def get_lanes(request: Request, date: str = Query(default=None)):
    dl = request.app.state.data_loader
    config = request.app.state.config
    report_date = pd.to_datetime(date) if date else pd.to_datetime(config["data"]["report_date"])

    security_daily = dl.load_security_data()["daily"]
    report = security_daily[security_daily["date"] == report_date].sort_values("cleared_volume", ascending=False)

    data = []
    for _, row in report.iterrows():
        data.append({
            "lane": row["lane"],
            "terminal": row["terminal"],
            "lane_group": row.get("lane_group", ""),
            "cleared_volume": int(row["cleared_volume"]),
            "reject_count": int(row["reject_count"]),
            "reject_rate_pct": round(float(row["reject_rate_pct"]), 1),
            "total_scanned": int(row.get("total_scanned", row["cleared_volume"] + row["reject_count"])),
            "avg_throughput_per_hour": round(float(row.get("avg_throughput_per_hour", 0)), 1),
        })

    return {"data": data}


@router.get("/high-reject")
def get_high_reject(request: Request, date: str = Query(default=None), threshold: float = 8.0):
    dl = request.app.state.data_loader
    config = request.app.state.config
    report_date = pd.to_datetime(date) if date else pd.to_datetime(config["data"]["report_date"])

    security_daily = dl.load_security_data()["daily"]
    report = security_daily[security_daily["date"] == report_date]
    high = report[report["reject_rate_pct"] > threshold].sort_values("reject_rate_pct", ascending=False)

    lanes = []
    for _, row in high.iterrows():
        lanes.append({
            "lane": row["lane"],
            "terminal": row["terminal"],
            "reject_rate_pct": round(float(row["reject_rate_pct"]), 1),
            "reject_count": int(row["reject_count"]),
            "cleared_volume": int(row["cleared_volume"]),
        })

    return {"lanes": lanes}


@router.get("/baggage")
def get_baggage(request: Request, date: str = Query(default=None)):
    dl = request.app.state.data_loader
    config = request.app.state.config
    report_date = pd.to_datetime(date) if date else pd.to_datetime(config["data"]["report_date"])

    baggage_data = dl.load_baggage_data()
    report = baggage_data[baggage_data["date"] == report_date]

    summary = {
        "total_flights": int(report["flights"].sum()),
        "total_pax": int(report["pax"].sum()),
        "avg_pax_per_flight": round(float(report["pax_per_flight"].mean()), 0) if len(report) > 0 else 0,
    }

    belts = []
    for _, row in report.iterrows():
        belts.append({
            "belt": row["belt"],
            "belt_type": row["belt_type"],
            "utilization_pct": round(float(row["utilization_pct"]), 1),
            "flights": int(row["flights"]),
            "pax": int(row["pax"]),
        })

    return {"summary": summary, "belts": belts}


@router.get("/gates")
def get_gates(request: Request, date: str = Query(default=None)):
    dl = request.app.state.data_loader
    config = request.app.state.config
    report_date = pd.to_datetime(date) if date else pd.to_datetime(config["data"]["report_date"])

    gate_data = dl.load_gate_data()
    report = gate_data[gate_data["date"] == report_date]

    boarding_mix = {}
    mix_df = report.groupby(["terminal", "boarding_mode"]).agg({"flights": "sum", "pax": "sum"}).reset_index()
    for terminal in ["T1", "T2"]:
        t_data = mix_df[mix_df["terminal"] == terminal]
        total_pax = t_data["pax"].sum()
        entries = []
        for _, row in t_data.iterrows():
            entries.append({
                "boarding_mode": row["boarding_mode"],
                "flights": int(row["flights"]),
                "pax": int(row["pax"]),
                "pax_pct": round(float(row["pax"] / total_pax * 100), 1) if total_pax > 0 else 0,
            })
        boarding_mix[terminal] = entries

    gates = []
    for _, row in report.sort_values("pax", ascending=False).iterrows():
        gates.append({
            "gate": row["gate"],
            "terminal": row["terminal"],
            "boarding_mode": row["boarding_mode"],
            "flights": int(row["flights"]),
            "pax": int(row["pax"]),
            "pax_per_flight": round(float(row["pax_per_flight"]), 0),
        })

    return {"boarding_mix": boarding_mix, "gates": gates}
