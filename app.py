# app.py

import streamlit as st
from authentication import authenticated

# st.set_page_config(page_title="My App", layout="centered")s

st.title("My Multi-Page Streamlit App")

# Navigation Menu
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Page 1", "Page 2"])

# Import and load each page based on selection
if page == "Page 1":
    from ret import page1

    page1.app()
elif page == "Page 2":
    from ret import page2

    page2.app()
