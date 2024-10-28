import streamlit as st
import base64
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

LOGO_IMAGE = "logo.png"

# Custom CSS to style the app and navigation buttons
st.markdown(
    """
    <style>
        .container {
            display: flex;
            border-top: 4px solid #8e00c6; 
            border-bottom: 1px solid #d8d8d8;
            # padding: 20px 10px 10px 10px;
            margin-bottom: 20px; 
            margin-top: 20px;
            # background-color: #faf4fc; 
            border-top-left-radius: 10px; 
            border-top-right-radius: 10px;
            text-align: center !important;  
            justify-content: center !important;
            align-items: center !important;
        }
        
        .logo-text {
            font-weight: 700 !important;
            font-size: 30px !important;
            color: #f9a01b !important;
            padding-top: 10px !important;
            line-height: 40px !important;
        }
        
        .logo-img {
            float: right;
            margin-right: 10px;
            width: 40px !important;
            height: 40px !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    f"""
    <div class="container">
        <img class="logo-img" src="data:image/png;base64,{base64.b64encode(open(LOGO_IMAGE, "rb").read()).decode()}">
        <p class="logo-text">Alpha Plus</p>
    </div>
    """,
    unsafe_allow_html=True,
)

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
        "nav-link-selected": {
            "background-color": "transparent",
            "color": "#8e00c6",
            # "font-weight": "bold",
            # "font-size": "20px",
            "border-top": "2px solid #8e00c6",
            "border-right": "2px solid #8e00c6",
            "border-left": "2px solid #8e00c6",
            "border-bottom": "2px solid #8e00c6",
        },
        "nav-link": {
            "font-weight": "bold",
        },
    },
)


# Display the selected page
if selected == "Forms":
    show_forms_page()
elif selected == "Data":
    show_data_page()
elif selected == "Dashboards":
    show_dashboard_page()
