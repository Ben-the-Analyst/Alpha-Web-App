# filter_modal.py
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd


# Function to define and display the modal with filters
def filter_modal():
    # Initialize filter settings if they don't exist
    if "filter_settings" not in st.session_state:
        st.session_state.filter_settings = {
            "newest_first": True,
            "oldest_first": False,
            "current_week": True,
            "current_month": False,
            "next_month": False,
            "last_month": False,
            "last_two_months": False,
        }

    # Create a form for the filters
    with st.form("filter_form"):
        st.write("### Sort By")

        # Sorting logic with mutual exclusivity
        col1, col2 = st.columns(2, gap="small")
        with col1:
            newest_first = st.checkbox(
                "Newest to oldest",
                value=st.session_state.filter_settings["newest_first"],
                key="temp_newest_first",
            )
        with col2:
            oldest_first = st.checkbox(
                "Oldest to newest",
                value=st.session_state.filter_settings["oldest_first"],
                key="temp_oldest_first",
            )

        # Define 3 columns for Current, Upcoming, and Past filters
        st.divider()
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("### Current")
            current_week = st.checkbox(
                "Current Week",
                value=st.session_state.filter_settings["current_week"],
                key="temp_current_week",
            )
            current_month = st.checkbox(
                "Current Month",
                value=st.session_state.filter_settings["current_month"],
                key="temp_current_month",
            )

        with col2:
            st.write("### Upcoming")
            next_month = st.checkbox(
                "Next Month",
                value=st.session_state.filter_settings["next_month"],
                key="temp_next_month",
            )

        with col3:
            st.write("### Past")
            last_month = st.checkbox(
                "Last Month",
                value=st.session_state.filter_settings["last_month"],
                key="temp_last_month",
            )
            last_two_months = st.checkbox(
                "Last 2 Months",
                value=st.session_state.filter_settings["last_two_months"],
                key="temp_last_two_months",
            )

        st.divider()
        col1, col2, col3 = st.columns(3)
        with col2:
            # Apply Filters button
            submitted = st.form_submit_button("Apply Filters")

        if submitted:
            # Ensure mutual exclusivity for sorting after form submission
            if newest_first and oldest_first:
                oldest_first = False

            # Update filter settings based on form values
            st.session_state.filter_settings.update(
                {
                    "newest_first": newest_first,
                    "oldest_first": oldest_first,
                    "current_week": current_week,
                    "current_month": current_month,
                    "next_month": next_month,
                    "last_month": last_month,
                    "last_two_months": last_two_months,
                }
            )
            st.success("Filters applied successfully!")
            return st.session_state.filter_settings

    return st.session_state.filter_settings


# Get the filtered data based on selected filters
def get_filtered_data(data, filters):
    """Filter data based on selected filters"""
    filtered_data = data.copy()

    # Get current date and time
    today = pd.Timestamp.now()

    # Calculate relevant dates
    current_week_start = today - pd.Timedelta(days=today.dayofweek)
    current_week_end = current_week_start + pd.Timedelta(days=6)

    current_month_start = today.replace(day=1)
    current_month_end = (current_month_start + pd.Timedelta(days=32)).replace(
        day=1
    ) - pd.Timedelta(days=1)

    next_month_start = (current_month_start + pd.Timedelta(days=32)).replace(day=1)
    next_month_end = (next_month_start + pd.Timedelta(days=32)).replace(
        day=1
    ) - pd.Timedelta(days=1)

    last_month_start = (current_month_start - pd.Timedelta(days=1)).replace(day=1)
    last_month_end = current_month_start - pd.Timedelta(days=1)

    last_two_months_start = (last_month_start - pd.Timedelta(days=32)).replace(day=1)

    # Convert the Date column to datetime if it isn't already
    filtered_data["Date"] = pd.to_datetime(filtered_data["Date"])

    # Apply date filters based on selection
    if filters.get("current_week"):
        filtered_data = filtered_data[
            (filtered_data["Date"] >= current_week_start)
            & (filtered_data["Date"] <= current_week_end)
        ]
    elif filters.get("current_month"):
        filtered_data = filtered_data[
            (filtered_data["Date"] >= current_month_start)
            & (filtered_data["Date"] <= current_month_end)
        ]
    elif filters.get("next_month"):
        filtered_data = filtered_data[
            (filtered_data["Date"] >= next_month_start)
            & (filtered_data["Date"] <= next_month_end)
        ]
    elif filters.get("last_month"):
        filtered_data = filtered_data[
            (filtered_data["Date"] >= last_month_start)
            & (filtered_data["Date"] <= last_month_end)
        ]
    elif filters.get("last_two_months"):
        filtered_data = filtered_data[
            (filtered_data["Date"] >= last_two_months_start)
            & (filtered_data["Date"] <= last_month_end)
        ]

    # Apply sorting
    if filters.get("newest_first"):
        filtered_data = filtered_data.sort_values("Date", ascending=False)
    elif filters.get("oldest_first"):
        filtered_data = filtered_data.sort_values("Date", ascending=True)

    return filtered_data
