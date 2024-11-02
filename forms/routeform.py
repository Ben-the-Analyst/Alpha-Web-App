import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import pytz


def load_form_data():
    time.sleep(2)


# Function to get current time
def current_time():
    timezone = pytz.timezone("Africa/Nairobi")  # Setting timezone to East Africa
    return datetime.now(timezone)


def route_planner():
    # Route Planner Form
    with st.spinner("Loading your form ..."):
        load_form_data()
    st.write("All the fields are mandatory")

    # Establishing a Google Sheets connection
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Fetch existing RoutePlanner data
    existing_route_data = conn.read(worksheet="RoutePlanner")
    settings_list_data = conn.read(worksheet="Settings")

    # List of data imports from sheets
    TERRITORIES1 = settings_list_data["Territories"].unique().tolist()
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

    # AGENTNAMES = settings_list_data["Names"].unique().tolist()
    # REGIONS = settings_list_data["Regions"].unique().tolist()
    # INSTITUTIONS = settings_list_data["Institutions"].unique().tolist()

    AGENTNAMES = sorted(settings_list_data["Names"].unique().tolist())
    REGIONS = sorted(settings_list_data["Regions"].unique().tolist())
    INSTITUTIONS = sorted(settings_list_data["Institutions"].unique().tolist())

    # Now AGENTNAMES, REGIONS, and INSTITUTIONS are sorted alphabetically.

    # Onboarding New Route Plan Form
    with st.form(key="route_planner", clear_on_submit=True):
        territories = st.selectbox("Territory*", options=TERRITORIES1, index=None)
        month = st.selectbox("Month*", options=MONTHS, index=None)
        week = st.selectbox("Week*", options=WEEKS, index=None)
        day = st.selectbox("Day*", options=DAYS, index=None)
        date = st.date_input(label="Route Plan Date", format="DD/MM/YYYY")
        agentname = st.selectbox("Your Name*", options=AGENTNAMES, index=None)
        region = st.selectbox("Region*", options=REGIONS, index=None)
        institutions = st.multiselect("Institutions / Stores", options=INSTITUTIONS)

        # Mark mandatory fields
        st.markdown("**required*")

        submit_button = st.form_submit_button(
            label="Submit Route Plan",
            help="Submit Route Plan",
            type="primary",
            icon=":material/send_money:",
            use_container_width=True,
        )

        # If the submit button is pressed
        if submit_button:
            # Check if all mandatory fields are filled
            if (
                not territories
                or not month
                or not week
                or not day
                or not date
                or not agentname
                or not region
                or not institutions
            ):
                st.warning(
                    icon=":material/error:",
                    body="Ensure all mandatory fields are filled.",
                )
                st.stop()
            else:
                # Show spinner while processing
                with st.spinner("Submitting your details..."):
                    # Simulate processing time
                    load_form_data()
                # Get the current time at submission
                submission_time = current_time()
                # Create a new row of Route Plan data
                route_data = pd.DataFrame(
                    [
                        {
                            "Territory": territories,
                            "Month": month,
                            "Week": week,
                            "Day": day,
                            "Date": date.strftime("%d-%m-%Y"),
                            "Agent": agentname,
                            "Region": region,
                            "Institutions": ", ".join(institutions),
                            "TimeStamp": submission_time.strftime("%d-%m-%Y  %H:%M:%S"),
                        }
                    ]
                )

                # Add the new Route Plan data to the existing data
                updated_route_df = pd.concat(
                    [existing_route_data, route_data], ignore_index=True
                )

                # Update Google Sheets with the new Route Plan data
                conn.update(worksheet="RoutePlanner", data=updated_route_df)

                st.success(
                    icon=":material/thumb_up:",
                    body="Route Plan details successfully submitted!",
                )
