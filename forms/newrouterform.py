import time
import pytz
import pandas as pd
import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection


# Function to get current time
def current_time():
    timezone = pytz.timezone("Africa/Nairobi")  # Setting timezone to East Africa
    return datetime.now(timezone)


# Cache the function to avoid reloading data on each action
@st.cache_data(ttl=300)
def fetch_data():
    # Establishing Google Sheets connection
    conn = st.connection("gsheets", type=GSheetsConnection)
    settings_list_data = conn.read(worksheet="Settings")
    existing_route_data = conn.read(worksheet="RoutePlanner")
    return settings_list_data, existing_route_data


@st.cache_data(persist=True)
def build_hierarchical_data(df):
    # Build the hierarchical structure
    cached_data = {}

    for _, row in df.iterrows():
        agent_name = row["Names"]
        region = row["Regions"]
        institution = row["Institutions"]

        # Create nested dictionaries as needed
        if agent_name not in cached_data:
            cached_data[agent_name] = {}  # Start a new dictionary for the agent

        if region not in cached_data[agent_name]:
            cached_data[agent_name][region] = []  # Start a new list for the region

        # Add institution to the agent's region
        if institution not in cached_data[agent_name][region]:
            cached_data[agent_name][region].append(institution)

    # Sort the keys alphabetically for better organization
    for agent in cached_data:
        for region in cached_data[agent]:
            cached_data[agent][region] = sorted(
                cached_data[agent][region]
            )  # Sort institutions

    # Sort the outer keys (agents)
    cached_data = {k: cached_data[k] for k in sorted(cached_data)}

    return cached_data


def new_route_planner():
    settings_list_data, existing_route_data = fetch_data()

    # Define static options
    TERRITORIES = settings_list_data["Territories"].unique().tolist()
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
    WEEKS = [1, 2, 3, 4, 5]
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
    cached_data = build_hierarchical_data(settings_list_data)

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
    week = st.selectbox(label="Week*", options=WEEKS, index=None, key="routeweeknumber")
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
        options=cached_data[selected_name].keys(),
        placeholder="select a region",
        key="routeregionselectedregion",
    )
    selected_institutions = st.multiselect(
        label="Select Institutions / Stores",
        options=cached_data[selected_name][selected_region],
        placeholder="select institutions",
        key="routeinstitutionsselectedinstitutions",
    )

    message_placeholder = st.empty()  # Empty container for success or error messages

    # Submit Button with Progress Indicator
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
            # Show progress bar for feedback on submission
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
                            "TimeStamp": submission_time.strftime("%d-%m-%Y  %H:%M:%S"),
                        }
                    ]
                )

                # Append data directly to avoid rerender
                conn = st.connection("gsheets", type=GSheetsConnection)
                existing_route_data = pd.concat(
                    [existing_route_data, route_data], ignore_index=True
                )
                conn.update(worksheet="RoutePlanner", data=existing_route_data)

            # Display success and reset placeholders
            message_placeholder.success(
                "Route Plan details successfully submitted!", icon=":material/thumb_up:"
            )
            clear_fields()  # Call the function to reset fields


# Clear fields function
def clear_fields():
    st.session_state["Selectrouteterritory"] = ""
    st.session_state["routemonthdropdown"] = ""
    st.session_state["routeweeknumber"] = ""
    st.session_state["routedayofweek"] = ""
    st.session_state["routedateinput"] = None  # For date inputs, set to None
    st.session_state["routenameselectedname"] = ""
    st.session_state["routeregionselectedregion"] = ""
    st.session_state["routeinstitutionsselectedinstitutions"] = (
        []
    )  # For multiselect, set to empty list
