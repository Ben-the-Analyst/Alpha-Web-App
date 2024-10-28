import streamlit as st


def show_dashboard_page():
    # tab pages for displaying the dashboards
    tab = st.tabs(["Route Dashboard", "Daily Dashboard", "HCP Dashboard"])

    with tab[0]:
        #
        st.subheader("Route Planner Dashboard")
        st.subheader("Filtered Product Data")

    with tab[1]:
        #
        st.subheader("Daily Report Dashboard")
        st.subheader("Summary Statistics")

    with tab[2]:
        #
        st.subheader("HCP Data Dashboard")
