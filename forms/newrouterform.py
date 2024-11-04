import pytz
import pandas as pd
import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection


# Function to get current time ------------------------
def current_time():
    timezone = pytz.timezone("Africa/Nairobi")
    return datetime.now(timezone)


# Cache the function to avoid reloading data on each action--------------
@st.cache_data(ttl=300)
def fetch_data():
    # Establishing Google Sheets connection--------------------------------
    conn = st.connection("gsheets", type=GSheetsConnection)
    institutions_list_data = conn.read(worksheet="Institutions")
    existing_route_data = conn.read(worksheet="RoutePlanner")
    return institutions_list_data, existing_route_data


@st.cache_data(persist=True)
def build_hierarchical_data(df):
    # hierarchical structure
    cached_data = {}

    for _, row in df.iterrows():
        agent_name = row["Names"]
        region = row["Regions"]
        institution = row["Institutions"]

        # --------nested dictionaries ---------------
        if agent_name not in cached_data:
            cached_data[agent_name] = {}  #  agent dictionary

        if region not in cached_data[agent_name]:
            cached_data[agent_name][region] = []  # region list

        # Add institution to the agent's region
        if institution not in cached_data[agent_name][region]:
            cached_data[agent_name][region].append(institution)

    # # Sort the keys alphabetically
    # for agent in cached_data:
    #     for region in cached_data[agent]:
    #         cached_data[agent][region] = sorted(cached_data[agent][region])

    # Inside build_hierarchical_data function
    for agent in cached_data:
        for region in cached_data[agent]:
            # Convert all values to strings before sorting
            cached_data[agent][region] = sorted(
                str(x) for x in cached_data[agent][region]
            )

    # Sort the outer keys (agents)
    cached_data = {k: cached_data[k] for k in sorted(cached_data)}

    return cached_data


# def clear_form():
#     """Clears the form input fields."""
#     # st.session_state["Selectrouteterritory"] = None
#     st.session_state["routemonthdropdown"] = None
#     st.session_state["routeweeknumber"] = 1
#     st.session_state["routedayofweek"] = None
#     # st.session_state["routenameselectedname"] = None
#     # st.session_state["routeregionselectedregion"] = None
#     # st.session_state["routeinstitutionsselectedinstitutions"] = []


def new_route_planner():
    institutions_list_data, existing_route_data = fetch_data()

    # Define static options
    TERRITORIES = institutions_list_data["Territories"].unique().tolist()
    MONTHS = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    DAYS = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    # Build and cache the hierarchical data
    cached_data = build_hierarchical_data(institutions_list_data)

    # Form Inputs
    territoriesx = st.selectbox(
        label="Select Territory*",
        options=TERRITORIES,
        index=None,
        key="Selectrouteterritory",
    )
    month = st.selectbox(
        label="Month*", options=MONTHS, index=None, key="routemonthdropdown"
    )
    week = st.number_input(
        label="Week*", min_value=1, max_value=5, step=1, key="routeweeknumber"
    )
    day = st.selectbox(label="Day*", options=DAYS, index=None, key="routedayofweek")
    date = st.date_input(label="Select Route Plan Date")
    selected_name = st.selectbox(
        label="Select Name",
        options=cached_data.keys(),
        placeholder="select your name",
        key="routenameselectedname",
    )
    selected_region = st.selectbox(
        label="Select Region",
        options=sorted(cached_data[selected_name].keys()),
        placeholder="select a region",
        key="routeregionselectedregion",
    )
    selected_institutions = st.multiselect(
        label="Select Institutions / Stores",
        options=sorted(cached_data[selected_name][selected_region]),
        placeholder="select institutions",
        key="routeinstitutionsselectedinstitutions",
    )
    # selected_region = st.selectbox(
    #     label="Select Region",
    #     options=cached_data[selected_name].keys(),
    #     placeholder="select a region",
    #     key="routeregionselectedregion",
    # )
    # selected_institutions = st.multiselect(
    #     label="Select Institutions / Stores",
    #     options=cached_data[selected_name][selected_region],
    #     placeholder="select institutions",
    #     key="routeinstitutionsselectedinstitutions",
    # )

    message_placeholder = st.empty()  # Empty container for success or error messages

    f3, f4 = st.columns(2)
    with f3:

        # Submit Button
        if st.button("Submit Route Plan"):
            if not (
                territoriesx
                and month
                and week
                and day
                and date
                and selected_name
                and selected_region
                and selected_institutions
            ):
                message_placeholder.warning("Ensure all mandatory fields are filled.")
            else:
                # Show spinner
                with st.spinner("Submitting your details..."):
                    # Collecting and submitting data
                    submission_time = current_time()
                    route_data = pd.DataFrame(
                        [
                            {
                                "Territory": territoriesx,
                                "Month": month,
                                "Week": week,
                                "Day": day,
                                "Date": date.strftime("%d-%m-%Y"),
                                "Agent": selected_name,
                                "Region": selected_region,
                                "Institutions": ", ".join(selected_institutions),
                                "TimeStamp": submission_time.strftime(
                                    "%d-%m-%Y  %H:%M:%S"
                                ),
                            }
                        ]
                    )

                    # Append data
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    existing_route_data = pd.concat(
                        [existing_route_data, route_data], ignore_index=True
                    )
                    conn.update(worksheet="RoutePlanner", data=existing_route_data)

                # Display success
                message_placeholder.success(
                    "Route Plan details successfully submitted!",
                    icon=":material/thumb_up:",
                )

    # with f4:
    #     if st.button(label="Clear", on_click=clear_form):
    #         clear_form
