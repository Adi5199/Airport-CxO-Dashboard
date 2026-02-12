from fastapi import APIRouter, Request, Query
from datetime import timedelta
import pandas as pd

router = APIRouter(prefix="/api/trends", tags=["trends"])


@router.get("/passenger")
def get_passenger_trends(request: Request, days: int = 30, end_date: str = Query(default=None), group_by: str = "passenger_type"):
    dl = request.app.state.data_loader
    config = request.app.state.config
    end = pd.to_datetime(end_date) if end_date else pd.to_datetime(config["data"]["report_date"])
    start = end - timedelta(days=days)

    daily_pax = dl.load_passenger_data()["daily"]
    trend = daily_pax[(daily_pax["date"] >= start) & (daily_pax["date"] <= end)]

    if group_by in trend.columns:
        grouped = trend.groupby(["date", group_by])["pax_count"].sum().reset_index()
        data = []
        for _, row in grouped.iterrows():
            data.append({
                "date": row["date"].strftime("%Y-%m-%d"),
                group_by: row[group_by],
                "pax_count": int(row["pax_count"]),
            })
    else:
        grouped = trend.groupby("date")["pax_count"].sum().reset_index()
        data = [{"date": row["date"].strftime("%Y-%m-%d"), "pax_count": int(row["pax_count"])} for _, row in grouped.iterrows()]

    return {"data": data}


@router.get("/biometric")
def get_biometric_trends(request: Request, days: int = 30, end_date: str = Query(default=None)):
    dl = request.app.state.data_loader
    config = request.app.state.config
    end = pd.to_datetime(end_date) if end_date else pd.to_datetime(config["data"]["report_date"])
    start = end - timedelta(days=days)

    bio_data = dl.load_biometric_data()
    trend = bio_data[(bio_data["date"] >= start) & (bio_data["date"] <= end)]

    daily_agg = trend.groupby(["date", "terminal"]).agg({
        "total_eligible_pax": "sum",
        "biometric_registrations": "sum",
        "successful_boardings": "sum",
    }).reset_index()

    daily_agg["adoption_pct"] = (daily_agg["biometric_registrations"] / daily_agg["total_eligible_pax"] * 100).round(1)
    daily_agg["success_rate"] = (daily_agg["successful_boardings"] / daily_agg["biometric_registrations"].replace(0, 1) * 100).round(1)

    daily = []
    for _, row in daily_agg.iterrows():
        daily.append({
            "date": row["date"].strftime("%Y-%m-%d"),
            "terminal": row["terminal"],
            "adoption_pct": float(row["adoption_pct"]),
            "success_rate": float(row["success_rate"]),
            "total_eligible": int(row["total_eligible_pax"]),
            "registrations": int(row["biometric_registrations"]),
        })

    # Channel breakdown for latest date
    latest = trend[trend["date"] == end]
    channels = []
    if "channel" in latest.columns:
        channel_agg = latest.groupby("channel")["biometric_registrations"].sum().reset_index()
        for _, row in channel_agg.iterrows():
            channels.append({"channel": row["channel"], "registrations": int(row["biometric_registrations"])})

    return {"daily": daily, "channels": channels}


@router.get("/voc")
def get_voc_trends(request: Request, days: int = 30, end_date: str = Query(default=None)):
    dl = request.app.state.data_loader
    config = request.app.state.config
    end = pd.to_datetime(end_date) if end_date else pd.to_datetime(config["data"]["report_date"])
    start = end - timedelta(days=days)

    voc_data = dl.load_voc_data()
    feedback = voc_data["feedback"]
    messages = voc_data["messages"]

    trend = feedback[(feedback["date"] >= start) & (feedback["date"] <= end)]

    # Daily aggregation
    voc_daily = trend.groupby("date").agg({"complaints": "sum", "compliments": "sum"}).reset_index()
    voc_daily["ratio"] = (voc_daily["compliments"] / voc_daily["complaints"].replace(0, 1)).round(2)

    daily = []
    for _, row in voc_daily.iterrows():
        daily.append({
            "date": row["date"].strftime("%Y-%m-%d"),
            "complaints": int(row["complaints"]),
            "compliments": int(row["compliments"]),
            "ratio": float(row["ratio"]),
        })

    # By terminal
    terminal_agg = trend.groupby("terminal").agg({"complaints": "sum", "compliments": "sum"}).reset_index()
    terminal_agg["ratio"] = (terminal_agg["compliments"] / terminal_agg["complaints"].replace(0, 1)).round(2)
    by_terminal = [{"terminal": r["terminal"], "complaints": int(r["complaints"]), "compliments": int(r["compliments"]), "ratio": float(r["ratio"])} for _, r in terminal_agg.iterrows()]

    # By media
    by_media = []
    if "media_type" in trend.columns:
        media_agg = trend.groupby("media_type")["total_feedback"].sum().reset_index().sort_values("total_feedback", ascending=False)
        by_media = [{"media_type": r["media_type"], "total_feedback": int(r["total_feedback"])} for _, r in media_agg.iterrows()]

    # Recent messages
    report_messages = messages[messages["date"] == end].head(10)
    recent = []
    for _, row in report_messages.iterrows():
        recent.append({
            "terminal": row["terminal"],
            "department": row["department"],
            "media": row["media"],
            "message": row["message"],
            "sentiment": row["sentiment"],
        })

    return {"daily": daily, "by_terminal": by_terminal, "by_media": by_media, "recent_messages": recent}
