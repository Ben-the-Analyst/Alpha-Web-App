# filter_modal.py
import streamlit as st
from datetime import datetime, timedelta


# Function to define and display the modal with filters
def filter_modal():
    st.write("### Filter Options")
    st.write("Use the filters below to narrow down data.")

    # Define 3 columns for Current, Upcoming, and Past filters
    col1, col2, col3 = st.columns(3)

    # Calculate date ranges
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())  # Start of the current week
    start_of_month = today.replace(day=1)  # Start of the current month
    next_month = (start_of_month + timedelta(days=31)).replace(
        day=1
    )  # Start of next month
    last_month = (start_of_month - timedelta(days=1)).replace(
        day=1
    )  # Start of last monthpip
    last_two_months = (last_month - timedelta(days=last_month.day)).replace(
        day=1
    )  # Start of two months ago

    with col1:
        st.write("### Current")
        st.checkbox("Current Week", key="current_week")
        st.checkbox("Current Month", key="current_month")

    with col2:
        st.write("### Upcoming")
        st.checkbox("Next Month", key="next_month")

    with col3:
        st.write("### Past")
        st.checkbox("Last Month", key="last_month")
        st.checkbox("Last 2 Months", key="last_two_months")

    # Add any additional filtering logic here if needed
