"""
KPI Card components for the dashboard
"""
import streamlit as st
import plotly.graph_objects as go
from typing import Optional


def render_kpi_card(title: str, value: any, delta: Optional[float] = None,
                    delta_label: str = "vs 7-day avg", suffix: str = "",
                    color: str = "blue", show_trend: bool = True):
    """
    Render a KPI card with value and trend

    Args:
        title: KPI title
        value: Main KPI value
        delta: Change percentage (positive or negative)
        delta_label: Label for delta
        suffix: Suffix for value (e.g., "%", "k", "M")
        color: Card accent color
        show_trend: Whether to show trend indicator
    """
    # Determine delta color
    if delta is not None:
        if delta > 0:
            delta_color = "inverse" if "lower" in delta_label.lower() else "normal"
        else:
            delta_color = "normal" if "lower" in delta_label.lower() else "inverse"
    else:
        delta_color = "off"

    # Format value
    if isinstance(value, (int, float)):
        if abs(value) >= 1000:
            display_value = f"{value/1000:.1f}k"
        else:
            display_value = f"{value:,.0f}" if isinstance(value, int) else f"{value:.2f}"
    else:
        display_value = str(value)

    display_value += suffix

    # Display
    st.metric(
        label=title,
        value=display_value,
        delta=f"{delta:+.1f}% {delta_label}" if delta is not None else None,
        delta_color=delta_color
    )


def render_compliance_gauge(value: float, target: float = 95.0, title: str = "Compliance"):
    """
    Render a gauge chart for compliance metrics

    Args:
        value: Actual compliance percentage
        target: Target compliance percentage
        title: Chart title
    """
    # Determine color
    if value >= target:
        color = "green"
    elif value >= target - 3:
        color = "yellow"
    else:
        color = "red"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16}},
        delta={'reference': target, 'suffix': '%'},
        gauge={
            'axis': {'range': [None, 100], 'ticksuffix': '%'},
            'bar': {'color': color},
            'steps': [
                {'range': [0, target - 10], 'color': "lightgray"},
                {'range': [target - 10, target], 'color': "lightblue"},
                {'range': [target, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': target
            }
        }
    ))

    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))

    st.plotly_chart(fig, use_container_width=True)


def render_mini_trendline(data, x_col: str, y_col: str, title: str = "", height: int = 100):
    """
    Render a small trendline sparkline

    Args:
        data: DataFrame with trend data
        x_col: X-axis column
        y_col: Y-axis column
        title: Chart title
        height: Chart height
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data[x_col],
        y=data[y_col],
        mode='lines',
        line=dict(color='#1f77b4', width=2),
        fill='tozeroy',
        fillcolor='rgba(31, 119, 180, 0.2)'
    ))

    fig.update_layout(
        title=title,
        showlegend=False,
        height=height,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
    )

    st.plotly_chart(fig, use_container_width=True)
