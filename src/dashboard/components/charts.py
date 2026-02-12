"""
Chart components for the dashboard
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
from typing import List, Optional


def create_time_series_with_target(data: pd.DataFrame, x_col: str, y_col: str,
                                    target_value: float = None,
                                    title: str = "", yaxis_title: str = "",
                                    color_col: Optional[str] = None):
    """
    Create a time series line chart with optional target line

    Args:
        data: DataFrame
        x_col: X-axis column (time)
        y_col: Y-axis column (metric)
        target_value: Optional horizontal target line
        title: Chart title
        yaxis_title: Y-axis label
        color_col: Optional column to color by
    """
    fig = go.Figure()

    if color_col and color_col in data.columns:
        # Multiple series
        for group in data[color_col].unique():
            group_data = data[data[color_col] == group]
            fig.add_trace(go.Scatter(
                x=group_data[x_col],
                y=group_data[y_col],
                mode='lines+markers',
                name=str(group),
                line=dict(width=2),
                marker=dict(size=6)
            ))
    else:
        # Single series
        fig.add_trace(go.Scatter(
            x=data[x_col],
            y=data[y_col],
            mode='lines+markers',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8),
            name=yaxis_title or y_col
        ))

    # Add target line
    if target_value is not None:
        fig.add_hline(
            y=target_value,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Target: {target_value}",
            annotation_position="right"
        )

    fig.update_layout(
        title=title,
        xaxis_title="",
        yaxis_title=yaxis_title,
        hovermode='x unified',
        height=400,
        margin=dict(l=50, r=50, t=50, b=50)
    )

    return fig


def create_stacked_bar_chart(data: pd.DataFrame, x_col: str, y_col: str, color_col: str,
                              title: str = "", yaxis_title: str = ""):
    """
    Create a stacked bar chart

    Args:
        data: DataFrame
        x_col: X-axis column (categories)
        y_col: Y-axis column (values)
        color_col: Column to stack by
        title: Chart title
        yaxis_title: Y-axis label
    """
    fig = px.bar(
        data,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title,
        labels={y_col: yaxis_title},
        text_auto=True
    )

    fig.update_layout(
        height=400,
        xaxis_title="",
        hovermode='x unified'
    )

    return fig


def create_heatmap(data: pd.DataFrame, x_col: str, y_col: str, value_col: str,
                   title: str = "", colorscale: str = "RdYlGn"):
    """
    Create a heatmap

    Args:
        data: DataFrame
        x_col: X-axis column
        y_col: Y-axis column
        value_col: Value column for color
        title: Chart title
        colorscale: Plotly colorscale name
    """
    pivot_data = data.pivot(index=y_col, columns=x_col, values=value_col)

    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale=colorscale,
        text=pivot_data.values,
        texttemplate='%{text:.1f}',
        textfont={"size": 10},
        colorbar=dict(title=value_col)
    ))

    fig.update_layout(
        title=title,
        height=400,
        xaxis_title=x_col,
        yaxis_title=y_col
    )

    return fig


def create_comparison_bar(data: pd.DataFrame, category_col: str, value_col: str,
                          title: str = "", orientation: str = 'h',
                          threshold: float = None):
    """
    Create a horizontal or vertical bar chart with optional threshold line

    Args:
        data: DataFrame
        category_col: Category column
        value_col: Value column
        title: Chart title
        orientation: 'h' for horizontal, 'v' for vertical
        threshold: Optional threshold line
    """
    # Sort by value
    data_sorted = data.sort_values(value_col, ascending=(orientation == 'h'))

    # Color by threshold if provided
    if threshold is not None:
        colors = ['green' if v >= threshold else 'red' for v in data_sorted[value_col]]
    else:
        colors = '#1f77b4'

    if orientation == 'h':
        fig = go.Figure(go.Bar(
            y=data_sorted[category_col],
            x=data_sorted[value_col],
            orientation='h',
            marker_color=colors,
            text=data_sorted[value_col],
            texttemplate='%{text:.1f}',
            textposition='outside'
        ))

        if threshold is not None:
            fig.add_vline(x=threshold, line_dash="dash", line_color="black",
                         annotation_text=f"Target: {threshold}")
    else:
        fig = go.Figure(go.Bar(
            x=data_sorted[category_col],
            y=data_sorted[value_col],
            marker_color=colors,
            text=data_sorted[value_col],
            texttemplate='%{text:.1f}',
            textposition='outside'
        ))

        if threshold is not None:
            fig.add_hline(y=threshold, line_dash="dash", line_color="black",
                         annotation_text=f"Target: {threshold}")

    fig.update_layout(
        title=title,
        showlegend=False,
        height=max(400, len(data) * 30) if orientation == 'h' else 400,
        margin=dict(l=150 if orientation == 'h' else 50, r=50, t=50, b=50)
    )

    return fig


def create_dual_axis_chart(data: pd.DataFrame, x_col: str, y1_col: str, y2_col: str,
                           title: str = "", y1_title: str = "", y2_title: str = ""):
    """
    Create a chart with two y-axes

    Args:
        data: DataFrame
        x_col: X-axis column
        y1_col: Left y-axis column
        y2_col: Right y-axis column
        title: Chart title
        y1_title: Left y-axis title
        y2_title: Right y-axis title
    """
    fig = go.Figure()

    # Add first trace (left y-axis)
    fig.add_trace(go.Bar(
        x=data[x_col],
        y=data[y1_col],
        name=y1_title or y1_col,
        marker_color='lightblue',
        yaxis='y'
    ))

    # Add second trace (right y-axis)
    fig.add_trace(go.Scatter(
        x=data[x_col],
        y=data[y2_col],
        name=y2_title or y2_col,
        line=dict(color='red', width=3),
        marker=dict(size=8),
        yaxis='y2'
    ))

    # Update layout with dual y-axes
    fig.update_layout(
        title=title,
        xaxis=dict(title=""),
        yaxis=dict(title=y1_title, side='left'),
        yaxis2=dict(title=y2_title, overlaying='y', side='right'),
        hovermode='x unified',
        height=400,
        legend=dict(x=0.5, y=1.1, orientation='h', xanchor='center')
    )

    return fig
