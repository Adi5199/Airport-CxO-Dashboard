from fastapi import APIRouter, Request, Query
from datetime import datetime, timedelta
import pandas as pd

router = APIRouter(prefix="/api/compliance", tags=["compliance"])


@router.get("/summary")
def get_compliance_summary(request: Request, date: str = Query(default=None), terminals: str = Query(default="T1,T2")):
    """Get compliance issues summary by category"""
    dl = request.app.state.data_loader
    config = request.app.state.config
    report_date = pd.to_datetime(date) if date else pd.to_datetime(config["data"]["report_date"])
    terminal_list = terminals.split(",")

    # Queue compliance violations (Operational)
    zone_compliance = dl.load_queue_data()["zone_compliance"]
    report = zone_compliance[(zone_compliance["date"] == report_date) & (zone_compliance["terminal"].isin(terminal_list))]
    queue_violations = int(len(report[report["actual_compliance_pct"] < 95]))

    # Safety issues (Regulatory)
    safety_data = dl.load_safety_data()
    report_safety = safety_data[(safety_data["date"] == report_date) & (safety_data["terminal"].isin(terminal_list))]
    safety_issues = len(report_safety)
    unresolved_safety = int(len(report_safety[report_safety["resolved"] == False])) if len(report_safety) > 0 else 0

    # OTP violations (Operational / Regulatory)
    otp_data = dl.load_otp_data()
    report_otp = otp_data[(otp_data["date"] == report_date) & (otp_data["terminal"].isin(terminal_list))]
    otp_violations = int(len(report_otp[report_otp["otp_pct"] < 80])) if len(report_otp) > 0 else 0

    # Slot adherence violations (Regulatory)
    slot_data = dl.load_slot_adherence_data()
    report_slot = slot_data[(slot_data["date"] == report_date) & (slot_data["terminal"].isin(terminal_list))]
    slot_violations = int(report_slot["late_slots"].sum()) if len(report_slot) > 0 else 0

    categories = [
        {
            "category": "Operational",
            "icon": "Settings",
            "issues": queue_violations + (1 if otp_violations > 0 else 0),
            "description": f"{queue_violations} queue compliance breaches, {otp_violations} OTP violations",
            "severity": "high" if queue_violations > 5 else "medium" if queue_violations > 2 else "low",
        },
        {
            "category": "Regulatory",
            "icon": "Scale",
            "issues": safety_issues + (1 if slot_violations > 5 else 0),
            "description": f"{safety_issues} safety events, {slot_violations} slot adherence deviations",
            "severity": "high" if unresolved_safety > 2 else "medium" if safety_issues > 3 else "low",
        },
        {
            "category": "Legal",
            "icon": "Gavel",
            "issues": 0,
            "description": "No active legal compliance events",
            "severity": "low",
        },
        {
            "category": "Internal SOPs",
            "icon": "BookOpen",
            "issues": max(0, queue_violations - 3) + (1 if unresolved_safety > 0 else 0),
            "description": f"SOP deviations in queue management and safety protocols",
            "severity": "medium" if queue_violations > 3 else "low",
        },
    ]

    return {
        "total_issues": sum(c["issues"] for c in categories),
        "categories": categories,
    }


@router.get("/upcoming-tasks")
def get_upcoming_tasks(request: Request, date: str = Query(default=None)):
    """Get upcoming compliance tasks and deadlines"""
    config = request.app.state.config
    report_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.strptime(config["data"]["report_date"], "%Y-%m-%d")

    tasks = [
        {
            "id": 1,
            "title": "DGCA Safety Audit Preparation",
            "category": "Regulatory",
            "deadline": (report_date + timedelta(days=5)).strftime("%Y-%m-%d"),
            "days_remaining": 5,
            "priority": "high",
            "status": "in_progress",
            "assigned_to": "Safety & Compliance Team",
        },
        {
            "id": 2,
            "title": "Quarterly Queue Performance Report — AERA Submission",
            "category": "Regulatory",
            "deadline": (report_date + timedelta(days=7)).strftime("%Y-%m-%d"),
            "days_remaining": 7,
            "priority": "high",
            "status": "pending",
            "assigned_to": "Operations Analytics",
        },
        {
            "id": 3,
            "title": "Fire Safety Drill — Terminal 2",
            "category": "Internal SOPs",
            "deadline": (report_date + timedelta(days=3)).strftime("%Y-%m-%d"),
            "days_remaining": 3,
            "priority": "high",
            "status": "scheduled",
            "assigned_to": "Fire & Emergency",
        },
        {
            "id": 4,
            "title": "Security Equipment Calibration — All Lanes",
            "category": "Operational",
            "deadline": (report_date + timedelta(days=10)).strftime("%Y-%m-%d"),
            "days_remaining": 10,
            "priority": "medium",
            "status": "pending",
            "assigned_to": "Security Operations",
        },
        {
            "id": 5,
            "title": "Baggage Handling SLA Review with Airlines",
            "category": "Operational",
            "deadline": (report_date + timedelta(days=14)).strftime("%Y-%m-%d"),
            "days_remaining": 14,
            "priority": "medium",
            "status": "pending",
            "assigned_to": "Ground Handling",
        },
        {
            "id": 6,
            "title": "Environmental Compliance — Noise Monitoring Report",
            "category": "Legal",
            "deadline": (report_date + timedelta(days=21)).strftime("%Y-%m-%d"),
            "days_remaining": 21,
            "priority": "low",
            "status": "pending",
            "assigned_to": "Environment & Sustainability",
        },
        {
            "id": 7,
            "title": "Slot Coordination Meeting — Summer Schedule",
            "category": "Regulatory",
            "deadline": (report_date + timedelta(days=2)).strftime("%Y-%m-%d"),
            "days_remaining": 2,
            "priority": "high",
            "status": "confirmed",
            "assigned_to": "Slot Coordination",
        },
        {
            "id": 8,
            "title": "Annual Accessibility Compliance Audit",
            "category": "Legal",
            "deadline": (report_date + timedelta(days=30)).strftime("%Y-%m-%d"),
            "days_remaining": 30,
            "priority": "low",
            "status": "pending",
            "assigned_to": "Facilities Management",
        },
    ]

    tasks.sort(key=lambda t: t["days_remaining"])

    return {"tasks": tasks}
