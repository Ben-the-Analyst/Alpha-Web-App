import streamlit as st
from streamlit_option_menu import option_menu

# Import the page functions
from forms import show_forms_page
from data import show_data_page
from dashboards import show_dashboard_page

# Set Streamlit page configuration
# st.set_page_config(page_title="My App", layout="wide")
st.set_page_config(layout="wide")

# Style to reduce header height
reduce_header_height_style = """
    <style>
        div.block-container {padding-top:1rem;}
    </style>
"""
st.markdown(reduce_header_height_style, unsafe_allow_html=True)

# Custom CSS to style the app and navigation buttons
st.markdown(
    """
    <style>
        .header {
            border-top: 4px solid #8e00c6; 
            padding: 20px 10px 10px 10px;
            margin-bottom: 20px; 
            margin-top: 20px;
            background-color: #f1f1f1;
            border-top-left-radius: 10px; 
            border-top-right-radius: 10px; 
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title of the app
st.markdown('<h1 class="header">Multi-Page Streamlit App</h1>', unsafe_allow_html=True)


# Create the horizontal menu
selected = option_menu(
    None,
    ["Forms", "Data", "Dashboards"],
    icons=["card-checklist", "database", "speedometer2"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "transparent"},
        "icon": {"color": "orange", "font-size": "25px"},
    },
)

# Display the selected page
if selected == "Forms":
    show_forms_page()
elif selected == "Data":
    show_data_page()
elif selected == "Dashboards":
    show_dashboard_page()
