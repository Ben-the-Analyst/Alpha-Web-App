import streamlit as st
import pickle


st.set_page_config(layout="wide")

# Style to reduce header height
reduce_header_height_style = """
    <style>
        div.block-container {padding-top:1rem;}
    </style>
"""
st.markdown(reduce_header_height_style, unsafe_allow_html=True)


# --- PAGE SETUP ---
home_page = st.Page(
    "z_AllPages/home.py",
    title="Home",
    icon=":material/home:",
    default=True,
)
dashboard = st.Page(
    "z_AllPages/sales_dashboard.py",
    title="Sales Dashboard",
    icon=":material/bar_chart:",
)
# project_2_page = st.Page(
#     "z_AllPages/chatbot.py",
#     title="Chat Bot",
#     icon=":material/smart_toy:",
# )


# --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
pg = st.navigation(pages=[home_page, dashboard])

# --- NAVIGATION SETUP [WITH SECTIONS]---
# pg = st.navigation(
#     {
#         "Info": [home_page],
#         "Projects": [dashboard],
#     }
# )


# --- SHARED ON ALL z_AllPages ---
st.logo("assets/images/logo.png", size="large")
st.sidebar.markdown("Some content here")
st.sidebar.button(
    "Logout",
    key="logout_button",
    icon=":material/move_item:",
    use_container_width=True,
)

st.sidebar.markdown("---")
st.sidebar.markdown("© 2024   Alpha +")  # Copyright
st.sidebar.markdown("All rights reserved.")

# --- RUN NAVIGATION ---
pg.run()


import streamlit as st
import pandas as pd
import requests as rs
from streamlit_gsheets import GSheetsConnection

st.title("Amazing User Login App")


conn = st.connection("gsheets", type=GSheetsConnection)
database = conn.read(worksheet="Users")

# Create user_state
if "user_state" not in st.session_state:
    st.session_state.user_state = {
        "FirstName": "",
        "Password": "",
        "logged_in": False,
        "Role": "",
        "Email": "",
        "Username": "",
    }

if not st.session_state.user_state["logged_in"]:
    # Create login form
    st.write("Please login")
    Email = st.text_input("E-Mail")
    Password = st.text_input("Password", type="password")
    submit = st.button("Login")

    # Check if user is logged in
    if submit:
        user_ = database[database["Email"] == Email].copy()
        if len(user_) == 0:
            st.error("User not found")
        else:
            if (
                user_["Email"].values[0] == Email
                and user_["Password"].values[0] == Password
            ):
                st.session_state.user_state["Email"] = Email
                st.session_state.user_state["Password"] = Password
                st.session_state.user_state["logged_in"] = True
                st.session_state.user_state["Role"] = user_["Role"].values[0]
                st.session_state.user_state["Email"] = user_["Email"].values[0]
                st.session_state.user_state["Username"] = user_["Username"].values[0]
                st.write("You are logged in")
                st.rerun()
            else:
                st.write("Invalid username or Password")
elif st.session_state.user_state["logged_in"]:
    st.write("Welcome to the app")
    st.write("You are logged in as:", st.session_state.user_state["Email"])
    st.write("You are a:", st.session_state.user_state["Role"])
    st.write("Your fixed user message:", st.session_state.user_state["Username"])
    if st.session_state.user_state["Role"] == "admin":
        st.write("You have admin rights. Here is the database")
        st.table(database)
