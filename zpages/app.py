import os
import streamlit as st
from pathlib import Path

# Import the page functions
from Aforms.zAllforms import show_forms_page


# Load custom CSS
def load_custom_css():
    with open("assets/css/style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


st.set_page_config(layout="wide")

# Style to reduce header height
reduce_header_height_style = """
    <style>
        div.block-container {padding-top:1rem;}
    </style>
"""
st.markdown(reduce_header_height_style, unsafe_allow_html=True)


st.logo("assets/images/logo.png")
# Add a spinner while loading forms
with st.spinner("Loading..."):
    show_forms_page()
# show_forms_page()
