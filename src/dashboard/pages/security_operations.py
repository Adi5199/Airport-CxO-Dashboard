"""
Security & Operations Page - Security lanes, baggage, gates
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.dashboard.components.charts import create_comparison_bar


def render(data_loader, reasoning_engine, filters, config):
    """Render Security & Operations page"""

    st.title("🔒 Security & Operations")

    report_date = filters['report_date']

    # Load data
    security_data = data_loader.load_security_data()
    baggage_data = data_loader.load_baggage_data()
    gate_data = data_loader.load_gate_data()

    # Security Lanes Section
    st.markdown("## 🛡️ Security Lane Performance")

    security_daily = security_data['daily']
    report_security = security_daily[security_daily['date'] == report_date]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Cleared", f"{int(report_security['cleared_volume'].sum()):,}")
    with col2:
        st.metric("Avg Reject Rate", f"{report_security['reject_rate_pct'].mean():.1f}%")
    with col3:
        high_reject = len(report_security[report_security['reject_rate_pct'] > 8])
        st.metric("High Reject Lanes", high_reject, delta="Needs Attention" if high_reject > 0 else None)

    # Lane performance chart
    col1, col2 = st.columns(2)

    with col1:
        # Cleared volume by lane
        sorted_cleared = report_security.sort_values('cleared_volume', ascending=True)

        fig_cleared = create_comparison_bar(
            sorted_cleared,
            category_col='lane',
            value_col='cleared_volume',
            title="Cleared Volume by Lane",
            orientation='h'
        )
        st.plotly_chart(fig_cleared, use_container_width=True)

    with col2:
        # Reject rate by lane
        sorted_reject = report_security.sort_values('reject_rate_pct', ascending=True)

        fig_reject = create_comparison_bar(
            sorted_reject,
            category_col='lane',
            value_col='reject_rate_pct',
            title="Reject Rate by Lane (%)",
            orientation='h',
            threshold=8.0
        )
        st.plotly_chart(fig_reject, use_container_width=True)

    # High reject lanes alert
    high_reject_lanes = report_security[report_security['reject_rate_pct'] > 8]
    if len(high_reject_lanes) > 0:
        st.warning("**⚠️ Lanes with High Reject Rates (>8%):**")
        for _, lane in high_reject_lanes.iterrows():
            st.write(f"- **{lane['lane']}** ({lane['terminal']}): {lane['reject_rate_pct']}% | {lane['reject_count']} rejections | {lane['cleared_volume']:,} cleared")

    st.markdown("---")

    # Baggage Reclaim Section
    st.markdown("## 🧳 Baggage Reclaim Utilization")

    report_baggage = baggage_data[baggage_data['date'] == report_date]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Flights", int(report_baggage['flights'].sum()))
    with col2:
        st.metric("Total PAX", f"{int(report_baggage['pax'].sum()):,}")
    with col3:
        st.metric("Avg PAX/Flight", f"{report_baggage['pax_per_flight'].mean():.0f}")

    # Belt utilization
    fig_belts = go.Figure()

    for belt_type in ['Domestic', 'International']:
        belt_data = report_baggage[report_baggage['belt_type'] == belt_type]

        fig_belts.add_trace(go.Bar(
            x=belt_data['belt'],
            y=belt_data['utilization_pct'],
            name=belt_type,
            text=belt_data['utilization_pct'].round(1),
            texttemplate='%{text}%',
            textposition='outside'
        ))

    fig_belts.add_hline(y=85, line_dash="dash", annotation_text="Optimal: 85%")

    fig_belts.update_layout(
        title="Baggage Belt Utilization",
        yaxis_title="Utilization %",
        height=400,
        barmode='group'
    )
    st.plotly_chart(fig_belts, use_container_width=True)

    st.markdown("---")

    # Gate & Boarding Mode Section
    st.markdown("## 🚪 Gate Utilization & Boarding Mode")

    report_gates = gate_data[gate_data['date'] == report_date]

    # Boarding mode mix
    boarding_mix = report_gates.groupby(['terminal', 'boarding_mode']).agg({
        'flights': 'sum',
        'pax': 'sum'
    }).reset_index()

    # Calculate percentages
    for terminal in ['T1', 'T2']:
        terminal_total = boarding_mix[boarding_mix['terminal'] == terminal]['pax'].sum()
        boarding_mix.loc[boarding_mix['terminal'] == terminal, 'pax_pct'] = \
            (boarding_mix.loc[boarding_mix['terminal'] == terminal, 'pax'] / terminal_total * 100).round(1)

    col1, col2 = st.columns(2)

    with col1:
        # T1 boarding mode
        t1_mix = boarding_mix[boarding_mix['terminal'] == 'T1']

        fig_t1 = go.Figure(data=[go.Pie(
            labels=t1_mix['boarding_mode'],
            values=t1_mix['pax'],
            hole=.4,
            textinfo='label+percent'
        )])
        fig_t1.update_layout(title="T1 Boarding Mode Mix", height=350)
        st.plotly_chart(fig_t1, use_container_width=True)

    with col2:
        # T2 boarding mode
        t2_mix = boarding_mix[boarding_mix['terminal'] == 'T2']

        fig_t2 = go.Figure(data=[go.Pie(
            labels=t2_mix['boarding_mode'],
            values=t2_mix['pax'],
            hole=.4,
            textinfo='label+percent'
        )])
        fig_t2.update_layout(title="T2 Boarding Mode Mix", height=350)
        st.plotly_chart(fig_t2, use_container_width=True)

    # Alert for high bus boarding
    t2_bus_pct = t2_mix[t2_mix['boarding_mode'] == 'Bus']['pax_pct'].values
    if len(t2_bus_pct) > 0 and t2_bus_pct[0] > 40:
        st.warning(f"⚠️ **High bus boarding at T2:** {t2_bus_pct[0]:.1f}% - May cause delays in passenger arrival at security")

    # Gate utilization table
    st.markdown("### Gate-Level Utilization")
    st.dataframe(
        report_gates[['gate', 'terminal', 'boarding_mode', 'flights', 'pax', 'pax_per_flight']].sort_values('pax', ascending=False),
        use_container_width=True,
        height=300
    )
