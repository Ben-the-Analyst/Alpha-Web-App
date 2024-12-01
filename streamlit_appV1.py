import time
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_gsheets import GSheetsConnection

# --------------------SETUP THE STREAMLIT PAGE CONFIGURATION---------------------------------------------------------------
st.set_page_config(
    page_title="AlphaPlus",
    page_icon=":material/home:",
    initial_sidebar_state="collapsed",
    layout="wide",
)

# --------------------REDUCE HEADER HEIGHT---------------------------------------------------------------

# reduce_header_height_style = """
#     <style>
#         div.block-container {padding-top:1rem;}
#     </style>
# """
# st.markdown(reduce_header_height_style, unsafe_allow_html=True)


# --------------------LOAD USER DATA FROM GOOGLE SHEETS---------------------------------------------------------------
conn = st.connection("gsheets", type=GSheetsConnection)
users_df = conn.read(worksheet="Users")
users = users_df.to_dict("records")

credentials = {"usernames": {}}
for user in users:
    credentials["usernames"][user["username"]] = {
        "fullname": user["name"],
        "name": user["username"],
        "email": user["email"],
        "password": user["password"],
        "role": user["role"],
        "Territory_ID": user["Territory_ID"],
    }

# --------------------SETUP THE STREAMLIT AUTHENTICATOR---------------------------------------------------------------
Authenticator = stauth.Authenticate(
    credentials,
    cookie_name="alphaplus",
    key="AUTH_SECRET_KEY",
    cookie_expiry_days=30,
)

# --------------------LOGIN FORM---------------------------------------------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        with st.spinner("    Fetching ..."):
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


# --------------------AUTHENTICATION CHECK---------------------------------------------------------------
if st.session_state["authentication_status"]:
    # Set all necessary authentication info in session state
    st.session_state["credentials"] = credentials
    st.session_state["authenticated"] = True
    st.session_state["username"] = st.session_state["username"]
    st.session_state["name"] = st.session_state["name"]
    st.session_state["user_credentials"] = credentials["usernames"][
        st.session_state["username"]
    ]

    # --- PAGE SETUP -------------------------------------------------------------------------------------------
    home_page = st.Page(
        "home.py",
        title="Home",
        icon=":material/home:",
        default=True,
    )
    # dashboard = st.Page(
    #     "sales_dashboard.py",
    #     title="Sales Dashboard",
    #     icon=":material/bar_chart:",
    # )
    # project_2_page = st.Page(
    #     "page.py",
    #     title="Chat Bot",
    #     icon=":material/smart_toy:",
    # )

    # --- NAVIGATION SETUP [WITHOUT SECTIONS] ----------------------------------------------------------------------------
    pg = st.navigation(pages=[home_page])

    # --- NAVIGATION SETUP [WITH SECTIONS]----------------------------------------------------------------------------
    # pg = st.navigation(
    #     {
    #         "Info": [home_page],
    #         "Projects": [dashboard],
    #     }
    # )

    # --- SHARED ON ALL z_AllPages ---------------------------------------------------------------------------------
    st.logo("static/logo.png", size="large")

    # ---------SIDEBAR-------------------------------------------------------------------------------------

    with st.sidebar.container(key="my_territoryid_container"):
        st.markdown(
            """
       <style>
       [data-testid="stSidebar"][aria-expanded="true"]{
           min-width: 244px;
           max-width: 244px;
       }
       """,
            unsafe_allow_html=True,
        )

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
        # st.write(
        #     f'username: <span style="color: {primary_color};"><strong>{user_credentials["name"]}</strong></span>',
        #     unsafe_allow_html=True,
        # )
        # Use the user-specific Territory_ID from credentials
        st.write(
            f"Your Territory: <span style='color: {primary_color};'><strong>{user_credentials['Territory_ID']}</strong></span>",
            unsafe_allow_html=True,
        )

    # --------------------LOGOUT BUTTON---------------------------------------------------------------
    if Authenticator.logout("Logout", "sidebar"):
        with st.spinner("Logging out..."):
            # Clear all authentication-related session state
            for key in [
                "authenticated",
                "username",
                "name",
                "credentials",
                "user_credentials",
                "authentication_status",
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.write("You have logged out successfully.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2024   Alpha +")  # Copyright
    st.sidebar.markdown("All rights reserved.")

    # --- RUN NAVIGATION ---
    pg.run()

    # After creating credentials
    st.session_state["credentials"] = credentials
    current_user_credentials = st.session_state["credentials"]


elif st.session_state["authentication_status"] is False:
    with col2:
        st.error("Username/password is incorrect")
elif st.session_state["authentication_status"] is None:
    with col2:
        st.info("Please enter your username and password")
