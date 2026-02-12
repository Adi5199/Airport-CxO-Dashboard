"""
Trends & Analytics Page - Historical trends, biometric adoption, VOC analysis
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
from pathlib import Path
from datetime import timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


def render(data_loader, reasoning_engine, filters, config):
    """Render Trends & Analytics page"""

    st.title("📈 Trends & Analytics")

    report_date = filters['report_date']

    # Load data
    pax_data = data_loader.load_passenger_data()
    biometric_data = data_loader.load_biometric_data()
    voc_data = data_loader.load_voc_data()

    # Date range for trends
    last_30_days = report_date - timedelta(days=30)

    # Passenger Trends Section
    st.markdown("## 📊 Passenger Volume Trends")

    daily_pax = pax_data['daily']
    trend_pax = daily_pax[
        (daily_pax['date'] >= last_30_days) &
        (daily_pax['date'] <= report_date)
    ]

    # By passenger type
    pax_by_type = trend_pax.groupby(['date', 'passenger_type'])['pax_count'].sum().reset_index()

    fig_pax_type = px.area(
        pax_by_type,
        x='date',
        y='pax_count',
        color='passenger_type',
        title="Daily Passenger Volumes - Domestic vs International (Last 30 Days)",
        labels={'pax_count': 'Passengers', 'date': 'Date'},
        color_discrete_map={'Domestic': '#1f77b4', 'International': '#ff7f0e'}
    )
    fig_pax_type.update_layout(height=400, hovermode='x unified')
    st.plotly_chart(fig_pax_type, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # By terminal
        pax_by_terminal = trend_pax.groupby(['date', 'terminal'])['pax_count'].sum().reset_index()

        fig_terminal = px.line(
            pax_by_terminal,
            x='date',
            y='pax_count',
            color='terminal',
            title="Passengers by Terminal",
            markers=True
        )
        fig_terminal.update_layout(height=350)
        st.plotly_chart(fig_terminal, use_container_width=True)

    with col2:
        # By flow
        pax_by_flow = trend_pax.groupby(['date', 'flow'])['pax_count'].sum().reset_index()

        fig_flow = px.line(
            pax_by_flow,
            x='date',
            y='pax_count',
            color='flow',
            title="Arrivals vs Departures",
            markers=True
        )
        fig_flow.update_layout(height=350)
        st.plotly_chart(fig_flow, use_container_width=True)

    st.markdown("---")

    # Biometric Adoption Trends
    st.markdown("## 🔐 Biometric Adoption & Digital Transformation")

    trend_biometric = biometric_data[
        (biometric_data['date'] >= last_30_days) &
        (biometric_data['date'] <= report_date)
    ]

    # Daily adoption by terminal
    adoption_daily = trend_biometric.groupby(['date', 'terminal']).agg({
        'total_eligible_pax': 'sum',
        'biometric_registrations': 'sum',
        'successful_boardings': 'sum'
    }).reset_index()

    adoption_daily['adoption_pct'] = (
        adoption_daily['biometric_registrations'] / adoption_daily['total_eligible_pax'] * 100
    ).round(2)

    adoption_daily['success_rate'] = (
        adoption_daily['successful_boardings'] / adoption_daily['biometric_registrations'] * 100
    ).round(2)

    col1, col2 = st.columns(2)

    with col1:
        # Adoption rate trend
        fig_adoption = px.line(
            adoption_daily,
            x='date',
            y='adoption_pct',
            color='terminal',
            title="Biometric Adoption Rate Trend (%)",
            markers=True
        )

        fig_adoption.add_hline(y=60, line_dash="dash", annotation_text="Target: 60%",
                              line_color="green")

        fig_adoption.update_layout(height=350, yaxis_title="Adoption %")
        st.plotly_chart(fig_adoption, use_container_width=True)

    with col2:
        # Success rate trend
        fig_success = px.line(
            adoption_daily,
            x='date',
            y='success_rate',
            color='terminal',
            title="Biometric Success Rate (%)",
            markers=True
        )
        fig_success.update_layout(height=350, yaxis_title="Success %")
        st.plotly_chart(fig_success, use_container_width=True)

    # Channel breakdown
    st.markdown("### Adoption by Channel")

    latest_date_biometric = trend_biometric[trend_biometric['date'] == report_date]
    channel_summary = latest_date_biometric.groupby('channel')['biometric_registrations'].sum().reset_index()

    fig_channel = go.Figure(data=[go.Pie(
        labels=channel_summary['channel'],
        values=channel_summary['biometric_registrations'],
        hole=.4,
        textinfo='label+percent'
    )])
    fig_channel.update_layout(title="Biometric Registrations by Channel (Today)", height=350)
    st.plotly_chart(fig_channel, use_container_width=True)

    st.markdown("---")

    # Voice of Customer Trends
    st.markdown("## 💬 Voice of Customer Analysis")

    voc_feedback = voc_data['feedback']
    trend_voc = voc_feedback[
        (voc_feedback['date'] >= last_30_days) &
        (voc_feedback['date'] <= report_date)
    ]

    # Daily feedback trend
    voc_daily = trend_voc.groupby('date').agg({
        'complaints': 'sum',
        'compliments': 'sum'
    }).reset_index()

    voc_daily['ratio'] = (voc_daily['compliments'] / voc_daily['complaints'].replace(0, 1)).round(2)

    fig_voc = go.Figure()

    fig_voc.add_trace(go.Bar(
        x=voc_daily['date'],
        y=voc_daily['complaints'],
        name='Complaints',
        marker_color='#d62728'
    ))

    fig_voc.add_trace(go.Bar(
        x=voc_daily['date'],
        y=voc_daily['compliments'],
        name='Compliments',
        marker_color='#2ca02c'
    ))

    fig_voc.update_layout(
        title="Daily Complaints vs Compliments",
        yaxis_title="Count",
        height=400,
        barmode='group',
        hovermode='x unified'
    )
    st.plotly_chart(fig_voc, use_container_width=True)

    # Ratio trend
    fig_ratio = go.Figure()

    fig_ratio.add_trace(go.Scatter(
        x=voc_daily['date'],
        y=voc_daily['ratio'],
        mode='lines+markers',
        name='Compliments:Complaints Ratio',
        line=dict(color='blue', width=3),
        marker=dict(size=8)
    ))

    fig_ratio.add_hline(y=2.0, line_dash="dash", annotation_text="Target: 2:1",
                       line_color="green")

    fig_ratio.update_layout(
        title="Compliments to Complaints Ratio Trend",
        yaxis_title="Ratio",
        height=350,
        hovermode='x unified'
    )
    st.plotly_chart(fig_ratio, use_container_width=True)

    # Feedback by terminal and media
    col1, col2 = st.columns(2)

    with col1:
        # By terminal
        terminal_voc = trend_voc.groupby('terminal').agg({
            'complaints': 'sum',
            'compliments': 'sum'
        }).reset_index()

        terminal_voc['ratio'] = (terminal_voc['compliments'] / terminal_voc['complaints']).round(2)

        fig_terminal_voc = go.Figure(data=[
            go.Bar(name='Complaints', x=terminal_voc['terminal'], y=terminal_voc['complaints'], marker_color='red'),
            go.Bar(name='Compliments', x=terminal_voc['terminal'], y=terminal_voc['compliments'], marker_color='green')
        ])

        fig_terminal_voc.update_layout(
            title="Feedback by Terminal (30-Day Total)",
            barmode='group',
            height=350
        )
        st.plotly_chart(fig_terminal_voc, use_container_width=True)

    with col2:
        # By media type
        media_voc = trend_voc.groupby('media_type')['total_feedback'].sum().reset_index()
        media_voc = media_voc.sort_values('total_feedback', ascending=False)

        fig_media = px.bar(
            media_voc,
            x='media_type',
            y='total_feedback',
            title="Feedback by Channel",
            color='total_feedback',
            color_continuous_scale='Blues'
        )
        fig_media.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_media, use_container_width=True)

    # Recent negative feedback
    st.markdown("### 📝 Recent Customer Feedback")

    voc_messages = voc_data['messages']
    recent_messages = voc_messages[voc_messages['date'] == report_date].head(10)

    tab1, tab2 = st.tabs(["Negative Feedback", "Positive Feedback"])

    with tab1:
        negative = recent_messages[recent_messages['sentiment'] == 'negative']
        for _, msg in negative.iterrows():
            st.warning(f"**{msg['terminal']} - {msg['department']}** ({msg['media']}): {msg['message']}")

    with tab2:
        positive = recent_messages[recent_messages['sentiment'] == 'positive']
        for _, msg in positive.iterrows():
            st.success(f"**{msg['terminal']} - {msg['department']}** ({msg['media']}): {msg['message']}")
