import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import pytz

# # --------------------AUTHENTICATION CHECK---------------------------------------------------------------
# if not st.session_state.get("authenticated"):
#     st.error("Please login to access this page")
#     st.stop()

# # --------------------GET USER SPECIFIC DATA(Signed in user)---------------------------------------------------------------
# username = st.session_state["username"]
# user_credentials = st.session_state["user_credentials"]
# # user_credentials = st.session_state["credentials"]["usernames"][username]
# user_territory = user_credentials["Territory_ID"]
# user_role = user_credentials["role"]
# user_fullname = user_credentials["fullname"]


# --------------------LOAD CUSTOM CSS---------------------------------------------------------------
def load_custom_css():
    with open("assets/css/style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_custom_css()


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
    clients_list_data = conn.read(worksheet="ClientsDatabase")
    existing_daily_data = conn.read(worksheet="DailyReport")
    outcomes = conn.read(worksheet="Outcome")
    users = conn.read(worksheet="Users")

    return clients_list_data, existing_daily_data, outcomes, users


# Add new function to get agent names
def get_agent_names(users_df):
    # Filter users by role="User" and get their names and territory IDs
    agents = users_df[users_df["role"] == "User"][["name", "Territory_ID"]]
    return dict(zip(agents["name"], agents["Territory_ID"]))


# --------------------BUILD HIERARCHICAL DATA---------------------------------------------------------------
@st.cache_data(persist=True)
# @st.cache_data(ttl=300)
def build_hierarchical_data(df, territory_id=None):
    # Filter data by territory if provided
    if territory_id:
        df = df[df["Territory"] == territory_id]

    cached_data = {}
    client_id_data = {}

    for _, row in df.iterrows():
        client_id = str(row["Client_ID"])
        address = str(row["Line_Address"])
        work_place = str(row["Workplace"])
        client_name = str(row["Client_Name"])

        # Build client_id hierarchy
        if address not in client_id_data:
            client_id_data[address] = client_id

        # Build work_place and client_name hierarchy
        if address not in cached_data:
            cached_data[address] = {}

        if work_place not in cached_data[address]:
            cached_data[address][work_place] = []

        if client_name not in cached_data[address][work_place]:
            cached_data[address][work_place].append(client_name)

    # Sort the data
    cached_data = {
        k: {wk: sorted(wv) for wk, wv in v.items()}
        for k, v in sorted(cached_data.items())
    }

    return cached_data, client_id_data


# --------------------DAILY REPORTING FORM---------------------------------------------------------------
def clear_form():
    """Clears the form input fields."""
    # st.session_state["daily_rpt_clientaddressselectedaddress"] = None
    st.session_state["daily_rpt_clientselectedworkplace"] = None
    st.session_state["daily_rpt_clientselectedclient"] = None
    st.session_state["daily_rpt_objective"] = ""
    st.session_state["daily_rpt_comments"] = ""
    st.session_state["daily_rpt_outcomes"] = None
    st.session_state["daily_rpt_future_objective"] = ""
    st.session_state["daily_rpt_appointment"] = datetime.now().date()


def daily_reporting_form():
    if "show_clear_button" not in st.session_state:
        st.session_state.show_clear_button = False
    f3, f4 = st.columns(2, gap="medium")
    with f4:
        if st.button(
            label="Clear",
            on_click=clear_form,
            use_container_width=True,
            icon=":material/clear_all:",
            key="clear_daily_form",
        ):
            clear_form()

    clients_list_data, existing_daily_data, outcomes, users = fetch_data()

    OUTCOMES = outcomes["Outcomes"].unique().tolist()
    PREFIXES = ["Mr.", "Mrs.", "Ms.", "Dr.", "Prof."]
    OUTCOMES = sorted(OUTCOMES)
    PREFIXES = sorted(PREFIXES)

    # Get agent names and their territories
    agent_territories = get_agent_names(users)

    # Add agent selection at the top
    selected_agent = st.selectbox(
        label="Select Your Name*",
        options=sorted(agent_territories.keys()),
        index=None,
        key="daily_rpt_selected_agent",
    )

    # Get territory ID for selected agent
    selected_territory = (
        agent_territories.get(selected_agent) if selected_agent else None
    )

    # Build hierarchical data filtered by territory
    cached_data, client_id_data = (
        build_hierarchical_data(clients_list_data, territory_id=selected_territory)
        if selected_territory
        else ({}, {})
    )

    selected_address = st.selectbox(
        label="Select Client Address",
        options=cached_data.keys() if cached_data else [],
        placeholder="select address",
        key="daily_rpt_clientaddressselectedaddress",
    )

    selected_workplace = st.selectbox(
        label="Select Client Workplace",
        options=(
            sorted(cached_data[selected_address].keys())
            if selected_address and selected_address in cached_data
            else []
        ),
        placeholder="select a work_place",
        key="daily_rpt_clientselectedworkplace",
    )

    selected_client = st.selectbox(
        label="Select Client Name",
        options=(
            sorted(cached_data[selected_address][selected_workplace])
            if selected_address
            and selected_workplace
            and selected_address in cached_data
            and selected_workplace in cached_data[selected_address]
            else []
        ),
        placeholder="select client name",
        key="daily_rpt_clientselectedclient",
    )

    prefix = st.selectbox(
        label="Prefix", options=PREFIXES, index=None, key="daily_rpt_prefix"
    )

    objective = st.text_input(label="Task Objective*", key="daily_rpt_objective")

    comments = st.text_area(label="Comments/Notes*", key="daily_rpt_comments")

    outcomes = st.selectbox(
        "Overall Outcome*",
        options=OUTCOMES,
        index=None,
        key="daily_rpt_outcomes",
        placeholder="Choose most relevant ",
    )

    future_objective = st.text_area(
        label="Future Task Objective", key="daily_rpt_future_objective"
    )

    appointment = st.date_input(
        label="Next Appointment", format="DD/MM/YYYY", key="daily_rpt_appointment"
    )

    st.markdown("**required*")

    message_placeholder = st.empty()  # Empty container for success or error messages
    spinner_placeholder = st.empty()  # New empty container for spinner

    # Submit Button
    if st.button(
        "Submit Report",
        key="submit_daily_form",
        help="Submit your daily report",
        type="primary",
        icon=":material/send_money:",
        use_container_width=True,
    ):
        if not (
            selected_agent
            and selected_address
            and selected_workplace
            and selected_client
            and prefix
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
                    current_month_val = current_month()
                    current_week_val = current_week()
                    current_day_val = today_dayOfweek()
                    daily_data = pd.DataFrame(
                        [
                            {
                                "TimeStamp": submission_time.strftime(
                                    "%d-%m-%Y  %H:%M:%S"
                                ),
                                "Agent_Name": selected_agent,
                                "Territory": selected_territory,
                                "Month": current_month_val,  # Use value instead of function
                                "Week": current_week_val,  # Use value instead of function
                                "Day": current_day_val,
                                "Address": selected_address,
                                "Workplace": selected_workplace,
                                "Client_ID": client_id_data.get(selected_address),
                                "Prefix": prefix,
                                "Client_Name": selected_client,
                                "Task_Objective": objective,
                                "Comments/Notes": comments,
                                "Outcome": outcomes,
                                "Future_Task_Objective": future_objective,
                                "Next_Appointment": appointment.strftime("%d-%m-%Y"),
                            }
                        ]
                    )

                    # Append data
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    existing_daily_data = pd.concat(
                        [existing_daily_data, daily_data], ignore_index=True
                    )
                    conn.update(worksheet="DailyReport", data=existing_daily_data)

            # Display success
            message_placeholder.success(
                "Daily Report successfully submitted!",
                icon=":material/thumb_up:",
            )
