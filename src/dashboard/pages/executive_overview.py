"""
Executive Overview Page - Top-level KPIs and Executive Summary
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.dashboard.components.kpi_cards import render_kpi_card, render_mini_trendline
from src.dashboard.components.charts import create_time_series_with_target, create_stacked_bar_chart


def render(data_loader, reasoning_engine, filters, config):
    """Render the Executive Overview page"""

    st.title("🏠 Executive Overview")

    # Get report date data
    report_date = filters['report_date']

    # Generate executive summary
    with st.spinner("Generating AI-powered executive summary..."):
        executive_summary = reasoning_engine.generate_executive_summary(report_date)

    # Top row: AI Executive Summary
    st.markdown("## 🤖 AI-Generated Executive Summary")
    st.info(executive_summary)

    st.markdown("---")

    # Key KPIs Row
    st.markdown("## 📊 Key Performance Indicators")

    # Load all data
    pax_data = data_loader.load_passenger_data()
    queue_data = data_loader.load_queue_data()
    security_data = data_loader.load_security_data()
    voc_data = data_loader.load_voc_data()

    # Filter for report date
    daily_pax = pax_data['daily']
    report_pax = daily_pax[daily_pax['date'] == report_date]

    # Calculate total passengers
    total_pax = int(report_pax['pax_count'].sum())
    domestic_pax = int(report_pax[report_pax['passenger_type'] == 'Domestic']['pax_count'].sum())
    intl_pax = int(report_pax[report_pax['passenger_type'] == 'International']['pax_count'].sum())

    # Get 7-day comparison
    if 'pax_count_vs_7day_pct' in report_pax.columns:
        pax_vs_7day = round(report_pax['pax_count_vs_7day_pct'].mean(), 1)
    else:
        pax_vs_7day = 0.0

    # Queue compliance
    zone_compliance = queue_data['zone_compliance']
    report_compliance = zone_compliance[zone_compliance['date'] == report_date]
    avg_compliance = round(report_compliance['actual_compliance_pct'].mean(), 1)
    compliance_delta = round(avg_compliance - 95.0, 1)

    # Security
    security_daily = security_data['daily']
    report_security = security_daily[security_daily['date'] == report_date]
    total_cleared = int(report_security['cleared_volume'].sum())
    avg_reject = round(report_security['reject_rate_pct'].mean(), 1)

    # VOC
    voc_feedback = voc_data['feedback']
    report_voc = voc_feedback[voc_feedback['date'] == report_date]
    total_complaints = int(report_voc['complaints'].sum())
    total_compliments = int(report_voc['compliments'].sum())
    voc_ratio = round(total_compliments / total_complaints, 2) if total_complaints > 0 else 0

    # Display KPIs
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        render_kpi_card(
            title="Total Passengers",
            value=total_pax,
            delta=pax_vs_7day,
            delta_label="vs 7-day avg",
            color="blue"
        )

    with col2:
        render_kpi_card(
            title="Domestic PAX",
            value=domestic_pax,
            suffix="",
            color="green"
        )

    with col3:
        render_kpi_card(
            title="International PAX",
            value=intl_pax,
            suffix="",
            color="orange"
        )

    with col4:
        render_kpi_card(
            title="Queue Compliance",
            value=avg_compliance,
            suffix="%",
            delta=compliance_delta,
            delta_label="vs target",
            color="red" if avg_compliance < 95 else "green"
        )

    with col5:
        render_kpi_card(
            title="VOC Ratio",
            value=voc_ratio,
            suffix=":1",
            color="green" if voc_ratio >= 2 else "red"
        )

    st.markdown("---")

    # Charts Row 1: Passenger Trends
    st.markdown("## 📈 15-Day Passenger & ATM Trends")

    col1, col2 = st.columns(2)

    with col1:
        # Passenger volume trend (last 15 days)
        last_15_days = report_date - timedelta(days=14)
        pax_trend = daily_pax[
            (daily_pax['date'] >= last_15_days) &
            (daily_pax['date'] <= report_date)
        ].groupby('date')['pax_count'].sum().reset_index()

        fig_pax = go.Figure()
        fig_pax.add_trace(go.Scatter(
            x=pax_trend['date'],
            y=pax_trend['pax_count'],
            mode='lines+markers',
            name='Passengers',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.1)'
        ))

        fig_pax.update_layout(
            title="📊 Daily Passenger Volume (15-Day Trend)",
            yaxis_title="Passengers",
            height=350,
            hovermode='x unified'
        )
        st.plotly_chart(fig_pax, use_container_width=True)

    with col2:
        # ATM trend
        atm_data = data_loader.load_atm_data()
        atm_trend = atm_data[
            (atm_data['date'] >= last_15_days) &
            (atm_data['date'] <= report_date)
        ].groupby('date')['atm_count'].sum().reset_index()

        fig_atm = go.Figure()
        fig_atm.add_trace(go.Scatter(
            x=atm_trend['date'],
            y=atm_trend['atm_count'],
            mode='lines+markers',
            name='ATMs',
            line=dict(color='#ff7f0e', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(255, 127, 14, 0.1)'
        ))

        fig_atm.update_layout(
            title="✈️ Daily Aircraft Movements (15-Day Trend)",
            yaxis_title="ATMs",
            height=350,
            hovermode='x unified'
        )
        st.plotly_chart(fig_atm, use_container_width=True)

    st.markdown("---")

    # Charts Row 2: Today's Performance
    st.markdown("## 🎯 Today's Performance Breakdown")

    col1, col2 = st.columns(2)

    with col1:
        # Passenger breakdown by terminal
        terminal_pax = report_pax.groupby(['terminal', 'flow'])['pax_count'].sum().reset_index()

        fig_terminal = create_stacked_bar_chart(
            terminal_pax,
            x_col='terminal',
            y_col='pax_count',
            color_col='flow',
            title="Passengers by Terminal & Flow",
            yaxis_title="Passengers"
        )
        st.plotly_chart(fig_terminal, use_container_width=True)

    with col2:
        # Queue compliance by zone
        zone_summary = report_compliance.groupby('zone')['actual_compliance_pct'].mean().reset_index()
        zone_summary = zone_summary.sort_values('actual_compliance_pct')

        fig_compliance = go.Figure()

        colors = ['green' if x >= 95 else 'orange' if x >= 90 else 'red'
                  for x in zone_summary['actual_compliance_pct']]

        fig_compliance.add_trace(go.Bar(
            y=zone_summary['zone'],
            x=zone_summary['actual_compliance_pct'],
            orientation='h',
            marker_color=colors,
            text=zone_summary['actual_compliance_pct'].round(1),
            texttemplate='%{text}%',
            textposition='outside'
        ))

        fig_compliance.add_vline(x=95, line_dash="dash", line_color="black",
                                annotation_text="Target: 95%")

        fig_compliance.update_layout(
            title="Queue Compliance by Zone",
            xaxis_title="Compliance %",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig_compliance, use_container_width=True)

    # Alerts Section
    st.markdown("---")
    st.markdown("## 🚨 Alerts & Anomalies")

    # Detect zones below target
    below_target = report_compliance[report_compliance['actual_compliance_pct'] < 95]

    if len(below_target) > 0:
        for _, row in below_target.head(3).iterrows():
            st.warning(f"""
**Zone:** {row['zone']} | **Time:** {row['time_window']}
- **Compliance:** {row['actual_compliance_pct']:.1f}% (Target: 95%)
- **Passengers Affected:** {row['pax_total']:,}
- **Variance:** {row['variance_from_target']:.1f}%
            """)
    else:
        st.success("✅ **All zones meeting compliance targets!**")

    # High reject rate security lanes
    high_reject = report_security[report_security['reject_rate_pct'] > 8]
    if len(high_reject) > 0:
        st.warning("**⚠️ High Reject Rate Security Lanes:**")
        for _, lane in high_reject.iterrows():
            st.write(f"- **{lane['lane']}**: {lane['reject_rate_pct']}% reject rate ({lane['reject_count']} rejections)")
