import streamlit as st


def show_dashboard_page():
    # tab pages for displaying the dashboards
    tab = st.tabs(["Route Dashboard", "Daily Dashboard", "HCP Dashboard"])

    with tab[0]:
        #
        st.subheader("Route Planner Dashboard")

    with tab[1]:
        st.subheader("HCP Data Dashboard")
