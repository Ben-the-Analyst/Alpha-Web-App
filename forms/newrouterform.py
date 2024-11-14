import pytz
import pandas as pd
import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection


# --------------------LOAD CUSTOM CSS---------------------------------------------------------------
def load_custom_css():
    with open("assets/css/style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_custom_css()


# --------------------CURRENT TIME---------------------------------------------------------------
def current_time():
    timezone = pytz.timezone("Africa/Nairobi")
    return datetime.now(timezone)


def get_current_month_details():
    current_date = current_time()
    current_month = current_date.strftime("%B")  # Full month name
    current_week = (current_date.day - 1) // 7 + 1  # Calculate week of month
    current_day = current_date.strftime("%A")  # Full day name
    return current_month, current_week, current_day


def get_month_options():
    return [datetime(2024, m, 1).strftime("%B") for m in range(1, 13)]


def get_week_of_month():
    current_date = current_time()
    last_day = (
        current_date.replace(day=1) + pd.DateOffset(months=1) - pd.DateOffset(days=1)
    ).day
    return list(
        range(1, (last_day // 7) + 2)
    )  # Adding 2 to account for possible partial weeks


def get_day_options():
    return [
        datetime(2024, 1, d).strftime("%A") for d in range(1, 8)
    ]  # Using 2024 Jan as it starts with Monday


# --------------------CACHE THE FUNCTION TO AVOID RELOADING DATA ON EACH ACTION--------------
@st.cache_data(ttl=300)
def fetch_data():
    # Establishing Google Sheets connection--------------------------------
    conn = st.connection("gsheets", type=GSheetsConnection)
    users = conn.read(worksheet="Users")
    clients_list_data = conn.read(worksheet="ClientsDatabase")
    existing_route_data = conn.read(worksheet="RoutePlan")
    return users, clients_list_data, existing_route_data


# --------------------GET AGENT NAMES---------------------------------------------------------------
def get_agent_names(users_df):
    # Filter users by role="User" and get their names and territory IDs
    agents = users_df[users_df["role"] == "User"][["name", "Territory_ID"]]
    return dict(zip(agents["name"], agents["Territory_ID"]))


@st.cache_data(persist=True)
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

        # Build client_id hierarchy - Map client names to their IDs
        client_id_data[client_name] = client_id  # Direct mapping of client name to ID

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
# def clear_form():
#     """Clears the form input fields."""
#     # st.session_state["route_plan_month"] = None
#     # st.session_state["route_plan_week"] = 1
#     # st.session_state["route_plan_day"] = None
#     st.session_state["route_plan_date"] = None
#     # st.session_state["route_plan_clientaddressselectedaddress"] = None
#     st.session_state["route_plan_clientselectedworkplace"] = None
#     st.session_state["route_plan_clientselectedclient"] = None


def new_route_planner():
    # if "show_clear_button" not in st.session_state:
    #     st.session_state.show_clear_button = False
    # f3, f4 = st.columns(2, gap="medium")
    # with f4:
    #     if st.button(
    #         label="Clear",
    #         on_click=clear_form,
    #         use_container_width=True,
    #         icon=":material/clear_all:",
    #         key="clear_route_planner_form",
    #     ):
    #         clear_form()

    users, clients_list_data, existing_route_data = fetch_data()

    current_month, current_week, current_day = get_current_month_details()

    month = st.selectbox(
        label="Month*",
        options=get_month_options(),
        index=get_month_options().index(current_month),
        key="route_plan_month",
    )

    week = st.selectbox(
        label="Week*",
        options=get_week_of_month(),
        index=(
            get_week_of_month().index(current_week)
            if current_week in get_week_of_month()
            else 0
        ),
        key="route_plan_week",
    )

    day = st.selectbox(
        label="Day*",
        options=get_day_options(),
        index=get_day_options().index(current_day),
        key="route_plan_day",
    )

    # month = st.selectbox(
    #     label="Month*", options=MONTHS, index=None, key="route_plan_month"
    # )
    # week = st.number_input(
    #     label="Week*", min_value=1, max_value=5, step=1, key="route_plan_week"
    # )
    # day = st.selectbox(label="Day*", options=DAYS, index=None, key="route_plan_day")
    date = st.date_input(label="Select Route Plan Date")
    # Get agent names and their territories
    agent_territories = get_agent_names(users)

    # Add agent selection at the top
    selected_agent = st.selectbox(
        label="Select Your Name*",
        options=sorted(agent_territories.keys()),
        index=None,
        key="route_plan_selected_agent",
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
        key="route_plan_clientaddressselectedaddress",
    )

    selected_workplace = st.selectbox(
        label="Select Client Workplace",
        options=(
            sorted(cached_data[selected_address].keys())
            if selected_address and selected_address in cached_data
            else []
        ),
        placeholder="select a work_place",
        key="route_plan_clientselectedworkplace",
    )

    selected_client = st.multiselect(
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
        key="route_plan_clientselectedclient",
    )
    st.markdown("**required*")
    message_placeholder = st.empty()  # Empty container for success or error messages
    spinner_placeholder = st.empty()  # New empty container for spinner
    st.divider()

    if st.button(
        "Submit Route Plan",
        key="submit_route_planner",
        help="Submit the route plan",
        type="primary",
        icon=":material/send_money:",
        use_container_width=True,
    ):
        if not (
            month
            and week
            and day
            and date
            and selected_agent
            and selected_territory
            and selected_address
            and selected_workplace
            and selected_client
        ):
            message_placeholder.warning("Ensure all mandatory fields are filled.")
        else:
            # Show spinner in the new location
            with spinner_placeholder:
                with st.spinner("Submitting your details..."):
                    # Collecting and submitting data
                    submission_time = current_time()
                    # Convert selected_client list to comma-separated string
                    client_names_str = ", ".join(selected_client)

                    # Get client IDs for selected clients and join them
                    client_ids_str = get_client_ids(
                        clients_list_data, selected_client, selected_workplace
                    )
                    route_data = pd.DataFrame(
                        [
                            {
                                "TimeStamp": submission_time.strftime(
                                    "%d-%m-%Y  %H:%M:%S"
                                ),
                                "Agent": selected_agent,
                                "Territory": selected_territory,
                                "Month": month,
                                "Week": week,
                                "Day": day,
                                "Date": date.strftime("%d-%m-%Y"),
                                "Address": selected_address,
                                "Workplace": selected_workplace,
                                "Client_ID": client_ids_str,
                                "Client_Name": client_names_str,
                            }
                        ]
                    )

                    # Append data
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    existing_route_data = pd.concat(
                        [existing_route_data, route_data], ignore_index=True
                    )
                    conn.update(worksheet="RoutePlan", data=existing_route_data)

            # Display success
            message_placeholder.success(
                "Route Plan details successfully submitted!",
                icon=":material/thumb_up:",
            )


def get_client_ids(clients_list_data, selected_clients, selected_workplace):
    """
    Get client IDs for selected clients in a specific workplace, maintaining the same order
    """
    # Fetch fresh data from the database
    conn = st.connection("gsheets", type=GSheetsConnection)
    fresh_clients_data = conn.read(worksheet="ClientsDatabase")

    # Filter fresh data for the selected workplace
    workplace_data = fresh_clients_data[
        fresh_clients_data["Workplace"] == selected_workplace
    ]

    # Create a dictionary mapping client names to their IDs
    client_id_map = dict(
        zip(workplace_data["Client_Name"], workplace_data["Client_ID"])
    )

    # Get client IDs in the same order as selected_clients
    ordered_client_ids = [str(client_id_map[client]) for client in selected_clients]

    return ", ".join(ordered_client_ids)
