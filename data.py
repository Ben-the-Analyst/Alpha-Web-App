import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection


def show_data_page():
    # tab pages for displaying the data
    tab = st.tabs(["Route Plans", "Daily Data", "HCP Data"])

    with tab[0]:
        st.subheader("Filtered Product Data")

        st.title("Read Google Sheet as DataFrame")

        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="RoutePlanner")

        conn = st.connection("gsheets", type=GSheetsConnection)
        # df2 = conn.read(worksheet="Institutions")

        st.dataframe(df)
        # st.dataframe(df2)

    with tab[1]:
        st.subheader("Summary Statistics")

    with tab[2]:
        # bar chart
        st.subheader("Nitrogen Ingredients in Products")
