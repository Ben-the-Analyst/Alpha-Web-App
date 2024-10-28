import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection


def show_data_page():
    # tab pages for displaying the data
    tab = st.tabs(["Route Plans", "Daily Data", "HCP Data"])

    with tab[0]:
        # st.subheader("Filtered Product Data")

        # st.title("Read Google Sheet as DataFrame")

        conn = st.connection("gsheets", type=GSheetsConnection)
        Route_data = conn.read(worksheet="RoutePlanner")

        st.dataframe(Route_data)

    with tab[1]:

        conn = st.connection("gsheets", type=GSheetsConnection)
        Daily_data = conn.read(worksheet="DailyData")
        st.dataframe(Daily_data)

    with tab[2]:
        # bar chart
        st.title("HCP Data")
