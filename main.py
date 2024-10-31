import streamlit as st
import time
from streamlit_option_menu import option_menu



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


st.logo("assets/images/logo.png", size="large")

# Sidebar menu
with st.sidebar:
    selected = option_menu(
        None,
        ["Home", "Reports"],
        icons=["house", "clipboard-data"],
        # menu_icon="cast",
        # orientation="horizontal",
        default_index=0,
    )

    # Footer container
    st.container(key="footer_container")
    st.button(
        "Logout",
        key="logout_button",
        icon=":material/exit_to_app:",
        use_container_width=True,
    )
    st.sidebar.markdown("---")  # Add a horizontal line for separation
    # st.sidebar.markdown("### Alpha +")
    # st.sidebar.markdown("This is a footer section.")
    st.sidebar.markdown("© 2024   Alpha +")  # Copyright or additional information

# Simulate data loading
with st.spinner("Data is loading..."):
    time.sleep(2)  # Reduced sleep time for faster loading

# Page content based on selection
if selected == "Home":
    # Add a spinner while loading forms
    with st.spinner("Loading..."):
        show_forms_page()
    # show_forms_page()


elif selected == "Reports":
    with st.spinner("Loading..."):
        st.title("Reports")
        st.markdown(
            "This is the **Dashboard** page, where you can adjust your preferences."
        )
