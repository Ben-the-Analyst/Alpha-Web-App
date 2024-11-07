import streamlit as st
import streamlit_authenticator as stauth
from streamlit_gsheets import GSheetsConnection
import time

# Set up the Streamlit page configuration
st.set_page_config(
    page_title="AlphaPlus",
    page_icon=":material/home:",
    initial_sidebar_state="collapsed",
    layout="wide",
)

# # Style to reduce header height
# reduce_header_height_style = """
#     <style>
#         div.block-container {padding-top:1rem;}
#     </style>
# """
# st.markdown(reduce_header_height_style, unsafe_allow_html=True)


# Establish a connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
users_df = conn.read(worksheet="Users")
# Extract user information from the Google Sheets data
users = users_df.to_dict("records")
fullname = []
emails = []
usernames = []
passwords = []
role = []
Territory_ID = []

# Organize user details into separate lists
for user in users:
    fullname.append(user["name"])
    emails.append(user["email"])
    usernames.append(user["username"])
    passwords.append(user["password"])
    role.append(user["role"])
    Territory_ID.append(user["Territory_ID"])
# st.write(users)
# st.write(emails)
# st.write(usernames)
# st.write(passwords)

# Define the credentials dictionary in the format expected by streamlit_authenticator
credentials = {"usernames": {}}
for index in range(len(usernames)):
    credentials["usernames"][usernames[index]] = {
        "fullname": fullname[index],
        "name": usernames[index],
        "email": emails[index],
        "password": passwords[index],
        "role": role[index],
        "Territory_ID": Territory_ID[index],
    }

Authenticator = stauth.Authenticate(
    credentials,
    cookie_name="Streamlit",
    key="AUTH_SECRET_KEY",
    cookie_expiry_days=6,
    preauthorized=emails,
)
# st.write(credentials)
col1, col2, col3 = st.columns(3)
with col2:
    try:
        with st.spinner("Hold on! Running ..."):
            name_or_status = Authenticator.login(
                fields={
                    "Form name": "Login to Alpa + ",
                    "Login": "Get Access",
                },
                location="main",
            )
            if st.session_state.get("authentication_status"):
                time.sleep(2)  # Short delay for smooth transition
    except Exception as e:
        st.error(e)

    # info, info1 = st.columns(2)

if st.session_state["authentication_status"]:

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

    # ---------HEADER----------------

    with st.sidebar.container(key="my_territoryid_container"):
        primary_color = st.get_option("theme.primaryColor")
        username = st.session_state["username"]
        user_credentials = credentials["usernames"][username]

        st.write(
            f'Welcome Back <span style="color: {primary_color};"><strong>{user_credentials["fullname"]}</strong></span>',
            unsafe_allow_html=True,
        )
        # st.write(
        #     f'Role: <span style="color: {primary_color};"><strong>{user_credentials["role"]}</strong></span>',
        #     unsafe_allow_html=True,
        # )
        # Use the user-specific Territory_ID from credentials
        st.write(
            f"Your Territory: <span style='color: {primary_color};'><strong>{user_credentials['Territory_ID']}</strong></span>",
            unsafe_allow_html=True,
        )
        # st.write(f'Welcome Back **{st.session_state["name"]}**')
        # st.write(
        #     f'Welcome Back <span style="color: {primary_color};"><strong>{st.session_state["name"]}</strong></span>',
        #     unsafe_allow_html=True,
        # )

    if Authenticator.logout("Logout", "sidebar"):
        with st.spinner("Logging out..."):
            time.sleep(10)  # Short delay for smooth transition
            st.rerun()  # Rerun the app to refresh the page

    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2024   Alpha +")  # Copyright
    st.sidebar.markdown("All rights reserved.")

    # --- RUN NAVIGATION ---
    pg.run()

    # After creating credentials
    st.session_state["credentials"] = credentials
    current_user_credentials = st.session_state["credentials"]

elif st.session_state["authentication_status"] is False:
    st.error("Username/password is incorrect")
elif st.session_state["authentication_status"] is None:
    st.warning("Please enter your username and password")
