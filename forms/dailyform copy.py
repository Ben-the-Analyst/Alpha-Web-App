import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import pytz
import re


# --------------------AUTHENTICATION CHECK---------------------------------------------------------------
# if not st.session_state.get("authenticated"):
#     st.error("Please login to access this page")
#     st.stop()


# Retrieve authenticator from session state
authenticator = st.session_state.get("authenticator", None)

# --------------------GET USER SPECIFIC DATA(Signed in user)---------------------------------------------------------------
username = st.session_state["username"]
user_credentials = st.session_state["user_credentials"]
# user_credentials = st.session_state["credentials"]["usernames"][username]
user_territory = user_credentials["Territory_ID"]
user_role = user_credentials["role"]


# --------------------------------SPINNER LOADING TIME---------------------------------------------------------------
# def load_form_data():
#     time.sleep(2)


# --------------------CURRENT TIME---------------------------------------------------------------
def current_time():
    timezone = pytz.timezone("Africa/Nairobi")  # Setting timezone to East Africa
    return datetime.now(timezone)


def current_month():
    """Returns current month in 3-letter format with first letter capitalized (e.g., 'Jan')"""
    return current_time().strftime("%b")


def current_week():
    """Returns the current week number of the month (1-5)"""
    current_date = current_time()
    # Get the first day of the month
    first_day = current_date.replace(day=1)
    # Get the day of the first week containing the 1st of the month
    first_week_day = first_day.day - first_day.weekday()
    # Calculate current week number
    current_week = ((current_date.day - first_week_day) // 7) + 1
    return current_week


def today_dayOfweek():
    """Returns current day of week with first letter capitalized (e.g., 'Monday')"""
    return current_time().strftime("%A")


# --------------------LOAD CLIENTS DATABASE---------------------------------------------------------------


# Cache the function to avoid reloading data on each action--------------
@st.cache_data(ttl=300)
def fetch_data():
    # Establishing Google Sheets connection--------------------------------
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Read the full clients database
    clients_list_data = conn.read(worksheet="ClientsDatabase")

    # Filter data if user role is "User"
    if user_role == "User":
        clients_list_data = clients_list_data[
            clients_list_data["Territory"] == user_territory
        ]

    existing_route_data = conn.read(worksheet="DailyReport")
    outcomes = conn.read(worksheet="Outcome")
    return clients_list_data, existing_route_data, outcomes


# --------------------BUILD HIERARCHICAL DATA---------------------------------------------------------------
# @st.cache_data(persist=True)
# @st.cache_data(ttl=300)
def build_hierarchical_data(df):
    # Create separate hierarchical structures
    cached_data = {}
    client_id_data = {}  # New structure for territories

    for _, row in df.iterrows():
        client_id = str(row["Client_ID"])  # Convert to string
        address = str(row["Line_Address"])  # Convert to string
        work_place = str(row["Workplace"])  # Convert to string
        client_name = str(row["Client_Name"])  # Convert to string

        # Build client_id hierarchy
        if address not in client_id_data:
            client_id_data[address] = set()
        client_id_data[address].add(client_id)

        # Build work_place and client_name hierarchy
        if address not in cached_data:
            cached_data[address] = {}

        if work_place not in cached_data[address]:
            cached_data[address][work_place] = []

        if client_name not in cached_data[address][work_place]:
            cached_data[address][work_place].append(client_name)

    # Sort institutions within regions
    for agent in cached_data:
        for work_place in cached_data[agent]:
            cached_data[agent][work_place] = sorted(cached_data[agent][work_place])

    # Convert client_id sets to sorted lists
    client_id_data = {
        agent: sorted(territories) for agent, territories in client_id_data.items()
    }

    # Sort the outer keys (agents)
    cached_data = {k: cached_data[k] for k in sorted(cached_data.keys())}
    client_id_data = {k: client_id_data[k] for k in sorted(client_id_data.keys())}

    return cached_data, client_id_data


# --------------------DAILY REPORTING FORM---------------------------------------------------------------
def clear_form():
    """Clears the form input fields."""
    st.session_state["routeaddressselectedaddress"] = None
    st.session_state["routeworkplaceselectedworkplace"] = None
    st.session_state["routeclientsselectedclient"] = None
    st.session_state["daily_objective"] = None
    st.session_state["daily_comments"] = None
    st.session_state["daily_outcomes"] = None
    st.session_state["daily_future_objective"] = None
    st.session_state["daily_appointment"] = None


def daily_reporting_form():
    clients_list_data, existing_route_data, outcomes = fetch_data()

    OUTCOMES = outcomes["Outcomes"].unique().tolist()
    OUTCOMES = sorted(OUTCOMES)

    # Build and cache the hierarchical data
    cached_data, client_id_data = build_hierarchical_data(clients_list_data)

    selected_address = st.selectbox(
        label="Select Client Address",
        options=cached_data.keys(),
        placeholder="select address",
        key="routeaddressselectedaddress",
    )

    selected_workplace = st.selectbox(
        label="Select Client Workplace",
        options=(
            sorted(cached_data[selected_address].keys()) if selected_address else []
        ),
        placeholder="select a work_place",
        key="routeworkplaceselectedworkplace",
    )
    selected_client = st.selectbox(
        label="Select Client Name",
        options=sorted(cached_data[selected_address][selected_workplace]),
        placeholder="select client name",
        key="routeclientsselectedclient",
    )

    selected_territory = (
        client_id_data[selected_address][0] if selected_address else None
    )

    objective = st.text_input(label="Task Objective*", key="daily_objective")

    comments = st.text_area(label="Comments/Notes*", key="daily_comments")

    outcomes = st.selectbox(
        "Overall Outcome*",
        options=OUTCOMES,
        index=None,
        key="daily_outcomes",
        placeholder="Choose most relevant ",
    )

    future_objective = st.text_area(
        label="Future Task Objective", key="daily_future_objective"
    )

    appointment = st.date_input(
        label="Next Appointment", format="DD/MM/YYYY", key="daily_appointment"
    )

    st.markdown("**required*")

    message_placeholder = st.empty()  # Empty container for success or error messages
    spinner_placeholder = st.empty()  # New empty container for spinner
    st.divider()

    f3, f4 = st.columns(2, gap="medium")
    with f3:
        if st.button(
            label="Clear",
            on_click=clear_form,
            use_container_width=True,
            icon=":material/clear_all:",
        ):
            clear_form()
    with f4:
        # Submit Button
        if st.button(
            "Submit Report",
            key="dailyform_submit",
            help="Submit your daily report",
            type="primary",
            icon=":material/send_money:",
            use_container_width=True,
        ):
            if not (
                selected_address
                and selected_workplace
                and selected_client
                and objective
                and comments
                and outcomes
                and future_objective
                and appointment
            ):
                message_placeholder.warning("Ensure all mandatory fields are filled.")
            else:
                # Show spinner in the new location
                with spinner_placeholder:
                    with st.spinner("Submitting your details..."):
                        # Collecting and submitting data
                        submission_time = current_time()
                        route_data = pd.DataFrame(
                            [
                                {
                                    "TimeStamp": submission_time.strftime(
                                        "%d-%m-%Y  %H:%M:%S"
                                    ),
                                    "Territory": user_territory,
                                    "Month": current_month,
                                    "Week": current_week,
                                    "Day": today_dayOfweek,
                                    "Client_ID": selected_territory,
                                    "Address": selected_address,
                                    "Region": selected_workplace,
                                    "Institutions": ", ".join(selected_client),
                                    "Task Objective": objective,
                                    "Comments/Notes": comments,
                                    "Outcome": outcomes,
                                    "Future Task Objective": future_objective,
                                    "Next Appointment": appointment.strftime(
                                        "%d-%m-%Y"
                                    ),
                                }
                            ]
                        )

                        # Append data
                        conn = st.connection("gsheets", type=GSheetsConnection)
                        existing_route_data = pd.concat(
                            [existing_route_data, route_data], ignore_index=True
                        )
                        conn.update(worksheet="DailyReport", data=existing_route_data)

                # Display success
                message_placeholder.success(
                    "Daily Report successfully submitted!",
                    icon=":material/thumb_up:",
                )
    st.divider()


# --------------------LEGACY DAILY FORM (FOR REFERENCE)---------------------------------------------------------------
# def daily_form():
#     with st.spinner("Loading your form ..."):
#         load_form_data()

#     st.write("All the fields are mandatory")

#     conn = st.connection("gsheets", type=GSheetsConnection)

#     existing_daily_data = conn.read(worksheet="DailyData")
#     clients_list_data = conn.read(worksheet="ClientsDatabase")
#     cadre = conn.read(worksheet="Cadre")
#     institution_types = conn.read(worksheet="Type")
#     institutions_department = conn.read(worksheet="Department")
#     outcomes = conn.read(worksheet="Outcome")

#     # Create agent-territory mapping
#     agent_territory_map = dict(
#         zip(clients_list_data["Names"], clients_list_data["Territories"])
#     )

#     PREFIXES = ["Mr.", "Mrs.", "Ms.", "Dr.", "Prof."]
#     AGENTNAMES = clients_list_data["Names"].unique().tolist()
#     CADRE = cadre["Cadre"].unique().tolist()
#     TYPE = institution_types["Type"].unique().tolist()
#     DEPARTMENT = institutions_department["Department"].unique().tolist()
#     OUTCOMES = outcomes["Outcomes"].unique().tolist()

#     PREFIXES = sorted(PREFIXES)
#     AGENTNAMES = sorted(AGENTNAMES)
#     CADRE = sorted(CADRE)
#     TYPE = sorted(TYPE)
#     DEPARTMENT = sorted(DEPARTMENT)
#     OUTCOMES = sorted(OUTCOMES)

#     with st.form(key="daily_form", clear_on_submit=True):
#         agentname = st.selectbox(
#             "Your Name*", options=AGENTNAMES, index=None, key="daily_agentname"
#         )

#         # if agentname:
#         #     st.info(f"Territory: {agent_territory_map[agentname]}")

#         date = st.date_input(label="Date", format="DD/MM/YYYY", key="daily_date")

#         prefix = st.selectbox(
#             "prefix*", options=PREFIXES, index=None, key="daily_prefix"
#         )

#         client_surname = st.text_input(
#             label="HCP/Client Surname*", key="daily_client_surname"
#         )

#         client_firstname = st.text_input(
#             label="HCP/Client Firstname*", key="daily_client_firstname"
#         )

#         cadre = st.selectbox("Cadre*", options=CADRE, index=None, key="daily_cadre")

#         institution_name = st.text_input(
#             label="Institution Name*", key="daily_institution_name"
#         )

#         pos_type = st.selectbox(
#             "Institution (POS) Type*", options=TYPE, index=None, key="daily_pos_type"
#         )

#         department = st.selectbox(
#             "Institution Department*",
#             options=DEPARTMENT,
#             index=None,
#             key="daily_department",
#         )

#         objective = st.text_input(label="Task Objective*", key="daily_objective")

#         comments = st.text_area(label="Comments/Notes*", key="daily_comments")

#         outcomes = st.selectbox(
#             "Overall Outcome*",
#             options=OUTCOMES,
#             index=None,
#             key="daily_outcomes",
#             placeholder="Choose most relevant ",
#         )

#         future_objective = st.text_area(
#             label="Future Task Objective", key="daily_future_objective"
#         )

#         appointment = st.date_input(
#             label="Next Appointment", format="DD/MM/YYYY", key="daily_appointment"
#         )

#         st.markdown("**required*")

#         message_placeholder = st.empty()
#         spinner_placeholder = st.empty()
#         st.divider()

#         submit_button = st.form_submit_button(
#             label="Submit ",
#             help="Submit your Details",
#             type="primary",
#             icon=":material/send_money:",
#             use_container_width=True,
#         )

#         if submit_button:

#             if (
#                 not agentname
#                 or not date
#                 or not prefix
#                 or not client_surname
#                 or not client_firstname
#                 or not cadre
#                 or not institution_name
#                 or not pos_type
#                 or not department
#                 or not objective
#                 or not comments
#                 or not outcomes
#                 or not future_objective
#                 or not appointment
#             ):
#                 message_placeholder.warning(
#                     icon=":material/error:",
#                     body="Ensure all fields are filled.",
#                 )
#                 st.stop()

#             with spinner_placeholder:
#                 with st.spinner("Submitting your details..."):
#                     load_form_data()

#                 submission_time = current_time()

#                 client_surname = client_surname.capitalize()
#                 client_firstname = client_firstname.capitalize()
#                 institution_name = institution_name.capitalize()
#                 objective = objective.capitalize()
#                 comments = comments.capitalize()
#                 future_objective = future_objective.capitalize()

#                 daily_data = pd.DataFrame(
#                     [
#                         {
#                             "Name": agentname,
#                             "Territory": agent_territory_map[agentname],
#                             "Date": date.strftime("%d-%m-%Y"),
#                             "Prefix": prefix,
#                             "HCP Surname": client_surname,
#                             "HCP Firstname": client_firstname,
#                             "Cadre": cadre,
#                             "Institution": institution_name,
#                             "Institution (POS) Type": pos_type,
#                             "Institution Department": department,
#                             "Task Objective": objective,
#                             "Comments/Notes": comments,
#                             "Outcome": outcomes,
#                             "Future Task Objective": future_objective,
#                             "Next Appointment": appointment.strftime("%d-%m-%Y"),
#                             "TimeStamp": submission_time.strftime("%d-%m-%Y  %H:%M:%S"),
#                         }
#                     ]
#                 )

#                 updated_daily_df = pd.concat(
#                     [existing_daily_data, daily_data], ignore_index=True
#                 )

#                 conn.update(worksheet="DailyData", data=updated_daily_df)

#                 message_placeholder.success(
#                     icon=":material/thumb_up:",
#                     body="Daily Activity details successfully submitted!",
# )
