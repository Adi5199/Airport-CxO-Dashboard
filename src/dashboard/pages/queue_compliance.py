"""
Queue Compliance Performance Page - Detailed analysis of queue times across all zones
This is the KEY PAGE for the DEMO SCENARIO
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.dashboard.components.kpi_cards import render_compliance_gauge
from src.dashboard.components.charts import create_time_series_with_target


def render(data_loader, reasoning_engine, filters, config):
    """Render the Queue Compliance page"""

    st.title("⏱️ Queue Time Compliance Performance")
    st.markdown("**Live Monitoring & AI-Powered Root Cause Analysis**")

    report_date = filters['report_date']

    # Load queue data
    queue_data = data_loader.load_queue_data()
    zone_compliance = queue_data['zone_compliance']
    hourly_compliance = queue_data['hourly_compliance']

    # Filter for report date
    report_zones = zone_compliance[zone_compliance['date'] == report_date]
    report_hourly = hourly_compliance[hourly_compliance['date'] == report_date]

    # Top Section: Overall Compliance Status
    st.markdown("## 🎯 Overall Compliance Status")

    col1, col2, col3, col4 = st.columns(4)

    # Calculate stats
    overall_compliance = round(report_zones['actual_compliance_pct'].mean(), 1)
    zones_below_target = len(report_zones[report_zones['actual_compliance_pct'] < 95])
    total_zones = report_zones['zone'].nunique()
    pax_affected = int(report_zones[report_zones['actual_compliance_pct'] < 95]['pax_total'].sum())

    with col1:
        st.metric("Overall Compliance", f"{overall_compliance}%", delta=f"{overall_compliance - 95:.1f}% vs target")

    with col2:
        st.metric("Zones Below Target", f"{zones_below_target}/{total_zones}",
                 delta=None if zones_below_target == 0 else "Action Required", delta_color="inverse")

    with col3:
        st.metric("Passengers Affected", f"{pax_affected:,}",
                 delta=None)

    with col4:
        target_met_pct = ((total_zones - zones_below_target) / total_zones * 100) if total_zones > 0 else 100
        st.metric("Target Achievement", f"{target_met_pct:.0f}%")

    st.markdown("---")

    # AI Insights Section - DEMO HIGHLIGHT
    st.markdown("## 🤖 AI-Powered Root Cause Analysis")

    st.info("""
**💡 Demo Scenario Active:** Analyzing queue compliance drop on January 24, 2026

Click "Analyze Root Cause" to trigger AI-powered drill-down analysis identifying:
- Worst performing zones and time windows
- Contributing factors (passenger spikes, security lane issues, airline concentration)
- Actionable recommendations for immediate deployment
    """)

    if st.button("🔍 Analyze Root Cause", type="primary", use_container_width=True):
        with st.spinner("AI analyzing operational data across all dimensions..."):
            # Generate comprehensive root cause analysis
            root_cause = reasoning_engine.generate_root_cause_analysis(
                date=report_date,
                zone="Check-in 34-86",  # Known issue zone from demo
                time_window="1400-1600"
            )

            st.markdown("### 📊 Root Cause Analysis Results")

            # Display analysis
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Primary Issue:** {root_cause['primary_issue']}")

                st.markdown("**Contributing Factors:**")
                for i, factor in enumerate(root_cause['factors'], 1):
                    st.markdown(f"{i}. {factor}")

                st.markdown(f"**Impact:** {root_cause['impact']}")

                st.markdown(f"**Severity:** `{root_cause['severity']}`")

            with col2:
                # Severity indicator
                severity_color = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}[root_cause['severity']]
                st.markdown(f"""
<div style='background-color: {severity_color}; color: white; padding: 1rem; border-radius: 0.5rem; text-align: center;'>
    <h3>SEVERITY</h3>
    <h1>{root_cause['severity']}</h1>
</div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("### 💡 Recommended Actions (Deploy Today)")

            for i, action in enumerate(root_cause['recommendations'], 1):
                st.success(f"**{i}.** {action}")

    st.markdown("---")

    # Zone-by-Zone Analysis
    st.markdown("## 📍 Zone-by-Zone Performance")

    # Zone selector
    zones = report_zones['zone'].unique()
    selected_zone = st.selectbox("Select Zone for Detailed Analysis", zones, index=3)  # Default to Check-in 34-86

    # Filter for selected zone
    zone_data = report_zones[report_zones['zone'] == selected_zone]

    col1, col2 = st.columns([1, 2])

    with col1:
        # Compliance gauge for the zone
        avg_zone_compliance = zone_data['actual_compliance_pct'].mean()
        render_compliance_gauge(
            value=avg_zone_compliance,
            target=95.0,
            title=f"{selected_zone} Compliance"
        )

        # Zone stats
        st.metric("Threshold (Minutes)", zone_data.iloc[0]['threshold_minutes'])
        st.metric("Total Passengers", f"{int(zone_data['pax_total'].sum()):,}")
        st.metric("Avg Wait Time", f"{zone_data['avg_wait_time_min'].mean():.1f} min")

    with col2:
        # Time-windowed performance
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=zone_data['time_window'],
            y=zone_data['actual_compliance_pct'],
            mode='lines+markers',
            name='Actual',
            line=dict(color='blue', width=3),
            marker=dict(size=10),
            text=zone_data['actual_compliance_pct'].round(1),
            texttemplate='%{text}%',
            textposition='top center'
        ))

        fig.add_hline(y=95, line_dash="dash", line_color="red",
                     annotation_text="Target: 95%", annotation_position="right")

        # Highlight violations
        violations = zone_data[zone_data['actual_compliance_pct'] < 95]
        if len(violations) > 0:
            fig.add_trace(go.Scatter(
                x=violations['time_window'],
                y=violations['actual_compliance_pct'],
                mode='markers',
                name='Below Target',
                marker=dict(color='red', size=15, symbol='x'),
                showlegend=False
            ))

        fig.update_layout(
            title=f"{selected_zone} - Compliance by Time Window",
            yaxis_title="Compliance %",
            xaxis_title="Time Window",
            height=400,
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # All Zones Heatmap
    st.markdown("## 🗺️ Compliance Heatmap - All Zones")

    # Pivot data for heatmap
    heatmap_data = report_zones.pivot_table(
        index='zone',
        columns='time_window',
        values='actual_compliance_pct',
        aggfunc='mean'
    )

    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='RdYlGn',
        zmid=95,
        text=heatmap_data.values.round(1),
        texttemplate='%{text}%',
        textfont={"size": 10},
        colorbar=dict(title="Compliance %")
    ))

    fig_heatmap.update_layout(
        title="Queue Compliance Heatmap (All Zones × Time Windows)",
        height=500,
        xaxis_title="Time Window",
        yaxis_title="Zone"
    ))

    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.markdown("---")

    # Detailed Table
    st.markdown("## 📋 Detailed Compliance Data")

    # Add filters
    col1, col2 = st.columns(2)
    with col1:
        terminal_filter = st.multiselect("Filter by Terminal", options=report_zones['terminal'].unique(),
                                        default=report_zones['terminal'].unique())
    with col2:
        show_only_violations = st.checkbox("Show only violations (< 95%)", value=False)

    # Filter table
    filtered_zones = report_zones[report_zones['terminal'].isin(terminal_filter)]
    if show_only_violations:
        filtered_zones = filtered_zones[filtered_zones['actual_compliance_pct'] < 95]

    # Display table
    display_cols = ['zone', 'time_window', 'actual_compliance_pct', 'target_compliance_pct',
                   'variance_from_target', 'pax_total', 'avg_wait_time_min']

    st.dataframe(
        filtered_zones[display_cols].sort_values('actual_compliance_pct'),
        use_container_width=True,
        height=400
    )

    # Export option
    csv = filtered_zones.to_csv(index=False)
    st.download_button(
        label="📥 Download Compliance Data (CSV)",
        data=csv,
        file_name=f"queue_compliance_{report_date.strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
