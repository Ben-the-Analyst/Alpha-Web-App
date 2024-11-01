import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time


# Cache the function to avoid reloading data on each action
@st.cache_data(ttl=300)
def fetch_data():
    # Establishing Google Sheets connection
    conn = st.connection("gsheets", type=GSheetsConnection)
    settings_list_data = conn.read(worksheet="Settings")
    existing_route_data = conn.read(worksheet="RoutePlanner")
    return settings_list_data, existing_route_data


def current_time():
    return datetime.now().time()


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
    # AGENTNAMES = sorted(settings_list_data["Names"].unique().tolist())
    # Build and cache the hierarchical data
    cached_data = build_hierarchical_data(settings_list_data)

    # Form Inputs
    territories = st.selectbox(
        "The Territory*", options=TERRITORIES, key="route_territory_selectbox2"
    )
    month = st.selectbox("Month*", options=MONTHS, key="route_month_selectbox")
    week = st.selectbox("Week*", options=WEEKS, key="route_week_selectbox")
    day = st.selectbox("Day*", options=DAYS, key="route_day_selectbox")
    date = st.date_input(label="Route Plan Date")
    selected_name = st.selectbox("Select Name", options=cached_data.keys())
    selected_region = st.selectbox(
        "Select Region", options=cached_data[selected_name].keys()
    )
    selected_institutions = st.multiselect(
        "Select Institutions / Stores",
        options=cached_data[selected_name][selected_region],
    )

    # Submission and Progress Elements
    progress_placeholder = st.empty()  # Empty container for progress display
    message_placeholder = st.empty()  # Empty container for success or error messages

    # Submit Button with Progress Indicator
    if st.button("Submit Route Plan"):
        if not (
            territories
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
                progress_bar = st.progress(0)
                for i in range(1, 101):
                    time.sleep(0.01)
                    progress_bar.progress(i)

                # Collecting and submitting data
                submission_time = current_time()
                route_data = pd.DataFrame(
                    [
                        {
                            "Territory": territories,
                            "Month": month,
                            "Week": week,
                            "Day": day,
                            "Date": date.strftime("%d-%m-%Y"),
                            "Agent": selected_name,
                            "Region": selected_region,
                            "Institutions": ", ".join(selected_institutions),
                            "Time": submission_time.strftime("%H:%M:%S"),
                        }
                    ]
                )

                # Append data directly to avoid rerender
                conn = st.connection("gsheets", type=GSheetsConnection)
                existing_route_data = pd.concat(
                    [existing_route_data, route_data], ignore_index=True
                )
                conn.update(worksheet="RoutePlanner", data=existing_route_data)

                # # Update DataFrame with  for dynamic append
                # updated_data_placeholder = st.empty()
                # data_display = updated_data_placeholder.dataframe(existing_route_data)
                # # data_display(route_data)

            # Display success and reset placeholders
            message_placeholder.success("Route Plan details successfully submitted!")
            progress_placeholder.empty()  # Clear progress bar


new_route_planner()
