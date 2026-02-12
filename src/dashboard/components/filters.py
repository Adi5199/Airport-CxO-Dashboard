"""
Filter components for the dashboard
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple


def render_global_filters(config: Dict) -> Dict:
    """
    Render global filters that apply across all tabs

    Returns:
        Dictionary of selected filter values
    """
    st.sidebar.title("🔍 Filters")

    # Date selection
    st.sidebar.subheader("Date Range")
    report_date = pd.to_datetime(config['data']['report_date'])

    date_option = st.sidebar.radio(
        "Select Period",
        options=["Report Date (Demo)", "Yesterday", "Last 7 Days", "Last 30 Days", "Custom"],
        index=0
    )

    if date_option == "Report Date (Demo)":
        start_date = report_date
        end_date = report_date
    elif date_option == "Yesterday":
        end_date = report_date - timedelta(days=1)
        start_date = end_date
    elif date_option == "Last 7 Days":
        end_date = report_date
        start_date = end_date - timedelta(days=7)
    elif date_option == "Last 30 Days":
        end_date = report_date
        start_date = end_date - timedelta(days=30)
    else:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input("From", value=report_date - timedelta(days=7))
        with col2:
            end_date = st.date_input("To", value=report_date)

    st.sidebar.markdown("---")

    # Terminal filter
    st.sidebar.subheader("Terminal")
    terminals = st.sidebar.multiselect(
        "Select Terminals",
        options=["All", "T1", "T2"],
        default=["All"]
    )

    if "All" in terminals:
        terminals = ["T1", "T2"]

    # Flow filter
    st.sidebar.subheader("Flow")
    flows = st.sidebar.multiselect(
        "Select Flow",
        options=["All", "Arrival", "Departure"],
        default=["All"]
    )

    if "All" in flows:
        flows = ["Arrival", "Departure"]

    # Passenger type filter
    st.sidebar.subheader("Passenger Type")
    pax_types = st.sidebar.multiselect(
        "Select Type",
        options=["All", "Domestic", "International"],
        default=["All"]
    )

    if "All" in pax_types:
        pax_types = ["Domestic", "International"]

    st.sidebar.markdown("---")

    # Time bucket for aggregations
    st.sidebar.subheader("Comparison Period")
    time_bucket = st.sidebar.selectbox(
        "Compare Against",
        options=["L7D", "L30D", "MTD", "YTD"],
        index=0
    )

    return {
        'start_date': pd.to_datetime(start_date),
        'end_date': pd.to_datetime(end_date),
        'terminals': terminals,
        'flows': flows,
        'pax_types': pax_types,
        'time_bucket': time_bucket,
        'report_date': report_date
    }


def apply_filters(df: pd.DataFrame, filters: Dict, date_col: str = 'date',
                  terminal_col: str = 'terminal', flow_col: str = 'flow',
                  pax_type_col: str = 'passenger_type') -> pd.DataFrame:
    """
    Apply filters to a DataFrame

    Args:
        df: DataFrame to filter
        filters: Dictionary of filter values from render_global_filters()
        date_col: Name of date column
        terminal_col: Name of terminal column
        flow_col: Name of flow column
        pax_type_col: Name of passenger type column

    Returns:
        Filtered DataFrame
    """
    filtered = df.copy()

    # Date filter
    if date_col in filtered.columns:
        filtered[date_col] = pd.to_datetime(filtered[date_col])
        filtered = filtered[
            (filtered[date_col] >= filters['start_date']) &
            (filtered[date_col] <= filters['end_date'])
        ]

    # Terminal filter
    if terminal_col in filtered.columns and filters['terminals']:
        filtered = filtered[filtered[terminal_col].isin(filters['terminals'])]

    # Flow filter
    if flow_col in filtered.columns and filters['flows']:
        filtered = filtered[filtered[flow_col].isin(filters['flows'])]

    # Passenger type filter
    if pax_type_col in filtered.columns and filters['pax_types']:
        filtered = filtered[filtered[pax_type_col].isin(filters['pax_types'])]

    return filtered
