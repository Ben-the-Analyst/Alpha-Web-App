import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection


def show_forms_page():
    # Main panel for displaying the table, summary, and plots
    tab = st.tabs(["Route Planner Form", "Daily Reporting Form", "HCP Form"])

    with tab[0]:
        # route planner form
        st.markdown("This is the Route Planner Form")
        st.subheader("All The Fields are Required")

    with tab[1]:
        # daily report form
        st.markdown("This is the Daily Reporting Form")
        st.subheader("All The Fields are Required")

    with tab[2]:
        # hcp form
        st.markdown("This is the HCP Form")
        st.subheader("All The Fields are Required")
