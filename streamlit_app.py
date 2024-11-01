import streamlit as st

st.set_page_config(layout="wide")

# # Style to reduce header height
# reduce_header_height_style = """
#     <style>
#         div.block-container {padding-top:1rem;}
#     </style>
# """
# st.markdown(reduce_header_height_style, unsafe_allow_html=True)


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
    icon=":material/exit_to_app:",
    use_container_width=True,
)

st.sidebar.markdown("---")
st.sidebar.markdown("© 2024   Alpha +")  # Copyright
st.sidebar.markdown("All rights reserved.")

# --- RUN NAVIGATION ---
pg.run()
