# authentication.py

import uuid
import streamlit as st
from streamlit_authenticator import Authenticate
from streamlit_gsheets import GSheetsConnection
from typing import Callable, Any
from functools import wraps

# Connect to Google Sheets and get user data
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

authenticator_mapping = {}


def create_authenticator(AUTH_SECRET_KEY: str) -> None:
    if AUTH_SECRET_KEY not in authenticator_mapping:
        authenticator_mapping[AUTH_SECRET_KEY] = Authenticate(
            credentials=credentials,
            cookie_name="my_app_cookie",
            cookie_key=AUTH_SECRET_KEY,
            cookie_expiry_days=7,
            preauthorized=None,
        )


def get_authenticator(AUTH_SECRET_KEY: str) -> Authenticate:
    create_authenticator(AUTH_SECRET_KEY)
    return authenticator_mapping[AUTH_SECRET_KEY]


def authenticated(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if "AUTH_SECRET_KEY" not in st.session_state:
            st.session_state["AUTH_SECRET_KEY"] = AUTH_SECRET_KEY
        AUTH_SECRET_KEY = st.session_state["AUTH_SECRET_KEY"]

        authenticator = get_authenticator(AUTH_SECRET_KEY)

        login_result = authenticator.login(location="main")

        if login_result is None:
            st.warning("Please enter your username and password.")
            return None
        auth_status = login_result

        if auth_status:
            return func(*args, **kwargs)
        elif auth_status is False:
            st.error("Invalid username or password")
        else:
            st.warning("Please log in to continue")

    return wrapper


# def authenticated(func: Callable) -> Callable:
#     @wraps(func)
#     def wrapper(*args: Any, **kwargs: Any) -> Any:
#         if (
#             "authentication_status" not in st.session_state
#             or "AUTH_SECRET_KEY" not in st.session_state
#         ):
#             st.session_state["AUTH_SECRET_KEY"] = AUTH_SECRET_KEY
#         else:
#             AUTH_SECRET_KEY = st.session_state["AUTH_SECRET_KEY"]

#         name, authentication_status, username = _get_authenticator(
#             AUTH_SECRET_KEY
#         ).login("main")
#         if authentication_status is False:
#             st.error("Username/password is incorrect")
#         elif authentication_status is None:
#             st.warning("Please enter your username and password")
#         elif authentication_status:
#             return func()

#     return wrapper
