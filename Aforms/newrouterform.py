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


def route_planner():
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
    AGENTNAMES = sorted(settings_list_data["Names"].unique().tolist())

    # Form Inputs
    territories = st.selectbox(
        "Territory*", options=TERRITORIES, key="route_territory_selectbox"
    )
    month = st.selectbox("Month*", options=MONTHS, key="route_month_selectbox")
    week = st.selectbox("Week*", options=WEEKS, key="route_week_selectbox")
    day = st.selectbox("Day*", options=DAYS, key="route_day_selectbox")
    date = st.date_input(label="Route Plan Date")
    selected_name = st.selectbox(
        "Your Name*", options=AGENTNAMES, key="route_name_selectbox"
    )

    # Filter Regions and Institutions dynamically
    filtered_regions = (
        settings_list_data[settings_list_data["Names"] == selected_name]["Regions"]
        .unique()
        .tolist()
    )
    selected_region = st.selectbox(
        "Region*", options=filtered_regions, key="route_region_selectbox"
    )
    filtered_institutions = (
        settings_list_data[
            (settings_list_data["Names"] == selected_name)
            & (settings_list_data["Regions"] == selected_region)
        ]["Institutions"]
        .unique()
        .tolist()
    )
    selected_institutions = st.multiselect(
        "Institutions / Stores",
        options=filtered_institutions,
        key="route_institutions_multiselect",
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

                # Update DataFrame with .add_rows() for dynamic append
                updated_data_placeholder = st.empty()
                data_display = updated_data_placeholder.dataframe(existing_route_data)
                data_display.add_rows(route_data)

            # Display success and reset placeholders
            message_placeholder.success("Route Plan details successfully submitted!")
            progress_placeholder.empty()  # Clear progress bar


route_planner()
